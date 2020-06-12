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
def contested(activeId, activeData, reactiveId, reactiveData):
    if overlaps(activeData["modifiers"], nonContest) or overlaps(reactiveData["modifiers"], nonContest):
        return False
