from infinity.dataParsing import *
from infinity.diceMaths import *
from math import *

armAmmo = {"N", "AP", "EXP", "Shock", "DA", "Fire", "K1", "Monofilament", "Plasma", "T2"}

btsAmmo = {"Breaker", "DT", "E/M", "E/M2", "Flash", "Nanotech", "Plasma", "Stun", "Viral", "Jammer", "Sepsitor",
           "Phermonic"}

phAmmo = {"ADH"}

armWoundAmmo = {"N", "AP", "EXP", "Shock", "DA", "Fire", "K1", "Plasma", "T2"}

btsWoundAmmo = {"Breaker", "DT", "Nanotech", "Viral", "Plasma", "Phermonic"}

btsEffectOnCrit = {"Breaker", "DT", "E/M", "E/M2", "Flash", "Nanotech", "Stun", "Viral", "Jammer", "Sepsitor",
                   "Phermonic"}

armEffectOnCrit = {"N", "AP", "EXP", "Shock", "DA", "Fire", "K1", "Monofilament", "Plasma", "T2"}

phEffectOnCrit = {"ADH"}

# attributes tells you extra information about the unit, e.g that it's in cover or a low vis zone, it's using surprise
#   attack, or it is buffed with assisted fire - note that all optional skills are here if they are in use

# Imagine a request as describing a general 'state of play' - units are in positions, stuff like smoke is down on the
#   board, ranges have been found. The request is like the minute you start rolling the dice to see what hapens.
# TODO consider if enforcing that the first three elements of attributes be Range, Burst Mod, and other is a good idea
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
        elif (self.u1action.isGenericAttack() and self.u2action.isGenericAttack()):
            return True
        elif ((self.u1action.attack and self.u2action.dodge) or (self.u1action.dodge) and (self.u2action.attack)):
            return True
        elif ((self.u1action.comattack and self.u2action.reset) or (self.u1action.reset and self.u2action.comattack)):
            return True

    def handle(self):
        u1attr = self.u1action.getAttr()
        u1stat = self.u1.getstat(u1attr)
        if (self.u1action.skill == "BS Attack"):
            u1stat += getBSMods(self.u1, self.u1attributes, self.u2, self.u2attributes)
        u1burst = getBurst(self.u1action, self.u1, self.u1attributes, self.u2, self.u2attributes)

        u2attr = self.u2action.getAttr()
        u2stat = self.u2.getstat(u2attr)
        if (self.u2action.skill == "BS Attack"):
            u2stat += getBSMods(self.u2, self.u2attributes, self.u1, self.u1attributes)
        u2burst = getBurst(self.u2action, self.u2, self.u2attributes, self.u1, self.u1attributes)

        u1avg = ContestedRollHitAvg(u1burst, u1stat, u2burst, u2stat)
        print(u1avg)


def getAmmo(u, uaction, uattributes, op, opattributes):


def getBurst(uaction, u, uattributes, op, opattributes):
    if (uattributes[1] is not None):
        return uattributes[1]
    else:
        burst = uaction.getActionBurst()
        if(uaction.skill in {"BS Attack", "Suppressive Fire", "Triangulated Fire", "Direct Template Wepaon"}):
            if not ({"fireteam 5", "fireteam 4", "fireteam 3"}.isdisjoint(uattributes)):
                burst += 1
            if ("Full Auto L1" in uattributes):
                burst += 1
            if ("Twin Weapons" in uattributes):
                burst += 1
            if ("Saturation Zone" in uattributes):
                burst -= 1
        elif(uaction.skill == "CC Attack"):
            # Martial Arts L5 will just be implemented using burst override, as it needs to ignore usage of other stuff
            if ("Martial Arts L4" in uattributes):
                burst += 1
            if (uattributes[3] is not None):
                burst += uattributes[3]
            elif (uattributes[4] is not None):
                burst += uattributes[4]
        return burst


def getBSMods(u, uattributes, op, opattributes):
    umod = 0
    # Visiblity mods are determined using an if/elif as only the higher will ever apply
    if ("nolof" in uattributes
            and ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(uattributes))):
        umod -= 6
    elif ((
                  "Eclipse Smoke" in uattributes)  # ecsmoke in u1attributes means that u1 is being affected by an eclipse smoke zone
          and ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(uattributes))):
        umod -= 6
    elif (("Smoke" in uattributes)
          and ({"Multispectral Visor L2", "Multispectral Visor L3"}.isdisjoint(u.obligs))
          and ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(uattributes))):
        umod -= 6
    elif (("White Noise" in uattributes)
          and not ({"Multispectral Visor L1", "Multispectral Visor L2",
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
          and (
          {"Multispectral Visor L1", "Multispectral Visor L2", "Multispectral Visor L3"}.isdisjoint(u.obligs))):
        umod -= 3
    # There are different versions of surprise attack and shot for different marker states as future proofing for
    #   multiple attackers on each side
    if ({"Sixth Sense L1", "Sixth Sense L2"}.isdisjoint(u.obligs)):
        if not ("Multispectral Visor L3" in u.obligs):
            if ("Surprise Shot L2:Camo" in opattributes):
                umod -= 6
            elif ("Surprise Shot L1:camo" in opattributes):
                umod -= 3
            elif ("Surprise Attack:camo" in opattributes and not ("Natural Born Warrior: A" in uattributes)):
                umod -= 6
        if ({"Biometric Visor L1", "Biometric Visor L2"}.isdisjoint(u.obligs)):
            if ("Surprise Shot L2:imp/echo" in opattributes):
                umod -= 6
            elif ("Surprise Shot L1:imp/echo" in opattributes):
                umod -= 3
            elif ("Surprise Attack:imp/echo" in opattributes and not ("Natural Born Warrior: A" in uattributes)):
                umod -= 6
        if ("Surprise Shot L2:decoy" in opattributes):
            umod -= 6
        elif ("Surprise Shot L1:decoy" in opattributes):
            umod -= 3
        elif ("Surprise Attack:decoy" in opattributes and not ("Natural Born Warrior: A" in uattributes)):
            umod -= 6
    if ({"Multispectral Visor L1", "Multispectral Visor L2"}.isdisjoint(u.obligs)):
        if ("Multispectral Visor L1" in u.obligs):
            if ("CH: Total Camouflage" in opattributes or "ODD: Optical Disruptor" in op.obligs):
                umod -= 3
        else:
            if ("CH: Total Camouflage" in opattributes or "ODD: Optical Disruptor" in op.obligs):
                umod -= 6
            if ("CH: Mimetism" in op.obligs or "CH: Camouflage" in opattributes):
                umod -= 3
    if ("Full Auto L2" in opattributes):
        umod -= 3
    if ("cover" in opattributes and {"Marksmanship L2", "Marksmanship LX"}.isdisjoint(uattributes)):
        umod -= 3
    if (not ("Natural Born Warrior: A" in uattributes)):
        if ("Martial Arts L1" in opattributes or "Martial Arts L3" in opattributes):
            umod -= 3
        elif ("Martial Arts L5" in opattributes):
            umod -= 6
        if not ({"Protheion L2", "Protheion L5"}.isdisjoint(opattributes)):
            umod -= 3
        if not ({"Guard L1", "Guard L2", "Guard L3"}.isdisjoint(opattributes)):
            umod -= 3
        if ("I-Khol L1" in opattributes):
            umod -= 3
        elif ("I-Khol L2" in opattributes):
            umod -= 6
        elif ("I-Khol L3" in opattributes):
            umod -= 9
        if ("Natural Born Warrior: B" in opattributes):
            umod -= 3
    # Range is stored as a tuple as shown ("range", value from range) - e.g ("range", -3)
    # Other is just used as a way for users to do extra fine tuning
    for att in uattributes:
        if type(att) == tuple:
            if att[0] == "range" or att[0] == "other":
                umod += att[1]
    if ("fireteam 5" in uattributes):
        umod += 3
    if ("TinBot E (Spotter)" in u.obligs):
        umod += 3
    if ("Marksmanship LX" in uattributes):
        umod += 6
    return max(-12, min(12, umod))


# tags is a set of strings that contain information about the action, e.g a smoke grenade thrown
#   in such a way as to not block LoS would have the "noncontest" tag
#   - note: noncontested needs to be set by the action creator based on things like hacking program choice
# tool tells you what weapon/hacking program is being used to carry out the skill
class Action:
    def __init__(self, skill, tags, tool="N/A", tool2="N/A"):
        self.skill = skill
        self.tool = tool
        self.tool2 = tool2

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
    def isGenericAttack(self):
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
        self.immobilized2 = 0
        self.immobilized1 = 0
        self.dead = 0
        self.isolated = 0
        self.posessed = 0
        self.stunned = 0
        self.burnt = 0
        self.sepsitorised = 0
        self.targeted = 0


# TODO Implement immunity, especially the ability to choose attribute
# TODO Make seperate saver for hacking attacks (hacking programs don't use normal effects of the ammo)
# hits is a tuple, the first element is crits and the second is regular hits
# I assume exp, da, and fire don't stack
def makeSaves(unit, hits, ammotypes, modifiers, damage):
    outcome = SaveOutcome()
    failedarmsaves = 0
    failedbtssaves = 0
    failedphsaves = 0
    arm = int(unit.getStat('arm'))
    bts = int(unit.getStat('bts'))
    ph = int(unit.getStat('ph'))
    if("Monofilament" in ammotypes or "K1" in ammotypes):
        arm = 0
    elif("AP" in ammotypes):
        arm = ceil(arm / 2.0)
    if("Breaker" in ammotypes or "E/M" in ammotypes or "E/M2" in ammotypes):
        bts = ceil(bts/2.0)
    if("ADH" in ammotypes):
        ph = max(0, ph - 6)
    if("Cover" in modifiers):
        arm += 3
        bts += 3
    armfailchance = min(1, max(0, (damage - arm) / 20.0))
    btsfailchance = min(1, max(0, (damage - bts) / 20.0))
    phfailchance = min(1, max(0, (damage - ph) / 20.0))

    # Failed saves from crits
    if not(armEffectOnCrit.isdisjoint(ammotypes)):
        failedarmsaves += hits[0]
    if not(btsEffectOnCrit.isdisjoint(ammotypes)):
        failedbtssaves += hits[0]
    # I assume regular bts saves from plasma only occur on crit if there's nothing causing normal bts crits
    elif("Plasma" in ammotypes):
        failedbtssaves += hits[0] * btsfailchance
    if not(phEffectOnCrit.isdisjoint(ammotypes)):
        failedphsaves += hits[0]

    # Regular arm saves
    if("EXP" in ammotypes):
        failedarmsaves += (hits[1] * 3 * armfailchance) + (hits[0] * 2 * armfailchance)
    elif("DA" in ammotypes):
        failedarmsaves += (hits[1] * 2 * armfailchance) + (hits[0] * armfailchance)
    elif("Fire" in ammotypes):
        failedarmsaves += recurringFireAvg(armfailchance, (hits[0] + hits[1]))
    elif not(armAmmo.isdisjoint(ammotypes)):
        failedarmsaves += armfailchance * hits[1]

    # Regular bts saves
    if not({"DT", "EM/2", "Stun", "Viral"}.isdisjoint(ammotypes)):
        failedbtssaves += (hits[1] * 2 * btsfailchance) + (hits[0] * btsfailchance)
    elif not(btsAmmo.isdisjoint(ammotypes)):
        failedbtssaves += hits[1] * btsfailchance

    # Regular ph saves
    if not(phAmmo.isdisjoint(ammotypes)):
        failedphsaves += phfailchance * hits[1]

    if ("Phermonic" in ammotypes):
        outcome.targeted += hits[1] + hits[0]
    armFailEffects(unit, failedarmsaves, ammotypes, outcome)
    btsFailEffects(unit, failedbtssaves, ammotypes, outcome)
    phFailEffects(unit, failedphsaves, ammotypes, outcome)
    return outcome


def armFailEffects(unit, failures, ammotypes, outcome):
    if not(armWoundAmmo.isdisjoint(ammotypes)):
        outcome.wounded += failures
        if ("T2" in ammotypes):
            outcome.wounded += failures
        if ("Fire" in ammotypes):
            outcome.burnt += failures
    if ("Monofilament" in ammotypes):
        outcome.dead += failures


def btsFailEffects(unit, failures, ammotypes, outcome):
    if not(btsWoundAmmo.isdisjoint(ammotypes)):
        outcome.wounded += failures
    if ("E/M" in ammotypes or "E/M2" in ammotypes):
        outcome.isolated += failures
        if (unit.getStat("Type") == "HI" or unit.getStat("Type") == "TAG" or unit.getStat("Type") == "REM"):
            outcome.immobilized2 += failures
    if ("Flash" in ammotypes or "Stun" in ammotypes):
        outcome.stunned += failures
    if ("Sepsitor" in ammotypes):
        outcome.sepsitorised += failures
    if ("Jammer" in ammotypes):
        outcome.isolated += failures


def phFailEffects(unit, failures, ammotypes, outcome):
    if ("ADH" in ammotypes):
        outcome.immobilized2 += failures


def recurringFireAvg(failchance, nosaves):
    failedsaves = 0
    for i in range(20):
        failed = failchance * nosaves
        nosaves = failed
        failedsaves += failed
    return failedsaves

