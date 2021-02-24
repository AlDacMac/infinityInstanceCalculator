from instanceHandling import (Instance, calcFailedSaves, applyImmunity, addSaveEffects, calculateDamage)
from dataParsing import (getUnitStats, getUnitSpec, getWeapon)
import pytest

# Test Data Structure
testInstance = Instance()

# Tests on the instance data structure
testInstance.addOrder("achilles1", 1, getUnitStats("aleph", "Achilles"), "BS Attack", modifiers=getUnitSpec("aleph", "Achilles"), tool1=getWeapon("Spitfire"))
testInstance.addOrder("fusilier1", 2, getUnitStats("pano", "Fusilier"), "BS Attack")

def test_achilles_added():
    assert testInstance.orders["achilles1"]["action"] == "BS Attack"

def test_fusi_added():
    assert testInstance.orders["fusilier1"]["action"] == "BS Attack"

def test_getUnitStats_achilles():
    assert testInstance.orders["achilles1"]["stats"] == {
        "cc": 24,
        "bs": 15,
        "ph": 15,
        "wip": 15,
        "arm": 4,
        "bts": 6,
        "type": "HI"
    }

# Tests on getUnitSpec
testInstance.addOrder("penny1", 1, getUnitStats("alep", "Penthesilea"), "Dodge", modifiers=getUnitSpec("alep", "Penthesilea"))

def test_getUnitSpec_achilles():
    assert getUnitSpec("aleph", "Achilles") == {"Martial Arts L4", "Multiterrain", "ODD: Optical Disruptor", "Kinematika L2"}

def test_getUnitSpec_penny():
    assert testInstance.orders["penny1"]["modifiers"] == {"I-Kohl L2","Motorcycle","ODD: Optical Disruptor","V: No Wound Incapacitation","Kinematika L2"}

def test_getUnitSpec_child():
    assert getUnitSpec("ariadna", "Kazak Spetsnaz: Boarding Shotgun") == {
        "Marksmanship L2",
        "Martial Arts L2",
        "CH: Mimetism",
        "AD: Parachutist"
    }

def test_getUnitSPec_syncedProfile():
    assert getUnitSpec("ariadna", "K-9 Antipode (Strelok)") == {
        "G: Synchronized",
        "CH: Camouflage",
        "Forward Deployment L2",
        "Kinematika L2",
        "Sensor",
        "Super-Jump"
    }

def test_getUnitSpec_masterProfile():
    assert getUnitSpec("pano", "Peacemaker") == {
        "Mechanized Deployment",
        "G: Remote Presence",
        "Repeater"
    }

# Tests on getWeapon

def test_getWeapon():
    assert getWeapon("Combi Rifle") == {
        "name": "Combi Rifle",
        "burst": "3",
        "ammo": "N",
        "damage": "13",
        "short_dist": "8",
        "short_mod": "3",
        "medium_dist": "16",
        "medium_mod": "3",
        "long_dist": "32",
        "long_mod": "-3",
        "max_dist": "48",
        "max_mod": "-6",
        "cc": "No",
        "template": "No",
        "suppressive": "Yes",
        "note": ""
    }

def test_getWeapon_special():
    assert getWeapon("Sepsitor") == {
        "name": "Sepsitor",
        "burst": "1",
        "ammo": "Sepsitor",
        "damage": "WIP",
        "short_dist": "--",
        "short_mod": "--",
        "medium_dist": "--",
        "medium_mod": "--",
        "long_dist": "--",
        "long_mod": "--",
        "max_dist": "--",
        "max_mod": "--",
        "cc": "No",
        "template": "Direct Template (Large Teardrop)",
        "uses": "2",
        "note": "Intuitive Attack"
    }

# Tests on Instance.contested
testInstance.addOrder("achilles2", 1, getUnitStats("aleph", "Achilles"), "BS Attack", modifiers=getUnitSpec("aleph", "Achilles"), tool1=getWeapon("Spitfire"))
testInstance.addOrder("fusilier2", 2, getUnitStats("pano", "Fusilier"), "BS Attack", 
    modifiers=getUnitSpec("pano", "Fusilier"), tool1=getWeapon("Combi Rifle"))
testInstance.addOrder("fusilier3", 1, getUnitStats("pano", "Fusilier"), "BS Attack", modifiers=getUnitSpec("pano", "Fusilier"))
testInstance.addOrder("hector1", 1, getUnitStats("alep", "Hector"), "BS Attack", tool1=getWeapon("Nanopulser"), burstSplit={"sphinx1": 1})
testInstance.addOrder("sphinx1", 1, getUnitStats("comb", "Sphinx"), "BS Attack", tool1=getWeapon("Heavy Flamethrower"), burstSplit={"hector1": 1})
testInstance.orders["achilles2"]["burstSplit"] = {"fusilier2"}
testInstance.orders["fusilier2"]["burstSplit"] = {"achilles2"}
testInstance.orders["fusilier3"]["burstSplit"] = {"fusilier2"}



def test_contested_true():
    assert testInstance.contested("achilles2", "fusilier2") == True

def test_contested_false():
    assert testInstance.contested("fusilier2", "fusilier3") == False

def test_contested_dtw():
    assert testInstance.contested("hector1", "sphinx1") == False

# Tests on modsRecieved and modsInflicted methods -----------------------------------------------------------------
testInstance.addOrder("achilles3", 1, getUnitStats("aleph", "Achilles"), "BS Attack", 
    modifiers=getUnitSpec("aleph", "Achilles"), tool1=getWeapon("Spitfire"))
testInstance.addOrder("fusilier4", 1, getUnitStats("pano", "Fusilier"), "BS Attack", 
    modifiers=getUnitSpec("pano", "Fusilier"), burstSplit={"kriza1": 1}, tool1=getWeapon("Combi Rifle"))
testInstance.addOrder("kriza1", 2, getUnitStats("nomads", "Kriza Borac"), "BS Attack", 
    modifiers=getUnitSpec("nomads", "Kriza Borac"), burstSplit={"fusilier4": 4}, tool1 = getWeapon("HMG"))
testInstance.addOrder("fusilier5", 1, getUnitStats("pano", "Fusilier"), "BS Attack", 
    modifiers=getUnitSpec("pano", "Fusilier"), tool1=getWeapon("Combi Rifle"))
testInstance.addOrder("riot1", 2, getUnitStats("nomads", "Riot Grrl"), "BS Attack", 
    modifiers=getUnitSpec("nomads", "Riot Grrl"), tool1="Spitfire")
testInstance.addOrder("penny2", 1, getUnitStats("alep", "Penthesilea"), "Dodge", modifiers=getUnitSpec("alep", "Penthesilea"))
testInstance.addOrder("rosie", 1, getUnitStats("ariadna", "Rosie"), "CC Attack", tool1=getWeapon("D-Charges (CC Mode)"), modifiers=getUnitSpec("aria", "Rosie"))

testInstance.orders["fusilier4"]["tool1"] = getWeapon("Combi Rifle")

testInstance.orders["fusilier4"]["coverInfo"].add("fusilier5")

def test_bsModsRecieved_spec():
    assert testInstance.bsModsRecieved("fusilier4", "achilles3") == -6

def test_bsRecievedGeneric_spec():
    assert testInstance.calcModsRecieved("fusilier4", "achilles3") == -6

def test_bsModsInflicted():
    assert testInstance.bsModsInflicted("fusilier4", "kriza1") == -3

def test_bsMods_cover():
    assert testInstance.bsModsRecieved("fusilier4", "fusilier5") == -3

def test_dodgeModsRecieved_modifiers():
    assert testInstance.dodgeModsRecieved("riot1", "achilles3") == 3

def test_dodgeModsRecieved_type():
    assert testInstance.dodgeModsRecieved("penny2", "fusilier4") == -3

def test_dodgeModsInflicted_modifiers():
    assert testInstance.dodgeModsInflicted("fusilier4", "penny2") == -6

def test_ccModsRecieved_dCharges():
    mod = testInstance.ccModsRecieved("rosie", "achilles3")
    assert mod == -3

# Tests for calcFailedSaves and immunity -----------------------------------------------------------------------------
testInstance.addOrder("achilles4", 1, getUnitStats("aleph", "Achilles"), "BS Attack", modifiers=getUnitSpec("aleph", "Achilles"), tool1=getWeapon("Spitfire"))
testInstance.addOrder("immFusi", 2, getUnitStats("pano", "Fusilier"), "Dodge", modifiers={"Total Immunity"})
testInstance.addOrder("simpleAvatar", 1, getUnitStats("comb", "Avatar"), "Idle")
testInstance.addOrder("ajax2", 1, getUnitStats("alep", "Ajax"), "CC Attack", modifiers={"Natural Born Warrior: B", "Berserk"}, tool1=getWeapon("EXP CCW"))

def test_failedSaves_basic():
    failed = calcFailedSaves(testInstance.orders["achilles4"], testInstance.orders["fusilier1"], 1, 0, {"N"})
    assert failed == {'failedArmSaves': 0.65, 'failedBtsSaves': 0, 'failedPhSaves': 0}

def test_failedSaves_crit():
    failed = calcFailedSaves(testInstance.orders["achilles4"], testInstance.orders["fusilier1"], 1, 1, {"N"})
    assert failed == {'failedArmSaves': 1.65, 'failedBtsSaves': 0, 'failedPhSaves': 0}

def test_failedSaves_da():
    failed = calcFailedSaves(testInstance.orders["achilles4"], testInstance.orders["fusilier1"], 1, 0, {"DA"})
    assert failed == {'failedArmSaves': 1.3, 'failedBtsSaves': 0, 'failedPhSaves': 0}

def test_failedSaves_exp():
    failed = calcFailedSaves(testInstance.orders["ajax2"], testInstance.orders["simpleAvatar"], 0.4, 0.6, {"EXP"})
    assert failed == {'failedArmSaves': 1.56, 'failedBtsSaves': 0, 'failedPhSaves': 0}

def test_immunity_basic():
    ammo = {"DA"}
    failed = calcFailedSaves(testInstance.orders["achilles4"], testInstance.orders["immFusi"], 1, 0, ammo)
    assert failed == {'failedArmSaves': 0.65, 'failedBtsSaves': 0, 'failedPhSaves': 0}

def test_immunity_arm():
    testInstance.orders["immFusi"]["stats"]["bts"] = 4
    failed = calcFailedSaves(testInstance.orders["achilles4"], testInstance.orders["immFusi"], 1, 0, {"N"})
    testInstance.orders["immFusi"]["stats"]["bts"] = 0
    assert failed == {'failedArmSaves': 0.5, 'failedBtsSaves': 0, 'failedPhSaves': 0}

# Tests for addSaveEffects
testInstance.addOrder("fusilier6", 1, getUnitStats("pano", "Fusilier"), "BS Attack", modifiers=getUnitSpec("pano", "Fusilier"))

def test_saveEffects_basic():
    effects = addSaveEffects(testInstance.orders["fusilier6"], 1, 0, 0, {"N"})
    assert effects == {
                "wounded": 1,
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

# Tests for calculateStat
testInstance.addOrder("achilles5", 1, getUnitStats("aleph", "Achilles"), "BS Attack", modifiers=getUnitSpec("aleph", "Achilles"), tool1=getWeapon("Spitfire"))
testInstance.addOrder("penny3", 1, getUnitStats("alep", "Penthesilea"), "Dodge", modifiers=getUnitSpec("alep", "Penthesilea"))

def test_calculateStat_bsAttack():
    assert testInstance.calculateStat("achilles5") == "bs"

def test_calculateStat_dodge():
    assert testInstance.calculateStat("penny1") == "ph"

# Tests for calculateDamage
testInstance.addOrder("avatar1", 1, getUnitStats("comb", "Avatar"), "BS Attack", 
    modifiers=getUnitSpec("comb", "Avatar"), tool1=getWeapon("Sepsitor"))

def test_calculateDamage_wip():
    assert calculateDamage(testInstance.orders["avatar1"]) == 17


# Temporary tests for handleBetween
testInstance.addOrder("simplefusi1", 1, getUnitStats("pano", "Fusilier"), "BS Attack",
    tool1=getWeapon("Combi Rifle"), modifiers=getUnitSpec("pano", "Fusilier"), burstSplit={"simplefusi2": 3})
testInstance.addOrder("simplefusi2", 1, getUnitStats("pano", "Fusilier"), "BS Attack", 
    tool1=getWeapon("Combi Rifle"), modifiers=getUnitSpec("pano", "Fusilier"), burstSplit={"simplefusi1": 1})
testInstance.orders["simplefusi1"]["stats"]["bs"] = 10
testInstance.orders["simplefusi2"]["stats"]["bs"] = 0

def test_tempHandleBetween():
    assert testInstance.handleBetween("simplefusi1", "simplefusi2")["wounded"] == 0.912

testInstance.addOrder("Achilles6", 1, getUnitStats("aleph", "Achilles"), "BS Attack",
    tool1=getWeapon("Spitfire"), modifiers=getUnitSpec("alep", "Achilles"), burstSplit={"simplefusi3": 1})
testInstance.addOrder("simplefusi3", 1, getUnitStats("pano", "Fusilier"), "BS Attack", 
    tool1=getWeapon("Combi Rifle"), modifiers=getUnitSpec("pano", "Fusilier"), burstSplit={"Achilles6": 1})
testInstance.orders["simplefusi3"]["stats"]["bs"] = 16

def test_tempHandleBetween_spec():
    assert testInstance.handleBetween("Achilles6", "simplefusi3")["wounded"] == 0.4066

testInstance.addOrder("simplefusi4", 1, getUnitStats("pano", "Fusilier"), "BS Attack",
    tool1=getWeapon("Combi Rifle"), modifiers=getUnitSpec("pano", "Fusilier"), burstSplit={"simplefusi5": 1})
testInstance.addOrder("simplefusi5", 1, getUnitStats("pano", "Fusilier"), "BS Attack", 
    tool1=getWeapon("Combi Rifle"), modifiers=getUnitSpec("pano", "Fusilier"), burstSplit={"simplefusi4": 1}, 
    coverInfo={"simplefusi4"})
testInstance.orders["simplefusi4"]["stats"]["bs"] = 10
testInstance.orders["simplefusi5"]["stats"]["bs"] = 3

def test_tempHandleBetween_cover():
    assert testInstance.handleBetween("simplefusi4", "simplefusi5")["wounded"] == 0.2399

testInstance.addOrder("simplefusi6", 1, getUnitStats("pano", "Fusilier"), "CC Attack",
    tool1=getWeapon("Knife"), modifiers=getUnitSpec("pano", "Fusilier"), burstSplit={"simplefusi7": 1})
testInstance.addOrder("simplefusi7", 1, getUnitStats("pano", "Fusilier"), "CC Attack",
    tool1=getWeapon("Knife"), modifiers=getUnitSpec("pano", "Fusilier"), burstSplit={"simplefusi6": 1})
testInstance.orders["simplefusi6"]["stats"]["cc"] = 10
testInstance.orders["simplefusi7"]["stats"]["cc"] = 0

def test_tempHandleBetween_cc():
    assert testInstance.handleBetween("simplefusi6", "simplefusi7")["wounded"] == 0.2185

testInstance.addOrder("myrm1", 1, getUnitStats("alep", "Myrmidon"), "BS Attack", 
    tool1=getWeapon("Chain Rifle"), modifiers=getUnitSpec("alep", "Myrmidon"), burstSplit={"simplefusi8": 1})
testInstance.addOrder("simplefusi8", 1, getUnitStats("pano", "Fusilier"), "Dodge", 
    modifiers=getUnitSpec("pano", "Fusilier"), burstSplit={"myrm1": 1})

def test_tempHandleBetween_dtw():
    assert testInstance.handleBetween("myrm1", "simplefusi8")["wounded"] == 0.3


testInstance.addOrder("avatar2", 1, getUnitStats("comb", "Avatar"), "BS Attack", 
    tool1=getWeapon("Sepsitor"), modifiers=getUnitSpec("comb", "Avatar"), burstSplit={"simplefusi9": 1})
testInstance.addOrder("simplefusi9", 1, getUnitStats("pano", "Fusilier"), "Dodge", 
    modifiers=getUnitSpec("pano", "Fusilier"), burstSplit={"avatar2": 1})

def test_tempHandleBetween_complexDtw():
    assert testInstance.handleBetween("avatar2", "simplefusi9") == {
                "wounded": 0,
                "unconscious": 0,
                "immobilised2": 0,
                "immobilised1": 0,
                "dead": 0,
                "isolated": 0,
                "posessed": 0,
                "stunned": 0,
                "burnt": 0,
                "sepsitorised": 0.425,
                "targeted": 0
            }

def test_tempHandleBetween_dodge():
    assert testInstance.handleBetween("simplefusi9", "avatar2") == (0.45, 0.05)

testInstance.addOrder("ajax1", 1, getUnitStats("alep", "Ajax"), "CC Attack", 
    tool1=getWeapon("EXP CCW"), modifiers={"Natural Born Warrior: B", "Berserk"}, burstSplit={"avatar3": 1})
testInstance.addOrder("avatar3", 1, getUnitStats("comb", "Avatar"), "CC Attack", 
    tool1=getWeapon("DA CCW"), modifiers=getUnitSpec("comb", "Avatar"), burstSplit={"ajax1": 1})

def test_tempHandleBetween_complexCc():
    assert testInstance.handleBetween("ajax1", "avatar3") == {
                "wounded": 1.56,
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

