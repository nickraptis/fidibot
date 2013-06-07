# Author: Giannakopoulos John <giannakopoulosj@gmail.com>
"""Module for fail quotes"""

from basemodule import BaseModule, BaseCommandContext

from alternatives import _

alternatives_dict = {
     'FAIL mofa': [
         'Den se grafo oute aristera oute dexia SE GRAFO STO KENTRO POUXO XORO',
         'tris pente eikosipente kai 10 sarantadio dose kai ena loukoumaki ston kirio',
     ]
}


class FailContext(BaseCommandContext):
    
    def cmd_fail(self, argument):
        """Give a random FAIL quote :-)"""
        self.send(self.target, _("FAIL mofa"))


class FailModule(BaseModule):
    context_class = FailContext


module = FailModule
