# Author: Nick Raptis <airscorp@gmail.com>
"""
Module for listing commands and help.
"""

from basemodule import BaseModule, BaseCommandContext

from alternatives import _

class HelpContext(BaseCommandContext):

    def cmd_list(self, argument):
        """List commands"""
        arg = argument.lower()
        index = self.bot.help_index
        public = "public commands  -- %s" % " ".join(index['public'])
        private = "private commands -- %s" % " ".join(index['private'])
        if 'all' in arg or 'both' in arg:
            output = "\n".join((public, private))
        elif 'pub' in arg or self.target.startswith('#'):
            output = public
        elif 'priv' in arg or not self.target.startswith('#'):
            output = private
        else:
            # we shouldn't be here
            self.logger.error("cmd_list")
            return
        self.send(self.target, output)

    def cmd_modules(self, argument):
        """List active modules"""
        index = self.bot.help_index
        output = "active modules   -- %s" % " ".join(index['modules'].keys())
        self.send(self.target, output)

    def cmd_help(self, argument):
        """Get help on a command or module"""
        arg = argument.lower()
        index = self.bot.help_index
        target = self.target
        args = arg.split()
        if not args:
            s = "usage: help <command> [public|private] / help module <module>"
            self.send(target, s)
        elif args[0] == 'module':
            args.pop(0)
            if not args:
                self.send(target, "usage: help module <module>")
            else:
                help_item = index['modules'].get(args[0])
                if help_item:
                    self.send(target, help_item['summary'])
                else:
                    self.send(target, _("No help for %s"), args[0])
        else:
            args.append("")
            cmd = args.pop(0)
            cmd_type = args.pop(0)
            if 'pu' in cmd_type or self.target.startswith('#'):
                cmd_type = 'public'
            elif 'pr' in cmd_type or not self.target.startswith('#'):
                cmd_type = 'private'
            else:
                # we shouldn't be here
                self.logger.error("cmd_list")
                return
            help_item = index[cmd_type].get(cmd)
            if help_item:
                self.send(target, index[cmd_type][cmd]['summary'])
            else:
                self.send(target, _("No help for %s"), cmd)


class HelpModule(BaseModule):
    context_class = HelpContext

module = HelpModule
