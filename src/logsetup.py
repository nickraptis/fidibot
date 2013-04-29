# Author: Nick Raptis <airscorp@gmail.com>

"""Module to hold logging functions"""

import logging
import sys
import irc.events

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
            command = tokens[1]
            try:
                message = tokens[3]
                if message[0] == ':':
                    message = message[1:]
            except IndexError:
                message = ''
            # if the command is numeric map it to a string
            if command in irc.events.numeric:
                command = irc.events.numeric[command].upper()
            # set up new format
            record.args = (command, message)
            record.msg = "%s  %s"
        if "TO SERVER" in msg:
            record.msg = "-->  %s"
        return super(ServerMsgFormatter, self).format(record)

def setup_logging():
    """Set up logger options"""
    # Setup irc.client logger
    client_logger = logging.getLogger('irc.client')
    client_logger.setLevel(logging.DEBUG)
    # add filters
    client_logger.addFilter(LowLevelFilter())
    client_logger.addFilter(PingPongFilter())
    client_logger.addFilter(PrivMsgFilter())
    # add handler
    client_handler = logging.StreamHandler(sys.stdout)
    client_handler.setFormatter(ServerMsgFormatter())
    client_logger.addHandler(client_handler)
