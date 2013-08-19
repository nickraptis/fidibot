import random        
from basemodule import BaseModule, BaseCommandContext

class dndContext(BaseCommandContext):

    def cmd_roll(self, argument):
        """ Rolling D&D style """
        #target = channel

        #Analyze and Format Command
        argument = argument.split()
        argument[0] = argument[0].lower()
        resault = "DM: Read The Freaking PHB"

        #Check Valid Command Input
        if not (len(argument)==3):
            self.send(self.channel, resault)
            return
        elif not argument[1].isdigit():
            self.send(self.channel, resault)
            return
        elif not argument[2].isdigit():
            self.send(self.channel, resault)
            return
        else:
            pass
            
        #Choose Between Attack or Save
        if argument[0] == "attack":
            #ROLL FOR ATTACK
            roll = random.randint(1, 20)
            #Attack and AC to Integers
            att = int(argument[1])
            ac = int(argument[2])
            if (roll+att)>=ac:
                resault = "You Hit"
            else:
                resault = "You Miss"
        elif argument[0] == "save":
            #ROLL FOR SAVE
            roll = random.randint(1, 20)
            #Save and DC to Integers
            save = int(argument[1])
            dc = int(argument[2])
            if (roll+save)>=dc:
                resault = "You Save"
            else:
                resault = "You Fail"
        else:
            resault = "DM: Read The Freaking PHB"
            self.send(self.channel, resault)
            return
        
        if roll==20 or roll==1:
            if roll == 1:
                critical = "Critical Fail"
            elif roll == 20:
                critical = "Critical Success"
            self.send(self.channel, ("%s %s %s"), resault, critical, roll)
        else:
            self.send(self.channel, ("%s %s"), resault, roll)
        
class dndModule(BaseModule):
        context_class = dndContext

module = dndModule
