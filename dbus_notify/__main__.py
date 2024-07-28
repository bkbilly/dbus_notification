import json
import argparse
from . import DBusNotification


def main():
    parser = argparse.ArgumentParser(
        prog="dbus-notification",
        description="Sends a notification")
    parser.add_argument("-t", "--title", default="", help="Title of notification")
    parser.add_argument("-m", "--message", default="", help="Subtitle of notification")
    parser.add_argument("-l", "--logo", default="", help="Adds a small image")
    parser.add_argument("-i", "--image", default=None, help="Adds a big image")
    parser.add_argument("-s", "--sound", default=None, help="Plays a sound either from a file or a system sound like message-new-instant")
    parser.add_argument("-u", "--urgency", default=None, choices=[None, 1, 2, 3], help="Sets the urgency, it's a number between 1, 2, 3")
    parser.add_argument("-c", "--timeout", default=-1, type=int, help="When to automatically close the notification")
    args = parser.parse_args()

    DBusNotification().send(
        args.title, args.message,
        logo=args.logo,
        image=args.image,
        sound=args.sound,
        urgency=args.urgency,
        timeout=args.timeout,
    )
