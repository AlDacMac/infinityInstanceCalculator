# attributes tells you extra information about the unit, e.g that it's in cover, it's using surprise
#   attack, or it is buffed with assisted fire
class request:
    def __init__(self, u1army, u1name, u1action, u1attributes, u2army, u2name, u2action, u2attributes):
        self.u1army = u1army
        self.u1tname = u1name
        self.u1action = u1action
        self.u1attributes = u1attributes
        self.u2army = u2army
        self.u2name = u2name
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


# skill is the literal name from the rules, e.g "bsattack", "dodge"
# tags is a set of strings that contain extra information about the action, e.g a smoke grenade thrown
#   in such a way as to not block LoS would have the "noncontest" tag
# tool tells you what weapon/hacking program is being used to carry out the skill
class action:
    def __init__(self, skill, tags, tool="N/A"):
        self.skill = skill
        self.tool = tool

        self.noncontest = True if "noncontest" in tags else False
        self.zerolof = True if "zerolof" in tags else False
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


