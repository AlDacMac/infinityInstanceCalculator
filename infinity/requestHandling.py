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
        if(self.u1action == "bsattack"):
            u1mod = self.getbsmods(1)
        if(self.u2action == "bsattack"):
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
        elif (("Eclipse Smoke" in uattributes) #ecsmoke in u1attributes means that u is being affected by an eclipse smoke zone
                and ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(uattributes))):
            umod -= 6
        elif (("Smoke" in uattributes)
                and ({"Multispectral Visor L2", "Multispectral Visor L3"}.isdisjoint(u.obligs))
                and ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(uattributes))):
            umod -= 6
        elif (("White Noise" in uattributes)
                and not({"Multispectral Visor L1", "Multispectral Visor L2",
                         "Multispectral Visor L3"}.isdisjoint(u.obligs))
                and ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(uattributes))):
            umod -= 6
        elif (("Poor Visibility" in uattributes)
                and ({"Multispectral Visor L2", "Multispectral Visor L3"}.isdisjoint(u.obligs))):
            if ("Multispectral Visor L1" in u.obligs):
                umod -= 3
            else:
                umod -= 6
        elif (("Low Visibility" in uattributes)
                and ({"Multispectral Visor L1", "Multispectral Visor L2", "Multispectral Visor L3"}.isdisjoint(u.obligs))):
            umod -= 3
        # There are different versions of surprise attack and shot for different marker states as future proofing for
        #   multiple attackers on each side
        if ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(u.obligs)):
            if not("Multispectral Visor L3" in u.obligs):
                if("Surprise Shot L2:Camo" in opattributes):
                    umod -= 6
                elif("Surprise Shot L1:camo" in opattributes):
                    umod -= 3
                elif("Surprise Attack:camo" in opattributes and not("Natural Born Warrior: A" in uattributes)):
                    umod -= 6
            if ({"Biometric Visor L1", "Biometric Visor L2"}.isdisjoint(u.obligs)):
                if ("Surprise Shot L2:imp/echo" in opattributes):
                    umod -= 6
                elif ("Surprise Shot L1:imp/echo" in opattributes):
                    umod -= 3
                elif ("Surprise Attack:imp/echo" in opattributes and not("Natural Born Warrior: A" in uattributes)):
                    umod -= 6
            if ("Surprise Shot L2:decoy" in opattributes):
                umod -= 6
            elif ("Surprise Shot L1:decoy" in opattributes):
                umod -= 3
            elif ("Surprise Attack:decoy" in opattributes and not ("Natural Born Warrior: A" in uattributes)):
                umod -= 6
        if({"Multispectral Visor L1", "Multispectral Visor L2"}.isdisjoint(u.obligs)):
            if ("Multispectral Visor L1" in u.obligs):
                if("CH: Total Camouflage" in opattributes or "ODD: Optical Disruptor" in op.obligs):
                    umod -= 3
            else:
                if ("CH: Total Camouflage" in opattributes or "ODD: Optical Disruptor" in op.obligs):
                    umod -= 6
                if ("CH: Mimetism" in op.obligs or "CH: Camouflage" in opattributes):
                    umod -= 3
        if("Full Auto L2" in opattributes):
            umod -= 3
        if("cover" in opattributes and {"Marksmanship L2", "Marksmanship LX"}.isdisjoint(uattributes)):
            umod -= 3
        if(not("Natural Born Warrior: A" in uattributes)):
            if("Martial Arts L1" in opattributes or "Martial Arts L3" in opattributes):
                umod -= 3
            elif("Martial Arts L5" in opattributes):
                umod -= 6
            if not({"Protheion L2", "Protheion L5"}.isdisjoint(opattributes)):
                umod -= 3
            if not({"Guard L1", "Guard L2", "Guard L3"}.isdisjoint(opattributes)):
                umod -= 3
            if("I-Khol L1" in opattributes):
                umod -= 3
            elif("I-Khol L2" in opattributes):
                umod -= 6
            elif("I-Khol L3" in opattributes):
                umod -= 9
            if("Natural Born Warrior: B" in opattributes):
                umod -= 3
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
        if("Marksmanship LX" in uattributes):
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

        if ("noncontest" in tags): self.noncontest = True
        else: self.noncontest = False
        if "attack" in tags: self.attack = True
        else: self.attack = False
        if "commsattack" in tags: self.comattack = True
        else: self.commattack = False
        if "dodge" in tags: self.dodge = True
        else: self.dodge = False
        if "reset" in tags: self.reset = True
        else: self.reset =  False

    # Tells you if the action is an attack or a comms attack
    def isattack(self):
        if self.comattack or self.attack:
            return True
        else:
            return False


class Unit:
    def __init__(self, armyname, name, child):
        self.armyname = armyname.lower()[0:4]
        self.name = name
        self.child = child

        # Unit skills and equipment are divided into those that are obligatory and those that are optional
        self.obligs: set = set({})
        self.options: set = set({})
        populateUnitSpec(self.armyname, self.name, self.obligs, self.options)

    def getStat(self, stat):
        return getUnitStat(self.armyname, self.name, stat)


class SaveOutcome:
    def __init__(self):
        self.wounded = 0
        self.unconscious = 0
        self.immobilized = 0
        self.dead = 0
        self.isolated = 0
        self.posessed = 0
        self.stunned = 0
        self.burnt = 0
        self.sepsitorised = 0




