"""Tests for DBusNotification behavior that do not require a DBus session."""
import sys
import types
import unittest


class DBusAddress:
    """Minimal DBusAddress stub."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Message:
    """Minimal DBus message stub."""

    def __init__(self, body):
        self.body = body


class Header:
    """Minimal DBus message header stub."""

    def __init__(self, message_type, member):
        self.message_type = message_type
        self.fields = {HeaderFields.member: member}


class SignalMessage:
    """Minimal DBus signal message stub."""

    def __init__(self, member, body):
        self.header = Header(MessageType.signal, member)
        self.body = body


def new_method_call(_address, _method, _signature, body):
    """Return a simple message object."""
    return Message(body)


class MessageType:
    """Minimal MessageType stub."""

    signal = "signal"


class MatchRule:
    """Minimal MatchRule stub."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def serialise(self):
        """Return a placeholder match rule."""
        return "match-rule"


class HeaderFields:
    """Minimal HeaderFields stub."""

    member = "member"


jeepney = types.ModuleType("jeepney")
jeepney.DBusAddress = DBusAddress
jeepney.new_method_call = new_method_call
jeepney.MessageType = MessageType
jeepney.MatchRule = MatchRule
jeepney.HeaderFields = HeaderFields
sys.modules["jeepney"] = jeepney

io_module = types.ModuleType("jeepney.io")
blocking_module = types.ModuleType("jeepney.io.blocking")
blocking_module.open_dbus_connection = lambda: None
sys.modules["jeepney.io"] = io_module
sys.modules["jeepney.io.blocking"] = blocking_module

from dbus_notification import DBusNotification  # pylint: disable=wrong-import-position


class Reply:
    """DBus reply stub."""

    def __init__(self, notification_id):
        self.body = [notification_id]


class FakeConn:
    """DBus connection stub."""

    def __init__(self):
        self.next_id = 1
        self.closed = []

    def send_and_get_reply(self, msg):
        """Return the requested replacement ID or a new notification ID."""
        requested_id = msg.body[1]
        if requested_id:
            return Reply(requested_id)
        notification_id = self.next_id
        self.next_id += 1
        return Reply(notification_id)

    def send_message(self, msg):
        """Record closed notification IDs."""
        self.closed.append(msg.body[0])


def make_notification():
    """Create a DBusNotification instance without opening a DBus connection."""
    notification = object.__new__(DBusNotification)
    notification.appname = "testapp"
    notification.callback = None
    notification.conn = FakeConn()
    notification.notifications = DBusAddress("/org/freedesktop/Notifications")
    notification.history = {}
    return notification


class DBusNotificationTest(unittest.TestCase):
    """Tests for DBusNotification."""

    def test_uniqueid_lookup_is_exact_and_handles_none_history(self):
        """Unique IDs are matched exactly and tolerate notifications without one."""
        notification = make_notification()

        plain_id = notification.send(message="plain")
        test_2_id = notification.send(message="test 2", uniqueid="test-2")
        test_id = notification.send(message="test", uniqueid="test")

        self.assertIsNone(notification.history[plain_id]["uniqueid"])
        self.assertEqual(notification._find_notification_id("test"), test_id)
        self.assertEqual(notification._find_notification_id("test-2"), test_2_id)
        self.assertIsNone(notification._find_notification_id(""))

    def test_send_replaces_exact_uniqueid(self):
        """Sending the same unique ID replaces the matching notification."""
        notification = make_notification()

        first_id = notification.send(message="test", uniqueid="test")
        second_id = notification.send(message="updated", uniqueid="test")

        self.assertEqual(second_id, first_id)
        self.assertEqual(notification.history[first_id]["message"], "updated")

    def test_close_without_id_closes_all_tracked_notifications(self):
        """Calling close without an ID closes all notifications from this instance."""
        notification = make_notification()
        first_id = notification.send(message="plain")
        second_id = notification.send(message="test", uniqueid="test")

        notification.close()

        self.assertEqual(notification.conn.closed, [first_id, second_id])
        self.assertEqual(notification.history, {})

    def test_button_callback_signal(self):
        """ActionInvoked signals emit button callbacks."""
        notification = make_notification()
        callbacks = []
        notification.callback = lambda *args: callbacks.append(args)
        notification.history[12] = {"id": 12, "title": "test"}

        notification._handle_callback_signal(
            SignalMessage("ActionInvoked", [12, "testapp_Acknowledge"])
        )

        self.assertEqual(callbacks, [("button", {
            "id": 12,
            "title": "test",
            "button": "Acknowledge",
        })])

    def test_closed_callback_signal(self):
        """NotificationClosed signals emit closed callbacks and remove history."""
        notification = make_notification()
        callbacks = []
        notification.callback = lambda *args: callbacks.append(args)
        notification.history[12] = {"id": 12, "title": "test"}

        notification._handle_callback_signal(
            SignalMessage("NotificationClosed", [12, 2])
        )

        self.assertEqual(callbacks, [("closed", {
            "id": 12,
            "title": "test",
            "reason": 2,
        })])
        self.assertEqual(notification.history, {})

    def test_close_empty_uniqueid_closes_all_tracked_notifications(self):
        """Calling close with an empty unique ID closes all notifications."""
        notification = make_notification()
        first_id = notification.send(message="plain")
        second_id = notification.send(message="test", uniqueid="test")

        notification.close("")

        self.assertEqual(notification.conn.closed, [first_id, second_id])
        self.assertEqual(notification.history, {})


if __name__ == "__main__":
    unittest.main()
