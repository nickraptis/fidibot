# Author: Nick Raptis <airscorp@gmail.com>
"""
Module for auto updating the fidibot

When an update command occurs, the bot will exit
with exit code 42. It is then a shell scripts job
to update it and bring it back online.
"""

from basemodule import BaseModule, BaseCommandContext
from alternatives import _


class UpdateContext(BaseCommandContext):

    def cmd_update_private(self, argument):
        """Exit, pending an update"""
        self.bot.disconnect(_("Going for an update"))
        raise SystemExit(42)

    # hide command from help
    cmd_update_private.hidden = True


    def do_public(self):
        """Make the update triggered by pushes to github"""
        if 'github' in self.nick.lower():
            if 'pushed' in self.input and 'fidibot' in self.input:
                # execute delayed so it has time to respond to bot messages
                self.connection.execute_delayed(5, self.cmd_update_private, ("",))
        # Let the message propagate further regardless
        return False



class UpdateModule(BaseModule):
    context_class = UpdateContext

module = UpdateModule
