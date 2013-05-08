# Author: Nick Raptis <airscorp@gmail.com>
"""
Module for Basic Commands to the fidibot

Apart for holding a base set of commands for the bot, this module also
serves as an example of how to build a module for fidibot.
"""
# As such, be sure to spend extra care while developing,
# so it is always clean and understandable ;)

from basemodule import BaseModule, BaseCommandContext


class BasicCommandsContext(BaseCommandContext):
    def cmd_echo(self, argument):
        """
        Echo back the argument, either to the channel or the user
        that sent us the command.
        """
        # determine if the source was a channel or a user
        target = self.channel if self.channel.startswith("#") else self.nick
        if argument:
            self.send(target, "%s", argument)
        else:
            self.send(target, "There's nothing to echo")
    
    def cmd_say_public(self, argument):
        """Say the argument back to the channel the command was called"""
        if argument:
            self.send(self.channel, "%s", argument)
        else:
            self.send(self.channel, "There's nothing to say")
        
    def cmd_say_private(self, argument):
        """Say the argument to the list of channels the bot is in"""
        if argument:
            for channel in self.bot.channels:
                self.send(channel, "%s", argument)
        else:
            self.send(self.nick, "There's nothing to say")

    def cmd_disconnect_private(self, argument):
        """Disconnect from server. Bot will try to reconnect"""
        self.bot.disconnect()
    
    def cmd_die_private(self, argument):
        """Disconnect and exit"""
        self.bot.die()
    
class BasicCommandsModule(BaseModule):
    context_class = BasicCommandsContext

module = BasicCommandsModule
    