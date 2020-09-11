from dataParsing import *
from math import *
from misc.misc import overlaps
from dicemaths.infinity import (contested_roll_hit_avg, uncontested_hit_avg)
import re

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

dodgeableAttacks = {"BS Attack", "Intuitive Attack", "Speculative Fire", "Marksmanship LX", "Triangulated Fire", "CC Attack"}

smokeDodgeableAttacks = {"BS Attack", "Marksmanship LX", "Triangulated Fire"}

bsAttacks = {"BS Attack", "Intuitive Attack", "Speculative Fire", "Marksmanship LX", "Triangulated Fire"}

ccAttacks = {"CC Attack", "Assault"}

allowCover = {"BS Attack", "Speculative Fire"}

dodges = {"Dodge", "Change Facing", "Engage"}

commsAttacks = {"Hacking", "Jammer", "Sat-Lock"}

resets = {"Reset"}

nonContest = {"nonContest", "Berserk"}

# ----------------------------------------------------------------------------------------------------------------------
# Tags used to denote categories of skill/equipment
# ----------------------------------------------------------------------------------------------------------------------

ignoresSmoke = ("MSV 2", "MSV 3")

sixthSense = {"Sixth Sense L1", "Sixth Sense L2"}

# ----------------------------------------------------------------------------------------------------------------------


# A list of units, what action they are performing, and what their target it.
# TODO Do a proper reformat of methods, some should be instance methods and some should not, depending on if they need to make 
#   use of the structure of the Instance.
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

    def addOrder(self, unitId, player, stats, action, losInfo=dict({}), rangeInfo=dict({}), coverInfo=set({}), modifiers=set({}), burstSplit=dict({}), tool1=None, tool2=None):
        unitData = {
            "unitId": unitId,           # This is kept here so that we can tell if two units are targting each other from just the data dict
            "player": player,           # 1 for active, 2 for reactive
            "stats": stats,
            "action": action,
            # TODO implement cases for no LOS, where visual mods don't apply
            "losInfo": losInfo,         # Dict from string (target IDs) to set (of conditions that apply to LOS, such as "noLOS", or "Eclipse")
            "rangeInfo": rangeInfo,     # Dict from string (target IDs) to int (range)
            "coverInfo": coverInfo,     # A set of the target Ids of units with partial cover agaisnt the firer - not that this does not mean that cover can be applied as marksmanship or template weapons ignore it
            "modifiers": modifiers,     # A set of skills and equipment, stored as strings
            # TODO when the web app sets inputs to here, have dodge target everyone targeting the dodger
            "burstSplit": burstSplit,       # A dict from string (target IDs) to int (burst for that target)
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
            if not(id in unitData["losInfo"]):
                unitData["losInfo"][id] = {}
            if not(id in unitData["rangeInfo"]):
                unitData["rangeInfo"][id] = 0
        self.orders[unitId] = unitData

    


    def calculateStat(self, actingId):
        actingData = self.orders[actingId]
        if actingData["action"] in bsAttacks:
            if "attr" in actingData["tool1"]:
                return actingData["tool1"]["attr"].lower()
            else:
                return "bs"
        elif actingData["action"] in dodges:
            return "ph"
        elif actingData["action"] == "CC Attack":
            return "cc"

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
            and actingData["unitId"] in contestingData["burstSplit"] and contestingData["unitId"] in actingData["burstSplit"]
            and not("Direct Template" in actingData["tool1"]["template"]) 
            and not("Direct Template" in contestingData["tool1"]["template"])):
                return True
        elif (
            actingData['action'] in dodgeableAttacks and contestingData['action'] in dodges
            and contestingData["unitId"] in actingData["burstSplit"]
            and not("Direct Template" in actingData["tool1"]["template"]) 
            ):
                return True
        elif (
            actingData['action'] in dodges and contestingData['action'] in dodgeableAttacks
            and actingData["unitId"] in contestingData["burstSplit"]
            and not("Direct Template" in contestingData["tool1"]["template"])
            ):
                return True
        elif (
            actingData['action'] in commsAttacks and contestingData['action'] in resets
            and contestingData["unitId"] in actingData["burstSplit"]
            ):
                return True
        elif (
            actingData['action'] in resets and contestingData['action'] in commsAttacks
            and actingData["unitId"] in contestingData["burstSplit"]
            ):
                return True
        # TODO take acount of smoke special dodge being able to block multiple attakcs, have a list that initially includes
        #   everyone when asking the smoke dodger to specify targets but that people can be removed from
        # Smoke dodges keep a list of all those who the smoke blocks in their burstSplit field
        elif ( 
            actingData['action'] in smokeDodgeableAttacks and contestingData['action'] == "Smoke Dodge"     
            and contestingData["unitId"] in actingData["burstSplit"] and actingData["unitId"] in contestingData["burstSplit"]
            and not overlaps(actingData["modifiers"], ignoresSmoke)):
                return True
        elif (
            actingData['action'] == "Smoke Dodge" and contestingData['action'] in smokeDodgeableAttacks
            and actingData["unitId"] in contestingData["burstSplit"]  and contestingData["unitId"] in actingData["burstSplit"]
            and not overlaps(contestingData["modifiers"], ignoresSmoke)
            ):
                return True
        else:
            return False


    def calcModsRecieved(self, actingId, contestingId):
        action = self.orders[actingId]["action"]
        if action in bsAttacks:
            return self.bsModsRecieved(actingId, contestingId)
        elif action in dodges:
            return self.dodgeModsRecieved(actingId, contestingId)
        elif action in ccAttacks:
            return self.ccModsRecieved(actingId, contestingId)


    def calcModsInflicted(self, contestingId, actingId):
        action = self.orders[contestingId]["action"]
        if action in bsAttacks:
            return self.bsModsInflicted(contestingId, actingId)
        elif action in dodges:
            return self.dodgeModsInflicted(contestingId, actingId)
        elif action in ccAttacks:
            return self.ccModsInflicted(contestingId, actingId)

    # For the sake of consistency, the unit that the modifiers will apply to should always come first in the variables
    #   - the "acting" can be thought of as the unit who's choice of action causes the modifiers

    # TODO add proper checks when face to face is required
    # Calculates the net modifier that a model applies to an enemy by a bs attack against them.
    #   This calcualtion is done seperately from bsModsRecieved as otherwise we could not handle someone not getting mods
    #   from a model shooting, but not at them.
    def bsModsInflicted(self, targetId, shooterId):
        targetData = self.orders[targetId]
        shooterData = self.orders[shooterId]
        targetModifiers = targetData["modifiers"]
        shooterModifiers = shooterData["modifiers"]
        totalMod = 0   
        if not sixthSenseApplies(targetId, shooterId):
            if not ("Multispectral Visor L3" in targetModifiers):
                if ("Surprise Shot L2:Camo" in shooterModifiers):
                    totalMod -= 6
                elif ("Surprise Shot L1:camo" in shooterModifiers):
                    totalMod -= 3
            if ({"Biometric Visor L1", "Biometric Visor L2"}.isdisjoint(targetModifiers)):
                if ("Surprise Shot L2:imp/echo" in shooterModifiers):
                    totalMod -= 6
                elif ("Surprise Shot L1:imp/echo" in shooterModifiers):
                    totalMod -= 3
            if ("Surprise Shot L2:decoy" in shooterModifiers):
                totalMod -= 6
            elif ("Surprise Shot L1:decoy" in shooterModifiers):
                totalMod -= 3
        if "Full Auto L2" in shooterModifiers and self.contested(targetId, shooterId):
            totalMod -= 3
        return totalMod


    # TODO remember to do max/min when modsRecieved and modsInflicted are combined
    # TODO consider making calculation of LOS mods its own thing
    # TODO implement triangulated fire
    def bsModsRecieved(self, shooterId, targetId):
        totalMod = 0
        shooterData = self.orders[shooterId]
        targetData = self.orders[targetId]
        shooterModifiers = shooterData["modifiers"]
        targetModifiers = targetData["modifiers"]
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
        # Other mods
        # ------------------------------------------------------------------------------------------------------------------
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


    def dodgeModsRecieved(self, dodgerId, attackerId):
        totalMod = 0
        dodgerData = self.orders[dodgerId]
        attackerData = self.orders[attackerId]
        dodgerModifiers = dodgerData["modifiers"]
        attackerModifiers = attackerData["modifiers"]
        if dodgerData["stats"]["type"] == "TAG":
            totalMod -= 3
        elif dodgerData["stats"]["type"] == "REM" or "Motorcycle" in dodgerModifiers:
            totalMod -= 3
        # ------------------------------------------------------------------------------------------------------------------
        # LOS Mods
        # ------------------------------------------------------------------------------------------------------------------
        if "noLof" in dodgerData["losInfo"][attackerData["unitId"]] and not(attackerData["weapon"]["template"] == "No") and not sixthSenseApplies(dodgerData, attackerData):
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


    def dodgeModsInflicted(self, attackerId, dodgerId):
        totalMod = 0
        attackerData = self.orders[attackerId]
        dodgerData = self.orders[dodgerId]
        dodgerModifiers = dodgerData["modifiers"]
        attackerModifiers = attackerData["modifiers"]
        # ------------------------------------------------------------------------------------------------------------------
        # Mods from cc special skills
        # ------------------------------------------------------------------------------------------------------------------
        if not ("Natural Born Warrior: A" in attackerModifiers):
            if ("I-Kohl L3" in dodgerModifiers):
                totalMod -= 9
            elif ("I-Kohl L2" in dodgerModifiers):
                totalMod -= 6
            elif ("I-Kohl L1" in dodgerModifiers):
                totalMod -= 3
        # ------------------------------------------------------------------------------------------------------------------
        return totalMod

    
    def ccModsRecieved(self, attackerId, targetId):
        totalMod = 0
        attackerData = self.orders[attackerId]
        attackerModifiers = attackerData["modifiers"]
        targetData = self.orders[targetId]
        targetModifiers = targetData["modifiers"]
        # Weapon specific modifiers (i.e D-Charges)
        if "note" in attackerData["tool1"]:
            modRegex = re.compile(r'CC\((?P<mod>-?..?)\)')      #Searches for a CC mod note, and seperates the mod into a group
            m = modRegex.match(attackerData["tool1"]["note"])
            if m:
                totalMod += int(m.group("mod"))
        # ------------------------------------------------------------------------------------------------------------------
        # CC Special Skills
        # ------------------------------------------------------------------------------------------------------------------
        if not ("Natural Born Warrior: A" in targetModifiers): 
            if "Martial Arts L3" in attackerModifiers:
                totalMod += 3
            if overlaps({"Protheion L1", "Protheion L5"}, attackerModifiers):
                totalMod += 3
            if overlaps({"Guard L2", "Guard L3"}, attackerModifiers):
                totalMod += 3
            if "Natural Born Warrior: B" in attackerModifiers:
                totalMod =+ 3
            if "Berserk" in attackerModifiers:
                totalMod += 6
        if attackerData["action"] == "Assault":
            totalMod -= 3
        return totalMod


    def ccModsInflicted(self, targetId, attackerId):
        totalMod = 0
        targetData = self.orders[targetId]
        targetModifiers = targetData["modifiers"]
        attackerData = self.orders[attackerId]
        attackerModifiers = attackerData["modifiers"]
        # ------------------------------------------------------------------------------------------------------------------
        # CC Special Skills
        # ------------------------------------------------------------------------------------------------------------------
        if not ("Natural Born Warrior: A" in targetModifiers) and self.contested(targetId, attackerId): 
            if ("Martial Arts L5" in attackerModifiers):
                totalMod -= 6
            elif overlaps({"Martial Arts L1", "Martial Arts L3"}, attackerModifiers):
                totalMod -= 3
            if overlaps({"Protheion L2", "Protheion L5"}, attackerModifiers):
                totalMod -= 3
            if overlaps({"Guard L1", "Guard L2", "Guard L3"}, attackerModifiers):
                totalMod -= 3
            if ("I-Khol L9" in attackerModifiers):
                totalMod -= 9
            elif ("I-Khol L2" in attackerModifiers):
                totalMod -= 6
            elif ("I-Khol L1" in attackerModifiers):
                totalMod -= 3
        # ------------------------------------------------------------------------------------------------------------------
        # Surprise attack
        # ------------------------------------------------------------------------------------------------------------------
        if not(sixthSenseApplies(targetData, attackerData) or ("Natural Born Warrior: A" in targetModifiers)):
            if ("Surprise Attack:camo" in attackerModifiers):
                if not ("Multispectral Visor L3" in targetModifiers):
                    totalMod -= 6
            elif ("Surprise Attack:imp/echo" in attackerModifiers):
                if overlaps({"Biometric Visor L1", "Biometric Visor L2"}, targetModifiers):
                    totalMod -= 6
            elif ("Surprise Attack:decoy" in attackerModifiers):
                totalMod -= 6
        return totalMod

# Returns true if the attacker is in turn being attacked at by the target, and either has Sixth Sense L2 or is within 8 inches
#   and has Sixth Sense L1
def sixthSenseApplies(attackerData, targetData):
    targetModifiers = targetData["modifiers"]
    attackerModifiers = attackerData["modifiers"]
    if attackerData["unitId"] in targetData["burstSplit"] and \
            (("Sixth Sense L2" in attackerModifiers)
                or ("Sixth Sense L1" in attackerModifiers and attackerData["rangeInfo"][targetData["unitId"]] <= 8)):
        return True

def calcFailedSaves(attackerData, targetData, hits, crits, ammo):
    failedArmSaves = 0
    failedBtsSaves = 0
    failedPhSaves = 0
    damage = calculateDamage(attackerData)
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

    return {"failedArmSaves": round(failedArmSaves, 4), 
            "failedBtsSaves": round(failedBtsSaves, 4), 
            "failedPhSaves": round(failedPhSaves, 4)}


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
    # - note on this: we'd have to remove from armWoundAmmo
    # - alternately, have the "woundAmmo" check as an else if of shock and viral checks
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
        unitData["effects"]["immobilised2"] += failedPhSaves
        effects["immobilised2"] += failedPhSaves
    if "Viral" in ammo and unitData["stats"]["wounds"] == 1:
        unitData["effects"]["dead"] += failedBtsSaves
        effects["dead"] += failedBtsSaves
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
# TODO: Add checks so that fatality only activates on attacks that use bs attribute
def calculateDamage(unitData):
    damString = unitData["tool1"]["damage"]
    phRegex = re.compile(r'PH.*')
    wipRegex = re.compile(r'WIP.*')
    phMatch = phRegex.match(damString)
    wipMatch = wipRegex.match(damString)
    if phMatch:
        damage = unitData["stats"]["ph"]
        if not(damString[2:] == ''):
            damage += int(damString[2:])
    elif wipMatch:
        damage = unitData["stats"]["wip"]
        if not(damString[3:] == ''):
            damage += int(damString[3:])
    else:
        damage = int(damString)
    if ((("Fatality L1" in unitData["modifiers"]) or ("Fatality L2" in unitData["modifiers"])) and
        not("Direct Template" in unitData["tool1"]["template"])):
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
    newAmmo = set(ammo.copy())
    if "Total Immunity" in unitData["modifiers"]:
        newAmmo = set({})
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

