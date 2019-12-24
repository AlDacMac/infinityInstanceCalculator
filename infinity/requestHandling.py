from infinity.dataParsing import *


# attributes tells you extra information about the unit, e.g that it's in cover or a low vis zone, it's using surprise
#   attack, or it is buffed with assisted fire - note that all optional skills are here if they are in use
class Request:
    def __init__(self, u1, u1action, u1attributes, u2, u2action, u2attributes):
        self.u1 = u1
        self.u1action = u1action
        self.u1attributes = u1attributes
        self.u2 = u2
        self.u2action = u2action
        self.u2attributes = u2attributes

    # returns true if the two actions contest each other
    def contested(self):
        if (self.u1action.noncontest or self.u2action.noncontest):
            return False
        elif (self.u1action.isattack() and self.u2action.isattack()):
            return True
        elif ((self.u1action.attack and self.u2action.dodge) or (self.u1action.dodge) and (self.u2action.attack)):
            return True
        elif ((self.u1action.comattack and self.u2action.reset) or (self.u1action.reset and self.u2action.comattack)):
            return True

    def handle(self):
        if (self.u1action.skill == "bsattack"):
            return self.handlebs()

    def handlebs(self):
        mods = 0
        if (("0vis" in self.u1attributes) and not("Multispectral Visor L2" or in "Sixth Sense L2")



# skill is the literal name from the rules, e.g "bsattack", "dodge"
# tags is a set of strings that contain information about the action, e.g a smoke grenade thrown
#   in such a way as to not block LoS would have the "noncontest" tag
#   - note: noncontested needs to be set by the action creator based on things like hacking program choice
# tool tells you what weapon/hacking program is being used to carry out the skill
class Action:
    def __init__(self, skill, tags, tool="N/A"):
        self.skill = skill
        self.tool = tool

        self.noncontest = True if "noncontest" in tags else False
        self.attack = True if "attack" in tags else False
        self.comattack = True if "commsattack" in tags else False
        self.dodge = True if "dodge" in tags else False
        self.reset = True if "reset" in tags else False

    # Tells you if the action is an attack or a comms attack
    def isattack(self):
        if self.comattack or self.attack:
            return True
        else:
            return False





