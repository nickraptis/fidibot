from basemodule import BaseModule, BaseCommandContext

class BasicCommandsContext(BaseCommandContext):
    def cmd_echo(self, argument):
        target = self.channel if self.channel.startswith("#") else self.nick
        self.send(target, "%s", argument)
    
    def cmd_say_public(self, argument):
        self.send(self.channel, "%s", argument)
        
    def cmd_say_private(self, argument):
        for channel in self.bot.channels:
            self.send(channel, "%s", argument) 

    def cmd_disconnect_private(self, argument):
        self.bot.disconnect()
    
    def cmd_die_private(self, argument):
        self.bot.die()
    
class BasicCommandsModule(BaseModule):
    context_class = BasicCommandsContext

module = BasicCommandsModule
    