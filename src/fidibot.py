#! /usr/bin/env python
#
# Author: Nick Raptis <airscorp@gmail.com>

import argparse
import irc.bot
from irc.strings import lower
from logsetup import setup_logging
from modules import activate_modules
from alternatives import alternatives, _

import logging
log = logging.getLogger(__name__)

# set unicode decoding to replace errors
from irc.buffer import DecodingLineBuffer as DLB
DLB.errors = 'replace'


class FidiBot(irc.bot.SingleServerIRCBot):

    def __init__(self, channel, nickname, server, port=6667, realname=None, password=''):
        if channel[0] != "#":
            # make sure channel starts with a #
            channel = "#" + channel
        self.channel = channel
        self.realname = realname if realname else nickname
        self.password = password
        self.identified = False
        self.alternatives = alternatives
        # load modules
        active_modules, active_alternatives = activate_modules()
        self.modules = [m(self) for m in active_modules]
        self.alternatives.merge_with(active_alternatives)
        super(FidiBot, self).__init__([(server, port)], nickname, realname)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        
    def on_privnotice(self, c, e):
        if e.source.nick == "NickServ":
            if "NickServ identify" in e.arguments[0]:
                log.debug("NickServ asks us to identify")
                if self.password:
                    log.info("Sending password to NickServ")
                    c.privmsg("NickServ", "identify " + self.password)
                else:
                    log.warning("We were asked to identify but we have no password")
            elif "You are now identified" in e.arguments[0]:
                log.debug("We are now identified with NickServ")
                self.identified = True
            elif "Invalid password" in e.arguments[0]:
                log.error("Invalid password! Check your settings!")

    def on_privmsg(self, c, e):
        # first try to defer the message to the active modules
        for m in self.modules:
            if m.on_privmsg(c, e):
                return
        
        # default behaviour if no module processes the message.
        command = lower(e.arguments[0].split(" ", 1)[0])
        if "fidi" in command:
            # maybe someone is calling us by name?
            c.privmsg(e.source.nick, _("You don't have to call me by name in private"))
            return
        log.debug("Failed to understand private message '%s' from user %s",
                  e.arguments[0], e.source.nick)
        c.privmsg(e.source.nick, _("I don't understand %s") % command)

    def on_pubmsg(self, c, e):
        # first try to defer the message to the active modules
        for m in self.modules:
            if m.on_pubmsg(c, e):
                return
        
        # default behaviour if no module processes the message.
        if "fidi" in lower(e.arguments[0]):
            log.debug("Failed to understand public message '%s' from user %s",
                      e.arguments[0], e.source.nick)
            c.privmsg(e.target, _("Someone talking about me? Duh!"))

    def on_join(self, c, e):
        nick = e.source.nick
        if not nick == c.get_nickname():
            c.privmsg(e.target, _("Welcome %s") % nick)


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
    bot = FidiBot(args.channel, args.nickname, args.server, args.port,
                  realname= args.realname, password=args.password)
    bot.start()

if __name__ == "__main__":
    main()
