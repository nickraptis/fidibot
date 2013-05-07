# Author: Nick Raptis <airscorp@gmail.com>

import logging


class BaseContext(object):
    
    def __init__(self, connection, event, module):
        self.connection = connection
        self.event = event
        self.module = module
        self.bot = module.bot
        self.nick = event.source.nick
        self.channel = event.target
        self.input = event.arguments[0]
    
    def send(self, target, msgformat, args):
        output = msgformat % args
        self.module.logger.debug("Sending to %s: %s", target, output)
        self.connection.privmsg(target, output)

    def do_public(self):
        return False
    
    def do_private(self):
        return False


class BaseCommandContext(BaseContext):
    
    def __init__(self, connection, event, module):
        super(BaseCommandContext, self).__init__(connection, event, module)

    def do_public(self):
        tokens = self.input.split(" ", 2)
        if not "fidi" in tokens[0].lower():
            return False
        try:
            command = tokens[1].lower()
        except IndexError:
            return False
        if not command:
            return False
        try:
            argument = tokens[2]
        except IndexError:
            argument = ''
        f = getattr(self, "cmd_"+command+"_public", 
                getattr(self, "cmd_"+command, None))
        if f:
            self.module.logger.debug(
                "%s sent public command %s with argument %s",
                self.nick, command, argument)
            f(argument)
            return True
        return False
    
    def do_private(self):
        tokens = self.input.split(" ", 1)
        command = tokens[0].lower()
        if not command:
            return False
        try:
            argument = tokens[1]
        except IndexError:
            argument = ''
        f = getattr(self, "cmd_"+command+"_private", 
                getattr(self, "cmd_"+command, None))
        if f:
            self.module.logger.debug(
                "%s sent private command %s with argument %s",
                self.nick, command, argument)
            f(argument)
            return True
        return False


class BaseModule(object):
    
    context_class = BaseContext
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__module__)
        self.init()
        
    def init(self):
        pass

    def on_pubmsg(self, connection, event):
        context = self.context_class(connection, event, self)
        return context.do_public()
    
    def on_privmsg(self, connection, event):
        context = self.context_class(connection, event, self)
        return context.do_private()
    
    def send(self, context, target, msgformat, args):
        self.logger.debug(msgformat, *args)
        context.send(target, msgformat, args)
