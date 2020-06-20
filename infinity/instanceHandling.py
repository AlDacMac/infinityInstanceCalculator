from infinity import dataParsing
from infinity import diceMaths
from math import *
from misc.misc import *

# proper capitalisation is used for real skills and equipment, camelCase is used for tags I've created

# ----------------------------------------------------------------------------------------------------------------------
# Tags used to denote categories of ammo
# ----------------------------------------------------------------------------------------------------------------------
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

# ----------------------------------------------------------------------------------------------------------------------
# Tags used to denote categories of action
# ----------------------------------------------------------------------------------------------------------------------
genericAttacks = {"BS Attack", "Intuitive Attack", "Speculative Fire", "Marksmanship LX", "Triangulated Fire",
                  "CC Attack", "Hacking"}

dodgeableAttacks = {"BS Attack", "Intuitive Attack", "Speculative Fire", "Marksmanship LX", "Triangulated Fire"}

smokeDodgeableAttacks = {"BS Attack", "Marksmanship LX", "Triangulated Fire"}

bsAttacks = {"BS Attack", "Intuitive Attack", "Speculative Fire", "Marksmanship LX"}

dodges = {"Dodge", "Change Facing", "Engage"}

commsAttacks = {"Hacking", "Jammer", "Sat-Lock"}

resets = {"Reset"}

nonContest = {"nonContest", "Beserk"}

# ----------------------------------------------------------------------------------------------------------------------
# Tags used to denote categories of skill/equipment
# ----------------------------------------------------------------------------------------------------------------------

ignoresSmoke = ("MSV 2", "MSV 3")

sixthSense = {"Sixth Sense L1", "Sixth Sense L2"}

# ----------------------------------------------------------------------------------------------------------------------


# TODO Implement cover by having a setting on the model performing the action stating if the TARGET has cover
# A list of units, what action they are performing, and what their target it.
class Instance:
    def __init__(self):
        # active and reactive are collections of orders, which themselves contain information about the unit performing
        #   the order, what tools they're using, modifiers, targets etc.
        self.active = dict({})
        self.reactive = dict({})
        # The trackers are used for creating unique IDs
        self.activeTracker = 0
        self.reactiveTracker = 0

    # TODO make the dictionaries work with burst splitting - a single unit Id should be able to target mutliple
    #   perhaps a make target a dict from unitId to the burst dedicated to that unit
    #   this also needs to work for template weapons, I reckon the same solution is viable
    #   I don't think I actually have to modify anything for this
    def addOrder(self, unitId, player, stats, action, losInfo=None, rangeInfo=None, coverInfo=None, modifiers=None, target=None, tool1=None, tool2=None):
        if modifiers is None:
            modifiers = set({})
        unitData = {
            "unitId": unitId,           # This is kept here so that we can tell if two units are targting each other from just the data dict
            "stats": stats,
            "action": action,
<<<<<<< HEAD
            "losInfo": losInfo,         # Dict from string (target IDs) to set (of conditions that apply to LOS, such as "noLOS", or "Eclipse")
            "rangeInfo": rangeInfo,     # Dict from string (target IDs) to int (range)
            "coverInfo": coverInfo,     # A set of the target Ids of units with partial cover agaisnt the firer
            "modifiers": modifiers,     # A set of skills and equipment, stored as strings
            "burstSplit": target,       # A dict from string (target IDs) to int (burst for that target)
=======
            "modifiers": modifiers,
            "target": target,
>>>>>>> parent of 7fa4b24... contested changed to a method of the Instance class, now called contestedBetween
            "tool1": tool1,
            "tool2": tool2
        }
        if player == 1:
            self.active[unitId] = unitData
        else:
            self.reactive[unitId] = unitData


# Contested takes two unitIds and their corresponding data dicts and determines if they contest each other.
# We assume that two actions either mutually contest or mutually don't, even if one action does not actualy require dice
#   i.e direct template weapon
# TODO Figure out if direct template weapons should be in nonContest
#   we do need to invoke special logic if the opponent is dodging, so they probably shouldn't - we can add the 1 hit
#   after hit calcs are made
#       hell we could just treat DTWs as always rolling 0
def contested(actingId, actingData, contestingId, contestingData):
    if overlaps(actingData["modifiers"], nonContest) or overlaps(contestingData["modifiers"], nonContest):
        return False
    elif actingData["action"] in genericAttacks and contestingData["action"] in genericAttacks:
        if actingId == contestingData["target"] and contestingId == actingData["target"]:
            return True
    elif actingData['action'] in dodgeableAttacks and contestingData['action'] in dodges:
        if actingData["target"] == contestingId:
            return True
    elif actingData['action'] in dodges and contestingData['action'] in dodgeableAttacks:
        if contestingData["target"] == actingId:
            return True
    elif actingData['action'] in commsAttacks and contestingData['action'] in resets:
        if actingData["target"] == contestingId:
            return True
    elif actingData['action'] in resets and contestingData['action'] in commsAttacks:
        if contestingData["target"] == actingId:
            return True
    # TODO take acount of smoke special dodge being able to block multiple attakcs, have a list that initially includes
    #   everyone but that people can be removed from
    elif actingData['action'] in smokeDodgeableAttacks and contestingData['action'] == "Smoke Dodge":
        # Smoke dodges will keep a list of all those who the smoke blocks in their targets field
        if actingData["target"] == contestingId and actingId in contestingData["target"]:
            if not overlaps(actingData["modifiers"], ignoresSmoke):
                return True
    elif actingData['action'] == "Smoke Dodge" and contestingData['action'] in smokeDodgeableAttacks:
        if contestingData["target"] == actingId and contestingId in actingData["target"]:
            if not overlaps(contestingData["modifiers"], ignoresSmoke):
                return True
<<<<<<< HEAD
        # TODO take acount of smoke special dodge being able to block multiple attakcs, have a list that initially
        #  includes everyone but that people can be removed from
        elif actingData['action'] in smokeDodgeableAttacks and reactingData['action'] == "Smoke Dodge":
            # Smoke dodges will keep a list of all those who the smoke blocks in their burstSplit field
            if reactingId in actingData["burstSplit"] and actingId in reactingData["burstSplit"]:
                if actingData["tool1"] == "Eclipse Smoke Grenade":
                    return True
                elif not overlaps(actingData["modifiers"], ignoresSmoke):
                    return True
        elif actingData['action'] == "Smoke Dodge" and reactingData['action'] in smokeDodgeableAttacks:
            if actingId in reactingData["burstSplit"] and reactingId in actingData["burstSplit"]:
                if not overlaps(reactingData["modifiers"], ignoresSmoke):
                    return True


# For the sake of consistency, the unit that the modifiers will apply to should always come first in the variables

# Calculates the net modifier that a model applies to an enemy by a bs attack against them.
#   This calcualtion is done seperately from bsModsRecieved as otherwise we could not handle someone not getting mods
#   from a model shooting, but not at them.
def bsModsInflicted(targetData, shooterData):
    targetModifiers = targetData["Modifiers"]
    shooterModifiers = shooterData["Modifiers"]
    totalMod = 0   
    if not overlaps({"Sixth Sense L1", "Sixth Sense L2"}, targetModifiers):
        if not ("Multispectral Visor L3" in targetModifiers):
            if ("Surprise Shot L2:Camo" in shooterModifiers):
                totalMod -= 6
            elif ("Surprise Shot L1:camo" in shooterModifiers):
                totalMod -= 3
            elif ("Surprise Attack:camo" in shooterModifiers and not ("Natural Born Warrior: A" in shooterModifiers)):
                totalMod -= 6
        if ({"Biometric Visor L1", "Biometric Visor L2"}.isdisjoint(targetModifiers)):
            if ("Surprise Shot L2:imp/echo" in shooterModifiers):
                totalMod -= 6
            elif ("Surprise Shot L1:imp/echo" in shooterModifiers):
                totalMod -= 3
            elif ("Surprise Attack:imp/echo" in shooterModifiers and not ("Natural Born Warrior: A" in shooterModifiers)):
                totalMod -= 6
        if ("Surprise Shot L2:decoy" in shooterModifiers):
            totalMod -= 6
        elif ("Surprise Shot L1:decoy" in shooterModifiers):
            totalMod -= 3
        elif ("Surprise Attack:decoy" in shooterModifiers and not ("Natural Born Warrior: A" in shooterModifiers)):
            totalMod -= 6
    if "Full Auto L2" in shooterModifiers:
        totalMod -= 3
    return totalMod

=======
>>>>>>> parent of 7fa4b24... contested changed to a method of the Instance class, now called contestedBetween

# TODO remember to do max/min when modsRecieved and modsInflicted are combined

# TODO consider making calculation of LOS mods its own thing
# TODO implement triangulated fire
def bsModsRecieved(shooterData, targetData):
    totalMod = 0
    targetModifiers = targetData["Modifiers"]
    shooterModifiers = shooterData["Modifiers"]
    # ------------------------------------------------------------------------------------------------------------------
    # Visibility mods, elifs are used as only the worst will apply
    # ------------------------------------------------------------------------------------------------------------------
    if "noLof" in shooterData["losInfo"][targetData["unitId"]] and sixthSenseApplies(shooterData, targetData):
        totalMod -= 6
    elif "eclipse" in (shooterData["losInfo"][targetData["unitId"]] and sixthSenseApplies(shooterData, targetData)):
        totalMod -= 6
    elif "Smoke" in shooterData["losInfo"][targetData["unitId"]] \
            and not overlaps(shooterModifiers, {"Multispectral Visor L2", "Multispectral Visor L3"}) \
            and sixthSenseApplies(shooterData, targetData):
        totalMod -= 6
    elif "White Noise" in shooterData["losInfo"][targetData["unitId"]] \
            and overlaps(shooterModifiers, {"Multispectral Visor L1", "Multispectral Visor L2", "Multispectral Visor L3"}) \
            and sixthSenseApplies(shooterData, targetData):
        totalMod -= 6
    elif "Poor Visibility" in shooterData["losInfo"][targetData["unitId"]] \
            and not overlaps(shooterModifiers, {"Multispectral Visor L2", "Multispectral Visor L3"}):
        if ("Multispectral Visor L1" in shooterModifiers):
            totalMod -= 3
        else:
            totalMod -= 6
    elif "Low Visibility" in shooterData["losInfo"][targetData["unitId"]] \
            and not overlaps(shooterModifiers, {"Multispectral Visor L1", "Multispectral Visor L2", "Multispectral Visor L3"}):
        totalMod -= 3
    # ------------------------------------------------------------------------------------------------------------------
    # Camouflage mods
    # ------------------------------------------------------------------------------------------------------------------
    if not overlaps(targetModifiers, {"Multispectral Visor L2", "Multispectral Visor L3"}):
        if "Multispectral Visor L1" in shooterModifiers:
            if ("CH: Total Camouflage" in targetModifiers or "ODD: Optical Disruptor" in targetModifiers):
                totalMod -= 3
        else:
            if ("CH: Total Camouflage" in targetModifiers or "ODD: Optical Disruptor" in targetModifiers):
                totalMod -= 6
            if ("CH: Mimetism" in targetModifiers or "CH: Camouflage" in targetModifiers):
                totalMod -= 3
    # ------------------------------------------------------------------------------------------------------------------
    # CC Mods
    # ------------------------------------------------------------------------------------------------------------------
    if (not ("Natural Born Warrior: A" in shooterModifiers)):   # TODO you might not actually be able to use NBW here
        if ("Martial Arts L1" in targetModifiers or "Martial Arts L3" in targetModifiers):
            totalMod -= 3
        elif ("Martial Arts L5" in targetModifiers):
            totalMod -= 6
        if not ({"Protheion L2", "Protheion L5"}.isdisjoint(targetModifiers)):
            totalMod -= 3
        if not ({"Guard L1", "Guard L2", "Guard L3"}.isdisjoint(targetModifiers)):
            totalMod -= 3
        if ("I-Khol L1" in targetModifiers):
            totalMod -= 3
        elif ("I-Khol L2" in targetModifiers):
            totalMod -= 6
        elif ("I-Khol L3" in targetModifiers):
            totalMod -= 9
        if ("Natural Born Warrior: B" in targetModifiers):
            totalMod -= 3
    # ------------------------------------------------------------------------------------------------------------------
    # Other mods
    # ------------------------------------------------------------------------------------------------------------------
    if ("Full Auto L2" in targetModifiers):
        totalMod -= 3
    if "cover" in targetModifiers and not overlaps(shooterModifiers, {"Marksmanship L2", "Marksmanship LX"}):
        totalMod -= 3
    if ("fireteam 5" in shooterModifiers):
        totalMod += 3
    if ("TinBot E (Spotter)" in shooterModifiers):
        totalMod += 3
    if ("Marksmanship LX" in shooterModifiers):
        totalMod += 6
    totalMod += shooterData["rangeInfo"][targetData["unitId"]]
    # ------------------------------------------------------------------------------------------------------------------
    return totalMod


# Returns true if the shooter is being attacked at by the target, and either has Sixth Sense L2 or is within 8 inches
#   and has Sixth Sense L1
def sixthSenseApplies(shooterData, targetData):
    targetModifiers = targetData["Modifiers"]
    shooterModifiers = shooterData["Modifiers"]
    if shooterData["unitId"] in targetData["burstSplit"] and \
            (("Sixth Sense L2" in shooterData["modifiers"])
                or ("Sixth Sense L1" in shooterData["modifiers"] and shooterData["rangeInfo"][targetData["unitId"]] <= 8)):
        return True
