# Author: 
"""
"""

from basemodule import BaseModule, BaseCommandContext
from alternatives import _

alternatives_dict = {
}


class TemplateContext(BaseCommandContext):
    
    def cmd_example(self, argument):
        """
        """
        self.send(self.target, _("%s"), argument)


class TemplateModule(BaseModule):
    context_class = TemplateContext

module = TemplateModule
