# Author: Nick Raptis <airscorp@gmail.com>
"""
Module to ignore certain users

Just a simple list based ignore.
Place this module early in the active chain.
If the user matches, the message will stop right there.
"""

from basemodule import BaseModule, BaseContext


ignore_list = ('fossbot', 'fossbot_')
ignore_startswith ='!@'

class IgnoreContext(BaseContext):

    def do_public(self):
        if self.input[0] in ignore_startswith:
            return True
        return self._do()

    def do_private(self):
        return self._do()

    def _do(self):
        if self.nick in ignore_list:
            return True
        else:
            return False


class IgnoreModule(BaseModule):
    context_class = IgnoreContext

module = IgnoreModule
