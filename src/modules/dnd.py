# Author: John Giannakopoulos <giannakopoulosj@gmail.com>

import random        
from basemodule import BaseModule, BaseCommandContext

from alternatives import _

class dndContext(BaseCommandContext):

    def cmd_roll(self, argument):
        """
        Rolling D&D style
        
        Usage: roll attack|save modifiers difficulty
        """
        
        # Analyze Arguments
        argument = argument.split()
        try:
            roll_type = argument[0].lower()
            modifier = int(argument[1])
            difficulty = int(argument[2])
        except (IndexError, ValueError):
            error = _("DM: Read The Freaking PHB")
            self.send(self.target, error)
            return
        
        #Choose Between Attack or Save
        if "att" in roll_type:
            success = _("You Hit")
            fail = _("You Miss")
            crit_success = _("Critical Hit!")
            crit_fail = _("Critical Miss!")
        elif "sav" in roll_type:
            success = _("You Save")
            fail = _("You Fail")
            crit_success = _("Critical Save!")
            crit_fail = _("Critical Fail!")
        else:
            invalid = _("DM: You cannot %s")
            self.send(self.target, invalid, roll_type)
            return
        
        # ROLL
        roll = random.randint(1, 20)
        
        # Determine Critical
        if roll == 20:
            result = crit_success
        elif roll == 1:
            result = crit_fail
        # Determine Success
        elif (roll + modifier) >= difficulty:
            result = success
        else:
            result = fail
        
        # Send the result
        self.send(self.target, _("You roll %s. %s"), roll, result)


class dndModule(BaseModule):
        context_class = dndContext

module = dndModule
