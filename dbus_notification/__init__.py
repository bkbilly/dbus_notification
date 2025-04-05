"""https://specifications.freedesktop.org/notification-spec/notification-spec-latest.html"""

import time
import logging
import threading
from jeepney import DBusAddress, new_method_call, MessageType, MatchRule, HeaderFields
from jeepney.io.blocking import open_dbus_connection

logger = logging.getLogger("dbus_notification")
logging.basicConfig(level=logging.ERROR)


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
            notifyid=0):

        hints = {}
        if urgency is not None:
            hints["urgency"] = ("i", urgency)
        if image not in ["", None]:
            hints["image-path"] = ("s", image)
        if sound not in ["", None]:
            if  "/" in sound:
                hints["sound-file"] = ("s", sound)
            else:
                hints["sound-name"] = ("s", sound)
        
        if len(actions) > 0:
            actions = [f"{self.appname}_{s}" if i % 2 == 0 else s for s in actions for i in (0, 1)]
        
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
        print(f"Notification sent with ID: {notification_id}")
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
        }

    def callback_button(self):
        # Create match rule for ActionInvoked signals
        time.sleep(0.3)
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
        self.conn.send_and_get_reply(add_match_msg)
        
        print("Waiting for action clicks... (Press Ctrl+C to exit)")
        while True:
            try:
                msg = self.conn.receive()
                if msg.header.fields.get(HeaderFields.destination) and len(msg.body) == 2:
                    notification_id, action_key = msg.body
                    if isinstance(action_key, str) and action_key.startswith(self.appname):
                        notification = self.history.get(notification_id, {"id": notification_id})
                        notification["button"] = action_key.removeprefix(f"{self.appname}_")
                        self.callback("button", notification)

            except:
                continue
