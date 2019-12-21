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


class action:
    def __init__(self, skill, tags, tool="N/A"):
        self.skill = skill
        self.tool = tool

        self.noncontest = True if "noncontest" in tags else False
        self.zerolof = True if "zerolof" in tags else False
        self.attack = True if "attack" in tags else False
        self.commsattack = True if "commsattack" in tags else False
        self.dodge = True if "dodge" in tags else False
        self.reset = True if "reset" in tags else False


# returns true if two actions can contest each other
def contested(action1, action2):
    if(action1.noncontest or action2.noncontest):
        return False
    elif((action1.attack or action1.commsattack) and (action2.attack or action2.commsattack)):
        return True
    elif((action1.attack and action2.dodge) or (action1.dodge) and (action2.attack)):
        return True
    elif((action1.commsattack and action2.reset) or (action1.reset and action2.commsattack)):
        return True