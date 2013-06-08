# Author: Nick Raptis <airscorp@gmail.com>
"""
Module for listing commands and help.
"""

from basemodule import BaseModule, BaseCommandContext


class HelpContext(BaseCommandContext):

    def cmd_list(self, argument):
        """List commands"""
        arg = argument.lower()
        all_cmds = {'public': [], 'private': []}
        for module in self.bot.modules:
            pub_priv = module.list_commands()
            all_cmds['public'] += pub_priv['public']
            all_cmds['private'] += pub_priv['private']
        public = "public commands  -- %s" % " ".join(all_cmds['public'])
        private = "private commands -- %s" % " ".join(all_cmds['private'])
        if 'all' in arg or 'both' in arg:
            output = "\n".join((public, private))
        elif 'pub' in arg or self.target.startswith('#'):
            output = public
        elif 'priv' in arg or not self.target.startswith('#'):
            output = private
        else:
            # we shouldn't be here
            self.logger.error()
            return
        self.send(self.target, output)


class HelpModule(BaseModule):
    context_class = HelpContext

module = HelpModule
