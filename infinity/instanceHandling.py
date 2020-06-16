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
            "losInfo": losInfo,         # Dict from string (target IDs) to set (of conditions that apply to LOS, such as "noLOS", or "Eclipse")
            "rangeInfo": rangeInfo,     # Dict from string (target IDs) to int (range)
            "coverInfo": coverInfo,     # A set of the target Ids of units with partial cover agaisnt the firer
            "modifiers": modifiers,     # A set of skills and equipment, stored as strings
            "burstSplit": target,       # A dict from string (target IDs) to int (burst for that target)
            "tool1": tool1,
            "tool2": tool2
        }
        if player == 1:
            self.active[unitId] = unitData
        else:
            self.reactive[unitId] = unitData

    # contestBetween takes two unitIds and determines if they contest each other.
    # We assume that two actions either mutually contest or mutually don't, even if one action does not actually
    #   require dice rolls, i.e direct template weapon
    def contestBetween(self, actingId, reactingId):
        actingData = self.active[actingId]
        reactingData = self.reactive[reactingId]
        if overlaps(actingData["modifiers"], nonContest) or overlaps(reactingData["modifiers"], nonContest):
            return False
        elif actingData["action"] in genericAttacks and reactingData["action"] in genericAttacks:
            if actingId in reactingData["burstSplit"] and reactingId in actingData["burstSplit"]:
                return True
        elif actingData['action'] in dodgeableAttacks and reactingData['action'] in dodges:
            if reactingId in actingData["burstSplit"]:
                return True
        elif actingData['action'] in dodges and reactingData['action'] in dodgeableAttacks:
            if actingId in reactingData["burstSplit"]:
                return True
        elif actingData['action'] in commsAttacks and reactingData['action'] in resets:
            if reactingId in actingData["burstSplit"]:
                return True
        elif actingData['action'] in resets and reactingData['action'] in commsAttacks:
            if actingId in reactingData["burstSplit"]:
                return True
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






