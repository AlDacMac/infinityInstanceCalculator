from dataParsing import *
from math import *
from misc.misc import overlaps

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

btsImm2Ammo = {"E/M", "E/M2"}

btsStunAmmo = {"Stun", "Flash"}

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

bsAttacks = {"BS Attack", "Intuitive Attack", "Speculative Fire", "Marksmanship LX", "Triangulated Fire"}

allowCover = {"BS Attack", "Speculative Fire"}

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


# A list of units, what action they are performing, and what their target it.
# TODO consider reformatting all methods to be part of the instance class, now that they can simply take id
class Instance:
    def __init__(self):
        # All units, regardless of player, are stored in the orders dict
        # TODO consider reformatting methods to take IDs instead of data dicts now that we only use
        #   a single dict and it's easy to retrive stuff.
        self.orders = dict({})
        # The trackers are used for creating unique IDs
        self.activeTracker = 0
        self.reactiveTracker = 0

    # The dictionaries work with burst splitting - a single unit Id is  able to target mutliple
    #   target is a dict from unitId to the burst dedicated to that unit
    #   this also works for template weapons

    def addOrder(self, unitId, player, stats, action, losInfo=dict({}), rangeInfo=dict({}), coverInfo=set({}), modifiers=set({}), target=dict({}), tool1=None, tool2=None):
        unitData = {
            "unitId": unitId,           # This is kept here so that we can tell if two units are targting each other from just the data dict
            "player": player,           # 1 for active, 2 for reactive
            "stats": stats,
            "action": action,
            "losInfo": losInfo,         # Dict from string (target IDs) to set (of conditions that apply to LOS, such as "noLOS", or "Eclipse")
            "rangeInfo": rangeInfo,     # Dict from string (target IDs) to int (range)
            "coverInfo": coverInfo,     # A set of the target Ids of units with partial cover agaisnt the firer - not that this does not mean that cover can be applied as marksmanship or template weapons ignore it
            "modifiers": modifiers,     # A set of skills and equipment, stored as strings
            "burstSplit": target,       # A dict from string (target IDs) to int (burst for that target)
            "target": target,
            "tool1": tool1,
            "tool2": tool2,
            "effects": {
                "wounded": 0,
                "unconscious": 0,
                "immobilised2": 0,
                "immobilised1": 0,
                "dead": 0,
                "isolated": 0,
                "posessed": 0,
                "stunned": 0,
                "burnt": 0,
                "sepsitorised": 0,
                "targeted": 0
            }
        }
        for id in self.orders.keys():
            self.orders[id]["losInfo"][unitId] = {}
            self.orders[id]["rangeInfo"][unitId] = 0
            unitData["losInfo"][id] = {}
            unitData["rangeInfo"][id] = 0
        self.orders[unitId] = unitData


    # Contested takes two unitIds and their corresponding data dicts and determines if they contest each other.
    # We assume that two actions either mutually contest or mutually don't, even if one action does not actualy require dice
    #   i.e direct template weapon
    # TODO Figure out if direct template weapons should be in nonContest
    #   we do need to invoke special logic if the opponent is dodging, so they probably shouldn't - we can add the 1 hit
    #   after hit calcs are made
    #       hell we could just treat DTWs as always rolling 0
    def contested(self, actingId, contestingId):
        actingData = self.orders[actingId] 
        contestingData = self.orders[contestingId]
        if overlaps(actingData["modifiers"], nonContest) or overlaps(contestingData["modifiers"], nonContest):
            return False
        elif (
            actingData["action"] in genericAttacks and contestingData["action"] in genericAttacks
            and actingData["unitId"] == contestingData["target"] and contestingData["unitId"] == actingData["target"]
            ):
                return True
        elif (
            actingData['action'] in dodgeableAttacks and contestingData['action'] in dodges
            and actingData["target"] == contestingData["unitId"]
            ):
                return True
        elif (
            actingData['action'] in dodges and contestingData['action'] in dodgeableAttacks
            and contestingData["target"] == actingData["unitId"]
            ):
                return True
        elif (
            actingData['action'] in commsAttacks and contestingData['action'] in resets
            and actingData["target"] == contestingData["unitId"]
            ):
                return True
        elif (
            actingData['action'] in resets and contestingData['action'] in commsAttacks
            and contestingData["target"] == actingData["unitId"]
            ):
                return True
        # TODO take acount of smoke special dodge being able to block multiple attakcs, have a list that initially includes
        #   everyone when asking the smoke dodger to specify targets but that people can be removed from
        # Smoke dodges keep a list of all those who the smoke blocks in their targets field
        elif ( 
            actingData['action'] in smokeDodgeableAttacks and contestingData['action'] == "Smoke Dodge"     
            and actingData["target"] == contestingData["unitId"] and actingData["unitId"] in contestingData["target"]
            and not overlaps(actingData["modifiers"], ignoresSmoke)):
                return True
        elif (
            actingData['action'] == "Smoke Dodge" and contestingData['action'] in smokeDodgeableAttacks
            and contestingData["target"] == actingData["unitId"] and contestingData["unitId"] in actingData["target"]
            and not overlaps(contestingData["modifiers"], ignoresSmoke)
            ):
                return True
        else:
            return False


# For the sake of consistency, the unit that the modifiers will apply to should always come first in the variables

# Calculates the net modifier that a model applies to an enemy by a bs attack against them.
#   This calcualtion is done seperately from bsModsRecieved as otherwise we could not handle someone not getting mods
#   from a model shooting, but not at them.
def bsModsInflicted(targetData, shooterData):
    targetModifiers = targetData["modifiers"]
    shooterModifiers = shooterData["modifiers"]
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


# TODO remember to do max/min when modsRecieved and modsInflicted are combined

# TODO consider making calculation of LOS mods its own thing
# TODO implement triangulated fire
def bsModsRecieved(shooterData, targetData):
    totalMod = 0
    targetModifiers = targetData["modifiers"]
    shooterModifiers = shooterData["modifiers"]
    # ------------------------------------------------------------------------------------------------------------------
    # Visibility mods, elifs are used as only the worst will apply
    # ------------------------------------------------------------------------------------------------------------------
    if "noLof" in shooterData["losInfo"][targetData["unitId"]] and not sixthSenseApplies(shooterData, targetData):
        totalMod -= 6
    elif "eclipse" in (shooterData["losInfo"][targetData["unitId"]] and not sixthSenseApplies(shooterData, targetData)):
        totalMod -= 6
    elif "Smoke" in shooterData["losInfo"][targetData["unitId"]] \
            and not overlaps(shooterModifiers, {"Multispectral Visor L2", "Multispectral Visor L3"}) \
            and not sixthSenseApplies(shooterData, targetData):
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
    if coverApplies(shooterData, targetData):
        totalMod -= 3
    if ("fireteam 5" in shooterModifiers):
        totalMod += 3
    if ("TinBot E (Spotter)" in shooterModifiers):
        totalMod += 3
    if (shooterData["action"] == "Marksmanship LX"):
        totalMod += 6
    totalMod += shooterData["rangeInfo"][targetData["unitId"]]
    # ------------------------------------------------------------------------------------------------------------------
    return totalMod

def dogeModsReceived(dodgerData, attackerData):
    totalMod = 0
    dodgerModifiers = dodgerData["modifiers"]
    attackerModifiers = attackerData["modifiers"]
    if dodgerData["stats"]["type"] == "TAG":
        totalMod -= 3
    elif dodgerData["stats"]["type"] == "REM" or "Motorcycle" in dodgerModifiers:
        totalMod -= 3
    # ------------------------------------------------------------------------------------------------------------------
    # LOS Mods
    # ------------------------------------------------------------------------------------------------------------------
    if "noLof" in dodgerData["losInfo"][attackerData["targetId"]] and not(attackerData["weapon"]["template"] == "No") and not sixthSenseApplies(dodgerData, attackerData):
        totalMod -= 3
    elif "Poor Visibility Zone" in dodgerData["losInfo"][attackerData["unitId"]]:
        totalMod -= 6
    elif "Low Visibility Zone" in dodgerData["losInfo"][attackerData["unitId"]]:
        totalMod -= 3
    # ------------------------------------------------------------------------------------------------------------------
    if "Hyper-Dynamics L3" in dodgerModifiers:
        totalMod += 9
    elif "Hyper-Dynamics L2" in dodgerModifiers:
        totalMod += 6
    elif "Hyper-Dynamics L1" in dodgerModifiers:
        totalMod += 3
    return totalMod

def dodgeModsInflicted(attackerData, dodgerData):
    totalMod = 0
    dodgerModifiers = dodgerData["modifiers"]
    attackerModifiers = attackerData["modifiers"]
    # ------------------------------------------------------------------------------------------------------------------
    if not ("Natural Born Warrior: A" in attackerModifiers):
        if ("I-Khol L3" in dodgerModifiers):
            totalMod -= 9
        elif ("I-Khol L2" in dodgerModifiers):
            totalMod -= 6
        elif ("I-Khol L1" in dodgerModifiers):
            totalMod -= 3
    # ------------------------------------------------------------------------------------------------------------------
    return totalMod

# Returns true if the shooter is being attacked at by the target, and either has Sixth Sense L2 or is within 8 inches
#   and has Sixth Sense L1
def sixthSenseApplies(shooterData, targetData):
    targetModifiers = targetData["modifiers"]
    shooterModifiers = shooterData["modifiers"]
    if shooterData["unitId"] in targetData["burstSplit"] and \
            (("Sixth Sense L2" in shooterData["modifiers"])
                or ("Sixth Sense L1" in shooterData["modifiers"] and shooterData["rangeInfo"][targetData["unitId"]] <= 8)):
        return True

def calcFailedSaves(attackerData, targetData, hits, crits, ammo):
    failedArmSaves = 0
    failedBtsSaves = 0
    failedPhSaves = 0
    damage = calculateDamage(attackerData)
    if ("Fatality L1" in attackerData["modifiers"]):
        damage += 1
    arm = targetData["stats"]["arm"]
    bts = targetData["stats"]["bts"]
    ph = targetData["stats"]["ph"]
    # just because you make the roll with arm instead of bts, doesn't make it combo with arm rolls
    #   - therefore if one stat (arm or bts), has an ammo type that you're immune to being sent at it, 
    #   - you can simply replace that stat with the other if the other is higher
    if ("Total Immunity" in targetData["modifiers"] or ("Bioimmunity" in targetData["modifiers"] and "Shock" in ammo)):
        arm = max(arm, bts)
    if ("Total Immunity" in targetData["modifiers"] or ("Bioimmunity" in targetData["modifiers"] and "Viral" in ammo)):
        arm = max(arm, bts)
    if ("Monofilament" in ammo or "K1" in ammo):
        arm = 0
        damage = 12
    elif ("AP" in ammo):
        arm = ceil(arm / 2.0)
    if ("Breaker" in ammo or "E/M" in ammo or "E/M2" in ammo):
        bts = ceil(bts/2.0)
    if ("ADH" in ammo):
        ph = max(0, ph - 6)
    if coverApplies(targetData, attackerData):
        arm += 3
        bts += 3
    armfailchance = min(1, max(0, (damage - arm) / 20.0))
    btsfailchance = min(1, max(0, (damage - bts) / 20.0))
    phfailchance = min(1, max(0, (damage - ph) / 20.0))

    # Failed saves from crits
    if overlaps(armEffectOnCrit, ammo):
        failedArmSaves += crits
    if overlaps(btsEffectOnCrit, ammo):
        failedBtsSaves += crits
    # I assume regular bts saves from plasma only occur on crit if there's nothing causing normal bts crits
    elif("Plasma" in ammo):
        failedBtsSaves += crits * btsfailchance
    if overlaps(phEffectOnCrit, ammo):
        failedPhSaves += crits

    # Regular arm saves
    if("EXP" in ammo):
        failedArmSaves += (hits * 3 * armfailchance) + (crits * 2 * armfailchance)
    elif("DA" in ammo):
        failedArmSaves += (hits * 2 * armfailchance) + (crits * armfailchance)
    elif("Fire" in ammo):
        failedArmSaves += recurringFireAvg(armfailchance, (crits + hits))
    elif overlaps(armAmmo, ammo):
        failedArmSaves += armfailchance * hits

    # Regular bts saves
    if overlaps({"DT", "EM/2", "Stun", "Viral"}, ammo):
        failedBtsSaves += (hits * 2 * btsfailchance) + (crits * btsfailchance)
    elif overlaps(btsAmmo, ammo):
        failedBtsSaves += hits * btsfailchance

    # Regular ph saves
    if overlaps(phAmmo, ammo):
        failedPhSaves += phfailchance * hits

    return {"failedArmSaves": failedArmSaves, 
            "failedBtsSaves": failedBtsSaves, 
            "failedPhSaves": failedPhSaves}


# Adds the effects of failed saves to a unit with respect to the ammo used on it, returns the increase in average effects
def addSaveEffects(unitData, failedArmSaves, failedBtsSaves, failedPhSaves, ammo):
    effects = {
                "wounded": 0,
                "unconscious": 0,
                "immobilised2": 0,
                "immobilised1": 0,
                "dead": 0,
                "isolated": 0,
                "posessed": 0,
                "stunned": 0,
                "burnt": 0,
                "sepsitorised": 0,
                "targeted": 0
            }
    if overlaps(ammo, armWoundAmmo):
        unitData["effects"]["wounded"] += failedArmSaves
        effects["wounded"] += failedArmSaves
    if "T2" in ammo:
        unitData["effects"]["wounded"] += failedArmSaves
        effects["wounded"] += failedArmSaves
    # TODO consider how to handle shock sending people straight to dead - do we include it in the wounds section also?
    if "Monofilament" in ammo or ("shock" in ammo and unitData["stats"]["wounds"] == 1):
        unitData["effects"]["dead"] += failedArmSaves
        effects["ead"] += failedArmSaves
    if overlaps(ammo, btsWoundAmmo):
        unitData["effects"]["wounded"] += failedArmSaves
        effects["wounded"] += failedArmSaves
    if overlaps({"E/M", "E/M2"}, ammo):
        unitData["effects"]["isolated"] += failedBtsSaves
        effects["isolated"] += failedBtsSaves
        if overlaps(unitData["stats"]["type"], {"HI", "TAG", "REM"}):
            unitData["effects"]["immobilised2"] += failedBtsSaves
            effects["immobilised2"] += failedBtsSaves
    if "Sepsitor" in ammo:
        unitData["effects"]["sepsitorised"] += failedBtsSaves
        effects["sepsitorised"] += failedBtsSaves
    if overlaps(btsStunAmmo, ammo):
        unitData["effects"]["stunned"] += failedBtsSaves
        effects["stunned"] += failedBtsSaves
    if "ADH" in ammo:
        unitData["effects"]["immobilised2"] += 1
        effects["immobilised2"] += 1
    if "Viral" in ammo and unitData["stats"]["wounds"] == 1:
        unitData["effects"]["dead"] += 1
        effects["immobilised2"] += 1
    return effects


# Given a shooter and a target, returns true if the target has partial cover to the shooter, and false otherwise
def coverApplies(shooterData, targetData):
    if not(targetData["unitId"] in shooterData["coverInfo"] or
            ("Nanoscreen" in targetData["modifiers"] and not("Burnt" in targetData["modifiers"]))):
        return False
    elif overlaps({"Impetuous", "Extremely Impetuous"}, targetData["modifiers"]):
        return False
    elif not(shooterData["action"] in allowCover):
        return False
    elif ("Marksmanship L2" in shooterData["modifiers"]):
        return False
    elif not(shooterData["tool1"]["template"] == "No"):
        return False
    return True

# Returns the damage dealt by the unit's weapon, adjusted by modifiers
def calculateDamage(unitData):
    damage = unitData["tool1"]["damage"]
    if (("Fatality L1" in unitData["modifiers"]) or ("Fatality L2" in unitData["modifiers"])):
        damage += 1
    return damage


# Returns the average number of failed saves in situations where failing a save requires another save to be made
def recurringFireAvg(failchance, nosaves):
    failedsaves = 0
    for i in range(20):
        failed = failchance * nosaves
        nosaves = failed
        failedsaves += failed
    return failedsaves


# Given a unit and a list of ammo, returns a new list modified to not include ammo the unit is immune to
def applyImmunity(unitData, ammo):
    newAmmo = ammo.copy()
    if "Total Immunity" in unitData["modifiers"]:
        newAmmo = {}
    if "Bioimmunity" in unitData["modifiers"]:
        newAmmo.discard("Shock")
    if "Shock Immunity" in unitData["modifiers"]:
        newAmmo.discard("Shock")
        newAmmo.discard("Viral") 
    # We must add normal ammo to newAmmo if the ammo set is capable of causing wounds, and 
    #   newAmmo is not
    if ((overlaps(ammo, btsWoundAmmo) and not overlaps(newAmmo, btsWoundAmmo)) or overlaps(ammo, armWoundAmmo)):
        newAmmo.add("N")
    # Sepsitor is not affected by total immunity, neither is ADH
    if "Sepsitor" in ammo:
        newAmmo.add("Sepsitor")
    if "ADH" in ammo:
        newAmmo.add("ADH")
    return newAmmo

