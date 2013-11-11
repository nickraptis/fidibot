# Author: Nick Raptis <airscorp@gmail.com>
"""
Module for Basic Commands to the fidibot

Apart for holding a base set of commands for the bot, this module also
serves as an example of how to build a module for fidibot.
"""
# As such, be sure to spend extra care while developing,
# so it is always clean and understandable ;)

from basemodule import BaseModule, BaseCommandContext
from alternatives import _


class BasicCommandsContext(BaseCommandContext):
    def cmd_echo(self, argument):
        """
        Echo back the argument, either to the channel or the user
        that sent us the command.
        """
        # determine if the source was a channel or a user
        if argument:
            self.send(self.target, "%s", argument)
        else:
            self.send(self.target, _("There's nothing to echo"))
    
    def cmd_say_public(self, argument):
        """Say the argument back to the channel the command was called"""
        if argument:
            self.send(self.channel, "%s", argument)
        else:
            self.send(self.channel, _("There's nothing to say"))
        
    def cmd_say_private(self, argument):
        """Say the argument to the list of channels the bot is in"""
        if argument:
            for channel in self.bot.channels:
                self.send(channel, "%s", argument)
        else:
            self.send(self.nick, _("There's nothing to say"))

    def cmd_disconnect_private(self, argument):
        """Disconnect from server. Bot will try to reconnect"""
        self.bot.disconnect(_("I'll be back!"))
    
    def cmd_die_private(self, argument):
        """Disconnect and exit"""
        self.bot.die(_("Goodbye cruel world!"))

    def cmd_crash_private(self, argument):
        """Crash the bot for testing purposes"""
        raise IndexError()

    def cmd_error_private(self, argument):
        """Print the last lines of the error log"""
        if argument.isdigit():
            n = min(int(argument), 50)
        else:
            n = 5
        with open("log/errors.log") as f:
            lines = f.readlines()
        err = "".join(lines[-n:]).rstrip()
        if err:
            self.send(self.target, "%s", err)

    # hide commands from help
    cmd_disconnect_private.hidden = True
    cmd_die_private.hidden = True
    cmd_crash_private.hidden = True
    cmd_error_private.hidden = True


class BasicCommandsModule(BaseModule):
    context_class = BasicCommandsContext


module = BasicCommandsModule
