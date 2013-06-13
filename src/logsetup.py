# Author: Nick Raptis <airscorp@gmail.com>

"""Module to hold logging functions"""

import logging
import re, sys
import irc.events
from logging.handlers import TimedRotatingFileHandler as TRHandler

colors = """
        \x1f|        # Underline
        \x02|        # Bold
        \x12|        # Reverse
        \x0f|        # Normal
        \x16|        # Italic
        
        \x01|        # ACTION Heading
        
        \x03         # Color
        (?:\d{1,2}   # with one or two digits for foreground
        (?:,\d{1,2}  # and maybe a comma and another 2 digits
        )?)?         # for background
         """
strip_colors = re.compile(colors, re.UNICODE | re.VERBOSE)

class LowLevelFilter(logging.Filter):
    """A filter for irc.client low level events"""
    
    def filter(self, record):
        if "_dispatcher" in record.msg:
            return False
        if "command:" in record.msg:
            return False
        return True

class PingPongFilter(logging.Filter):
    """A filter for irc.client PING PONG events"""
    
    def filter(self, record):
        if "PING" in record.getMessage():
            return False
        if "PONG" in record.getMessage():
            return False
        return True

class PrivMsgFilter(logging.Filter):
    """A filter for irc.client PRIVMSG events
    
    We usually don't want to see these events
    as we are handling them elsewhere"""    
    
    def filter(self, record):
        if "PRIVMSG" in record.getMessage():
            return False
        return True

class ChannelLogFilter(logging.Filter):
    """Filter for logging in moobot format"""

    acc_types = ["KICK", "MODE", "JOIN", "NICK", "TOPIC", "PART", "QUIT"]

    def filter(self, record):
        msg = record.getMessage()
        arg = record.args[0]
        if "FROM SERVER" in msg or "TO SERVER" in msg:
            if "CHANMODES=" in arg or "CHANNELLEN=" in arg:
                return False
            for msg_type in self.acc_types:
                if msg_type in arg:
                    return True
            if "PRIVMSG" in arg and "#" in arg:
                return True
        return False

class ServerMsgFormatter(logging.Formatter):
    """Formatter that checks if the event is of 
    FROM/TO SERVER: type, and strips it to a leaner
    form"""
    
    def format(self, record):
        msg = record.getMessage()
        if "FROM SERVER" in msg:
            # extract command and message
            tokens = record.args[0].split(" ", 3)
            # [1:] gets rid of the first character which is a colon
            source = tokens[0][1:]
            # we are only interested in source if it has a nickname
            source = source.split("!")[0] if "!" in source else ""
            command = tokens[1]
            try:
                target = tokens[2]
            except IndexError:
                source = tokens[1][1:]
                command = tokens[0]
                target = ''
            try:
                message = tokens[3]
                while message[0] == ':':
                    message = message[1:]
            except IndexError:
                message = ''
            message = strip_colors.sub("", message)
            # if the command is numeric map it to a string
            if command in irc.events.numeric:
                command = irc.events.numeric[command].upper()
            # prune to 11 characters
            command = command[:11]
            # set up new format
            if command in ("JOIN", "PART", "QUIT"):
                record.args = (command, source, command.lower(), target, message)
                record.msg = "%-11s %s %sed channel %s %s"
            elif source:
                record.args = (command, source, message)
                record.msg = "%-11s %s: %s"
            else:
                record.args = (command, message)
                record.msg = "%-11s %s"
        if "TO SERVER" in msg:
            record.msg = "---->  %s"
        return super(ServerMsgFormatter, self).format(record)

class ChannelLogFormatter(logging.Formatter):
    """Formatter to moobot format"""

    def __init__(self, *args, **kargs):
        self.bot = kargs['bot']
        del(kargs['bot'])
        super(ChannelLogFormatter, self).__init__(*args, **kargs)

    def format(self, record):
        from_to = record.msg
        arg = record.args[0]
        arg = strip_colors.sub("", arg)
        if "TO SERVER" in from_to:
            arg = ":%s %s" % (self.bot.nickname, arg)
        if "ACTION" in arg:
            arg = arg.replace("PRIVMSG", "CTCP")
        if "PRIVMSG" in arg and "#" in arg:
            arg = arg.replace("PRIVMSG", "PUBMSG")
        
        if self.usesTime():
            asctime = self.formatTime(record, self.datefmt)
        
        return self._fmt % {'asctime': asctime, 'message': arg}

def escape(string):
    """Escapes newlines and tabs in a string"""
    string = string.replace('\n', '\\n')
    string = string.replace('\t', '\\t')
    return string


def setup_logging():
    """Set up logger options"""
    # Setup root logger
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(levelname)-8s %(name)-10s  %(message)s"))
    logger.addHandler(handler)

def setup_client_logging(bot):
    # Setup irc.client logger
    client_logger = logging.getLogger('irc.client')
    client_logger.setLevel(logging.DEBUG)
    client_logger.propagate = False
    # Setup channel logs
    channel_logger = logging.getLogger('irc.client')
    channel_handler = TRHandler("log/moolog/moobot.log", when='midnight')
    channel_handler.addFilter(LowLevelFilter())
    channel_handler.addFilter(ChannelLogFilter())
    channel_handler.setFormatter(ChannelLogFormatter(bot=bot,
        fmt="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    channel_logger.addHandler(channel_handler)
    # add main handler
    client_handler = logging.StreamHandler(sys.stdout)
    client_handler.addFilter(LowLevelFilter())
    client_handler.addFilter(PingPongFilter())
    client_handler.addFilter(PrivMsgFilter())
    client_handler.setFormatter(ServerMsgFormatter("CLIENT   %(message)s"))
    client_logger.addHandler(client_handler)
