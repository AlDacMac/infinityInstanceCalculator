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
    def addOrder(self, unitId, player, stats, action, modifiers=None, target=None, tool1=None, tool2=None):
        if modifiers is None:
            modifiers = set({})
        unitData = {
            "stats": stats,
            "action": action,
            "modifiers": modifiers,
            "target": target,
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
    elif actingData['action'] in smokeDodgeableAttacks and contestingData['action'] == "Smoke Dodge":
        if actingData["target"] == contestingId and not overlaps(actingData["modifiers"], ignoresSmoke):
            return True
    elif actingData['action'] == "Smoke Dodge" and contestingData['action'] in smokeDodgeableAttacks:
        if contestingData["target"] == actingId and not overlaps(contestingData["modifiers"], ignoresSmoke):
            return True



