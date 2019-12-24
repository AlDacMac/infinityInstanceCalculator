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
        u1mod = self.getbsmods(1)
        u2mod = self.getbsmods(2)

    def getbsmods(self, whichone):
        if whichone == 1:
            uattributes = self.u1attributes
            opattributes = self.u2attributes
            u = self.u1
            op = self.u2
        else:
            uattributes = self.u2attributes
            opattributes = self.u1attributes
            u = self.u2
            op = self.u1
        umod = 0
        # Visiblity mods are determined using an if/elif as only the higher will ever apply
        if ("nolof" in uattributes
                and ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(uattributes))):
            umod -= 6
        elif (("ecsmoke" in uattributes) #ecsmoke in u1attributes means that u is being affected by an eclipse smoke zone
                and ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(uattributes))):
            umod -= 6
        elif (("smoke" in uattributes)
                and ({"Multispectral Visor L2", "Multispectral Visor L3"}.isdisjoint(u.obligs))
                and ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(uattributes))):
            umod -= 6
        elif (("whitenoise" in uattributes)
                and not({"Multispectral Visor L1", "Multispectral Visor L2",
                         "Multispectral Visor L3"}.isdisjoint(u.obligs))
                and ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(uattributes))):
            umod -= 6
        elif (("poorvis" in uattributes)
                and ({"Multispectral Visor L2", "Multispectral Visor L3"}.isdisjoint(u.obligs))):
            if ("Multispectral Visor L1" in u.obligs):
                umod -= 3
            else:
                umod -= 6
        elif (("lowvis" in uattributes)
                and ({"Multispectral Visor L1", "Multispectral Visor L2", "Multispectral Visor L3"}.isdisjoint(u.obligs))):
            umod -= 3
        # There are different versions of surprise attack and shot for different marker states as future proofing for
        #   multiple attackers on each side
        if ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(u.obligs)):
            if not("Multispectral Visor L3" in u.obligs):
                if("surprise shot l2:camo" in opattributes):
                    umod -= 6
                elif("surprise shot l1:camo" in opattributes):
                    umod -= 3
                elif("surprise attack:camo" in opattributes and not("nbw: a" in uattributes)):
                    umod -= 6
            if ({"Biometric Visor L1", "Biometric Visor L2"}.isdisjoint(u.obligs)):
                if ("surprise shot l2:imp/echo" in opattributes):
                    umod -= 6
                elif ("surprise shot l1:imp/echo" in opattributes):
                    umod -= 3
                elif ("surprise attack:imp/echo" in opattributes and not("nbw: a" in uattributes)):
                    umod -= 6
            if ("surprise shot l2:decoy" in opattributes):
                umod -= 6
            elif ("surprise shot l1:decoy" in opattributes):
                umod -= 3
            elif ("surprise attack:decoy" in opattributes and not ("nbw: a" in uattributes)):
                umod -= 6
        if({"Multispectral Visor L1", "Multispectral Visor L2"}.isdisjoint(u.obligs)):
            if ("Multispectral Visor L1" in u.obligs):
                if("tocamo" in opattributes or "ODD: Optical Disruptor" in op.obligs):
                    umod -= 3
            else:
                if ("tocamo" in opattributes or "ODD: Optical Disruptor" in op.obligs):
                    umod -= 6
                if ("CH: Mimetism" in op.obligs or "camo" in opattributes):
                    umod -= 3
        if("full auto l2" in opattributes):
            umod -= 3
        if("cover" in opattributes and {"marksmanship l2", "marksmanship lx"}.isdisjoint(uattributes)):
            umod -= 3
        if(not("nbw: a" in uattributes)):
            if("ma 1" in opattributes or "ma 3" in opattributes):
                umod -= 3
            elif("ma 5" in opattributes):
                umod -= 6
            if not({"protheion l2", "protheion l5"}.isdisjoint(opattributes)):
                umod -= 3
            if not({"guard l1", "guard l2", "guard l3"}.isdisjoint(opattributes)):
                umod -= 3
            if ("ikhol l1" in opattributes):
                umod -= 3
            elif("ikhol l2" in opattributes):
                umod -= 6
            elif("ikhol l3" in opattributes):
                umod -= 9
        # Range is stored as a tuple as shown ("range", value from range) - e.g ("range", -3)
        # Other is just used as a way for users to do extra fine tuning
        for att in uattributes:
            if type(att) == tuple:
                if att[0] == "range" or att[0] == "other":
                    umod += att[1]
        if("fireteam 5" in uattributes):
            umod += 3
        if("TinBot E (Spotter)" in u.obligs):
            umod += 3
        if("marksmanship lx" in uattributes):
            umod += 6
        return max(-12, min(12, umod))


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





