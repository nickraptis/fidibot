#! /usr/bin/env python
#
# Author: Nick Raptis <airscorp@gmail.com>

import argparse
import irc.bot
from irc.strings import lower
from logsetup import setup_logging, setup_client_logging
from introspect import build_index
from modules import activate_modules
from alternatives import alternatives, read_files, _

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
        self.nickname = self._nickname_wanted = nickname
        self.channel = channel
        self.realname = realname if realname else nickname
        self.password = password
        self.identified = False
        self.alternatives = alternatives
        # load modules
        active_modules, active_alternatives = activate_modules()
        self.modules = [m(self) for m in active_modules]
        self.alternatives.merge_with(active_alternatives)
        # add alternatives from directory
        self.alternatives.merge_with(read_files())
        self.alternatives.clean_duplicates()
        # build help index
        self.help_index = build_index(self.modules)
        super(FidiBot, self).__init__([(server, port)], nickname, realname)
        # set up rate limiting after 5 seconds to one message per second
        self.connection.execute_delayed(5,
            self.connection.set_rate_limit, (1,))
        # set up keepalive
        self._pings_pending = 0
        self._last_kicker = ''
        self.connection.execute_every(300, self._keepalive)

    def _keepalive(self):
        if self._pings_pending >= 2:
            log.warning("Connection timed out. Will try to reconnect!")
            self.disconnect()
            self._pings_pending = 0
            return
        try:
            self.connection.ping('keep-alive')
            self._pings_pending += 1
        except irc.client.ServerNotConnectedError:
            pass

    def on_pong(self, c, e):
        self._pings_pending = 0

    def on_kick(self, c, e):
        nick = e.arguments[0]
        channel = e.target
        if nick == c.get_nickname():
            self._last_kicker = e.source.nick
        c.execute_delayed(10, c.join, (channel,))

    def on_nicknameinuse(self, c, e):
        new_nick = self.nickname + "_"
        c.nick(new_nick)
        c.execute_delayed(10, self.changeback_nickname)
        self.nickname = new_nick

    def changeback_nickname(self):
        if self.nickname.endswith('_'):
            new_nick = self._nickname_wanted
            self.connection.nick(new_nick)
            self.nickname = new_nick

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
        
        # don't do default behaviour for the GitHub bots
        if 'github' in e.source.nick.lower():
            return
        # default behaviour if no module processes the message.
        if "fidi" in lower(e.arguments[0]):
            log.debug("Failed to understand public message '%s' from user %s",
                      e.arguments[0], e.source.nick)
            c.privmsg(e.target, _("Someone talking about me? Duh!"))

    def on_join(self, c, e):
        nick = e.source.nick
        # ignore the commings and goings of the GitHub bots
        if 'github' in nick.lower():
            return
        if not nick == c.get_nickname():
            c.privmsg(e.target, _("Welcome %s") % nick)
        elif self._last_kicker:
            c.privmsg(e.target, _("Why did you kick me, %s?") % self._last_kicker)
            self._last_kicker = ''

    def on_bannedfromchan(self, c, e):
        c.execute_delayed(10, c.join, (e.arguments[0],))


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
    setup_client_logging(bot)
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.disconnect(_("Someone closed me!"))
    except Exception as e:
        log.exception(e)
        bot.disconnect(_("I crashed damn it!"))
        raise SystemExit(4)

if __name__ == "__main__":
    main()
