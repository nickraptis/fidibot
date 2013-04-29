#! /usr/bin/env python
#
# Author: Nick Raptis <airscorp@gmail.com>

import argparse
import irc.bot
from irc.strings import lower
from logsetup import setup_logging

class FidiBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, realname=None, password=None):
        self.channel = channel
        self.realname = realname if realname else nickname
        self.password = password
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, realname)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        # split incoming string into "command message"
        command = lower(e.arguments[0].split(" ", 1)[0])
        try:
            msg = e.arguments[0].split(" ", 1)[1]
        except IndexError:
            msg = ""
        
        if command == "pes":
            if msg:
                c.privmsg(self.channel, msg)
            else:
                c.privmsg(e.source.nick, "Ti na pw?")
        else:
            c.privmsg(e.source.nick, "Ti thes na peis %s?" % command)

    def on_pubmsg(self, c, e):
        string = e.arguments[0]
        string_low = lower(e.arguments[0])
        if "fidi" in string_low:
            answer = " ".join([word for word in string.split() if "fidi" not in lower(word)])
            c.privmsg(e.target, answer)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('server', help="Server to connect to")
    parser.add_argument('channel', help="Channel to join. Prepending with # is optional")
    parser.add_argument('nickname', help="Nickname to use")
    parser.add_argument('-r', '--realname', help="Real name to use. Defaults to nickname")
    parser.add_argument('-x', '--password', help="Password to authenticate with NickServ")
    parser.add_argument('-p', '--port', default=6667, type=int, help="Connect to port")
    return parser.parse_args()


def main():
    args = get_args()
    setup_logging()
    bot = FidiBot(args.channel, args.nickname, args.server, args.port)
    bot.start()

if __name__ == "__main__":
    main()
