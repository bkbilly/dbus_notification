"""https://specifications.freedesktop.org/notification-spec/notification-spec-latest.html"""

import time
import logging
import threading
import traceback
from jeepney import DBusAddress, new_method_call, MessageType, MatchRule, HeaderFields
from jeepney.io.blocking import open_dbus_connection

logger = logging.getLogger("dbus_notification")
logging.basicConfig(level=logging.WARNING)


class DBusNotification():
    """Uses DBus to send notifications"""

    def __init__(self, appname="dbus_notification", callback=None):
        self.appname = appname
        self.callback = callback
        # Connect to the session bus
        self.conn = open_dbus_connection()
        
        # Notification service address
        self.notifications = DBusAddress(
            "/org/freedesktop/Notifications",
            bus_name="org.freedesktop.Notifications",
            interface="org.freedesktop.Notifications"
        )
        # History is already being used to keep a list of sent notifications
        self.history = {}
        if self.callback is not None:
            mythread = threading.Thread(
                target=self.callback_button,
                daemon=True,
            )
            mythread.start()

    def send(self,
            title="",
            message="",
            logo="",
            image=None,
            sound=None,
            actions=[],
            urgency=None,
            timeout=-1,
            notifyid=0,
            uniqueid=None):

        hints = {}
        if urgency is not None:
            hints["urgency"] = ("i", urgency)
        if image not in ["", None]:
            hints["image-path"] = ("s", image)
        if sound not in ["", None]:
            if "/" in sound:
                hints["sound-file"] = ("s", sound)
            else:
                hints["sound-name"] = ("s", sound)
        
        # Ensure actions are formatted as key-value pairs (Action ID, Localized Label)
        if len(actions) > 0:
            # The actions array requires pairs of strings: [action_id_1, label_1, action_id_2, label_2, ...]
            actions = [f"{self.appname}_{s}" if i % 2 == 0 else s for s in actions for i in (0, 1)]
        
        # Finds the notification ID for the uniqueid if provided, otherwise uses 0 for new notification
        if uniqueid is not None and uniqueid != "":
            notifyid = next((k for k, v in reversed(self.history.items()) if uniqueid in v["uniqueid"]), 0)
            logger.debug("Found notification ID %s for unique ID %s.", notifyid, uniqueid)

        # Send the notification
        msg = new_method_call(
            self.notifications,
            "Notify",
            "susssasa{sv}i",
            (
                self.appname,
                notifyid,
                logo,
                title,
                message,
                actions,
                hints,
                timeout
            )
        )
        notification_id = self.conn.send_and_get_reply(msg).body[0]
        logger.debug("Notification sent with ID: %s", notification_id)
        
        # Store or update the history with the confirmed ID
        self.history[notification_id] = {
            "id": notification_id,
            "title": title,
            "message": message,
            "logo": logo,
            "image": image,
            "sound": sound,
            "actions": actions,
            "urgency": urgency,
            "timeout": timeout,
            "uniqueid": uniqueid,
        }
        return notification_id

    def close(self, id_or_uniqueid):
        """Closes a specific notification using its ID."""
        if isinstance(id_or_uniqueid, int):
            notifyid = id_or_uniqueid
        elif isinstance(id_or_uniqueid, str):
            notifyid = next((k for k, v in reversed(self.history.items()) if id_or_uniqueid in v["uniqueid"]), None)
            if notifyid is None:
                logger.warning("Could not find a valid notification ID for: %s", id_or_uniqueid)
                return
        else:
            return

        if notifyid not in self.history:
            # Only log a warning if the ID isn't in our local history, but attempt to close it anyway.
            logger.warning("Notification ID %s not found in local history, but attempting to close via DBus.", notifyid)

        # Prepare the method call for CloseNotification(uint32 id)
        close_msg = new_method_call(
            self.notifications,
            "CloseNotification",
            "u",
            (notifyid,)
        )
        
        # Send the message. We don't need a reply.
        self.conn.send_message(close_msg)
        logger.debug("Close requested for Notification ID %s.", notifyid)
        
        # Remove from history only if it was there
        if notifyid in self.history:
            del self.history[notifyid]

    def close_all(self):
        """Closes all notifications tracked by this instance's history."""
        notification_ids = list(self.history.keys())
        for notifyid in notification_ids:
            self.close(notifyid)
        
    def callback_button(self):
        # Create match rule for ActionInvoked signals
        time.sleep(0.3)
        logger.debug("Start callback")
        rule = MatchRule(
            type="signal",
            interface="org.freedesktop.Notifications",
            member="ActionInvoked",
            path="/org/freedesktop/Notifications"
        )
        
        # Convert rule to string format needed for AddMatch
        rule_str = str(rule)

        # Add the match rule
        add_match_msg = new_method_call(
            DBusAddress("/org/freedesktop/DBus", "org.freedesktop.DBus"),
            "AddMatch",
            "s",
            (rule.serialise(),)
        )
        listen_conn = open_dbus_connection()
        listen_conn.send_and_get_reply(add_match_msg)
        
        logger.debug("Waiting for action clicks...")
        while True:
            try:
                msg = listen_conn.receive()
                if msg.header.message_type != MessageType.signal:
                    continue
                if msg.header.fields.get(HeaderFields.member) != "ActionInvoked":
                    continue
                if len(msg.body) != 2:
                    continue
                notification_id, action_key = msg.body
                if not isinstance(action_key, str):
                    continue
                if not action_key.startswith(self.appname):
                    continue
                notification = self.history.get(notification_id, {"id": notification_id})
                notification["button"] = action_key.removeprefix(f"{self.appname}_")
                self.callback("button", notification)
            except Exception as err:
                logger.warning(
                    "Error processing notification action: %s, %s",
                    err,
                    traceback.format_exc(),
                )
