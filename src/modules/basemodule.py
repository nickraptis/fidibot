# Author: Nick Raptis <airscorp@gmail.com>
"""
Base classes for fidibot modules.

Terminology
-----------
A Module class acts as a dispatcher and state keeper for the module.
It is basically a factory for Context objects.
Add in it whatever you wish to keep between events.

A Context on the other hand is the actual workhorse of the module.
It is stateless and a new instance is made for each event.

For specifics, look at each of the classes documentation.

Making a new module
-------------------
- Subclass one of the base Context classes.
  BaseCommandContext is handy for command based operations.
  
- Subclass BaseModule.
  Most of the time all you need to do is override its
  `context_class` attribute to point to your Context subclass.
  
- Set a file level attribute named `module` that points to
  your Module subclass.

For an example, look at the `basiccmds` module.
"""

import logging
from time import sleep
from logsetup import escape as esc
from introspect import list_commands


class BaseContext(object):
    """
    Base class to process IRC events.
    
    Reference attributes:
    ---------------------
    connection: The connection that originated the event.
    event:      The event that spawned this instance.
    module:     The module to which we belong.
    bot:        The bot we are a part of.
    logger:     The module's logger
    
    Convenience attributes:
    -----------------------
    nick:    Nickname of the user that originated the event.
    channel: Channel name that the event was originated in, if any.
    input:   The full string received for the event.
    target:  The user's nick for privates, or the channel for publics.
    
    Usage:
    ------
    Subclass and override any `do_<event_type>` methods you wish.
    """
    
    def __init__(self, connection, event, module):
        self.connection = connection
        self.event = event
        self.module = module
        self.bot = module.bot
        self.logger = self.module.logger
        self.nick = event.source.nick
        self.channel = event.target
        self.target = self.channel if self.channel.startswith("#") else self.nick
        self.input = event.arguments[0]
    
    def send(self, target, msgformat, *args):
        """
        Send a formatted message to target.
        
        Read on BaseModule's .send() for more.
        """
        # defer the send to the module, passing the connection as a key_arg
        self.module.send(target, msgformat, *args, connection=self.connection)

    def do_public(self):
        """
        Process an event coming from a public channel.
        
        Return True to signal that you have processed the event.
        Return False to signal that you're not interested and the next module
        in line should try to process it.
        """
        return False
    
    def do_private(self):
        """
        Process an event coming from a private message.
        
        Return True to signal that you have processed the event.
        Return False to signal that you're not interested and the next module
        in line should try to process it.
        """
        return False


class BaseCommandContext(BaseContext):
    """
    Base class to process IRC events containing commands to the bot.
    
    Events that get handled is in the formats:
    `bot_name command [argument]` for channel messages,
    `command [argument]` for private ones.
    
    Read on BaseContext's .send() for how you should send back text.
    
    Usage:
    ------
    You shouldn't need to override any of the defined methods.
    Instead, define your own methods corresponding to the commands you
    wish to process. These methods should be prepended with `cmd_` and
    can have a suffix of `_public` or `_private` if they should once be
    called on public or private messages respectively.
    The rest of the text after the event has been parsed is passed to
    the function as an argument.
    
    See the `basiccmds` module for examples.
    """
    
    def do_public(self):
        """
        Dispatch a public event to a cmd__public or cmd_ method
        """
        # look at the forst word of the event
        # to determine if it is addressed to us.
        tokens = self.input.split(" ", 2)
        if not "fidi" in tokens[0].lower():
            return False
        # get the next word to be a command
        try:
            command = tokens[1].lower()
        except IndexError:
            return False
        if not command:
            return False
        # hold the remaining text as the argument, if any
        try:
            argument = tokens[2]
        except IndexError:
            argument = ''
        # try to find a method to dispatch to
        f = getattr(self, "cmd_"+command+"_public", 
                getattr(self, "cmd_"+command, None))
        if f:
            self.module.logger.debug(
                "%s sent public command %s with argument %s",
                self.nick, command, argument)
            f(argument)
            return True
        # if there isn't a corresponding method, signal the bot
        return False
    
    def do_private(self):
        """
        Dispatch a private event to a cmd__private or cmd_ method
        """
        # get first next word to be a command
        tokens = self.input.split(" ", 1)
        command = tokens[0].lower()
        if not command:
            return False
        # hold the remaining text as the argument, if any
        try:
            argument = tokens[1]
        except IndexError:
            argument = ''
        # try to find a method to dispatch to
        f = getattr(self, "cmd_"+command+"_private", 
                getattr(self, "cmd_"+command, None))
        if f:
            self.module.logger.debug(
                "%s sent private command %s with argument %s",
                self.nick, command, argument)
            f(argument)
            return True
        # if there isn't a corresponding method, signal the bot
        return False


class BaseModule(object):
    """
    Base class for Modules
    
    Class attributes:
    ---------------------
    context_class: The context class to use to process events.
    
    Reference attributes:
    ---------------------
    bot:    The bot we are a part of.
    logger: The logger we should be using.
    
    Usage:
    ------
    For simple usage, subclass and override the `context_class` attribute.
    If you need to init state, you can use the hook method `init`.
    Send text through the `send` method. Handy for messages that are not
    the result of an event, perhaps responding to a timer.
    """
    
    context_class = BaseContext
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__module__)
        self.init()
        
    def init(self):
        """
        Run additional initialization commands after __init__
        
        Override this instead of the actual __init__ method if you
        need to initialize state, or anything else.
        """
        pass

    def on_pubmsg(self, connection, event):
        """
        Spawn a new Context instance to handle the public event
        """
        context = self.context_class(connection, event, self)
        return context.do_public()
    
    def on_privmsg(self, connection, event):
        """
        Spawn a new Context instance to handle the public event
        """
        context = self.context_class(connection, event, self)
        return context.do_private()
    
    def list_commands(self, cmd_type=None):
        """
        List module commands.
        
        This is automatic for command contexts. If you use the base
        context, you should override and return something like
        {'public': [], 'private': []}
        yourself.
        """
        return list_commands(self)

    def send(self, target, msgformat, *args, **kargs):
        """
        Send a formatted message to target.
        
        A context should pass it's connection as a key_arg.

        This is the prefferred method to send text back to IRC,
        as any number of operations, like logging or multiline send,
        can be done before transparent to the caller.
        """
        connection = kargs.get('connection', self.bot.connection)
        output = msgformat % args
        self.logger.debug("Sending to %s: %s", target, esc(output))
        lines = output.split("\n")
        connection.privmsg(target, lines.pop(0))
        for line in lines:
            sleep(1)
            if not line:
                line = " "
            connection.privmsg(target, line)
