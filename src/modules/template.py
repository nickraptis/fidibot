# Author: Your Name here <your@email.com>
"""
Template file for making bot modules

You should make a docstring yourself here to decribe your bot.
The first line should be concise as it will be used by help.

Don't forget to name of your module in modules/__init__.py
Only the first part of the filename is needed,
ie. "template" for template.py
"""

from basemodule import BaseModule, BaseCommandContext
# if you want an advanced bot, import BaseContext and instead
# of making commands, override do_public() and do_private()

from alternatives import _

alternatives_dict = {
# Enter alternatives for your strings here like such

#     'Welcome %s': [
#         'Welcome %s',
#         'Hello %s',
#     ]
}


class TemplateContext(BaseCommandContext):
    # No docstring needed here
    # Read modules/basemodule for documentation
    # and modules/basiccmds.py for an example
    
    def cmd_example(self, argument):
        """
        An example command. Just name it cmd_<command name>.
        
        Add a docstring like this one for help to use it
        
        You can instead end your command in _public or _private
        so it only works for channel or private messages
        """
        # Send something back
        # You should always use a formatted string so the bot can log easily
        # and you can use alternatives by wrapping your format string in _()
        self.send(self.target, _("%s"), argument)


# Now subclass Base Module and change it's context_class to your own
class TemplateModule(BaseModule):
    context_class = TemplateContext

# Set module to your Module subclass. Congrats!
module = TemplateModule
