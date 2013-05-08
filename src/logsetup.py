# Author: Nick Raptis <airscorp@gmail.com>

"""Module to hold logging functions"""

import logging
import re, sys
import irc.events

colors = """
        \x1f|        # Underline
        \x02|        # Bold
        \x12|        # Reverse
        \x0f|        # Normal
        \x16|        # Italic
        
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
            target = tokens[2]
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

def setup_logging():
    """Set up logger options"""
    # Setup root logger
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(levelname)-8s %(name)-10s  %(message)s"))
    logger.addHandler(handler)
    
    # Setup irc.client logger
    client_logger = logging.getLogger('irc.client')
    client_logger.setLevel(logging.DEBUG)
    client_logger.propagate = False
    # add filters
    client_logger.addFilter(LowLevelFilter())
    client_logger.addFilter(PingPongFilter())
    client_logger.addFilter(PrivMsgFilter())
    # add handler
    client_handler = logging.StreamHandler(sys.stdout)
    client_handler.setFormatter(ServerMsgFormatter("CLIENT   %(message)s"))
    client_logger.addHandler(client_handler)
