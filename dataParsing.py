import json
import re


optional = {"Shock Immunity", "Immunity: POS", "Total Immunity", "Sixth Sense L1", "Sixth Sense L2", "Surprise Shot L1",
            "Surprise Shot L2", "Surprise Attack", "Marksmanship L1", "Marksmanship L2", "Poison", "Martial Arts L1"
            , "Martial Arts L2", "Martial Arts L3", "Martial Arts L4", "Martial Arts L5"}
sepecialweapons = {
    "Sepsitor":  {
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
    },
    "Sepsitor Plus": {
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
        "note": "Intuitive Attack"
    }, 
    "Jammer": {
        "name": "Jammer",
        "burst": "1",
        "ammo": "Jammer",
        "damage": "13",
        "short_dist": "--",
        "short_mod": "--",
        "medium_dist": "--",
        "medium_mod": "--",
        "long_dist": "--",
        "long_mod": "--",
        "max_dist": "--",
        "max_mod": "--",
        "cc": "No",
        "template": "No",
        "note": "Comms Attack, Intuitive Attack, No LoF, State: Isolated, Technical Weapon, Zone of Control"
    },
    "Forward Observer": {
        "name": "Forward Observer",
        "burst": "1",
        "ammo": "Forward Observer",
        "damage": "N/A",
        "short_dist": "8",
        "short_mod": "0",
        "medium_dist": "24",
        "medium_mod": "0",
        "long_dist": "48",
        "long_mod": "-3",
        "max_dist": "96",
        "max_mod": "-6",
        "cc": "No",
        "template": "No",
        "note": "Non-Lethal, Non-Lootable, Technical Weapon"
    }
}

def getArmyUnits(armyname):
    unit_names = []
    with open("unit_data/" + armyname.lower()[0:4] + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for profile in units:
            if("obsolete" in profile.keys()):
                continue
            # print(profile["name"])
            unit_names.append(profile["name"])
    return unit_names


def getUnitStat(army, unitName, stat):
    with open("unit_data/" + army.lower()[0:4] + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for profile in units:
            if ("obsolete" in profile.keys()):
                continue
            elif (profile["name"] == unitName):
                return profile[stat.lower()]
        raise LookupError


def getUnitStats(armyName, unitName):
    statNames = ["cc", "bs", "ph", "wip", "arm", "bts", "w"]
    unitStats = dict({})
    with open("unit_data/" + armyName.lower()[0:4] + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for unit in units:
            if ("obsolete" in unit.keys()):
                continue
            elif (unit["name"] == unitName):
                for stat in statNames:
                    unitStats[stat] = unit[stat]
                return unitStats
        raise LookupError


# To specify child x of unit y, input y: x for unitname (e.g Achilles: Spitfire)
# To specify profile x of unit y, input x (y) for unitname (e.g Auxbot (Peacemaker))
# TODO Implement some way of setting "default" profiles, for example not having to specify
#   "Myrmidon: Assault Hacker" if you want to get the one with the hacking device
def getUnitSpec(armyname, unitname):
    spec = set({})
    childname = None
    profilename = None
    if ": " in unitname:
        [unitname, childname] = unitname.split(": ")
    elif "(" in unitname:
        [profilename, unitname, X] = re.split(r'\s\(|\)', unitname)    #X here is just a discarded ")"
    with open("unit_data/" + armyname.lower()[0:4] + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for unit in units:
            if ("obsolete" in unit):
                continue
            elif unit["name"] == unitname:
                spec = spec|set(unit["spec"])
                if childname:
                    for child in unit["childs"]:
                        if child["name"] == childname:
                            spec = spec|set(child["spec"])
                if "profiles" in unit:
                    for profile in unit["profiles"]:
                        if profile["id"] == 1:
                            if profilename == None:
                                spec = spec|set(profile["spec"])
                            else:
                                continue
                        elif profile["name"] == profilename:
                            spec = spec|set(profile["spec"])
                    
    return spec


# Takes a weapon name, and returns the weapon data dictionary from unit_data/weapons.json
def getWeapon(weaponname):
    if(weaponname in {"Jammer", "Sepsitor", "Sepsitor Plus", "Forward Observer"}):
        return sepecialweapons["weaponname"]
    else: 
        with open("unit_data/weapons.json", "r") as read_file:
            weapons = json.load(read_file)
            for weapon in weapons:
                if(weapon["name"] == weaponname):
                    return weapon
            raise LookupError


# DEPRECATED
def populateUnitSpec(armyname, unitname, obligs, options):
    with open("unit_data/" + armyname.lower()[0:4] + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for profile in units:
            if ("obsolete" in profile):
                continue
            elif (profile["name"] == unitname):
                if "spec" in profile:
                    for spec in profile["spec"]:
                        if spec in optional:
                            options.add(spec)
                        else:
                            obligs.add(spec)
                for child in profile["childs"]:
                    if child["name"] == child:
                        if "spec" in child:
                            for spec in child["spec"]:
                                if spec in optional:
                                    options.add(spec)
                                else:
                                    obligs.add(spec)


# TODO Fix this for all the funky no ammo weapons
def getAmmoTypes(weaponname):
    if(weaponname in {"Jammer", "Sepsitor", "Forward Observer"}):
        return weaponname
    elif(weaponname == "Sepsitor Plus"):
        return "Sepsitor"
    else:
        with open("unit_data/weapons.json", "r") as read_file:
            weapons = json.load(read_file)
            for weapon in weapons:
                if(weapon["name"] == weaponname):
                    return weapon["ammo"].split("+")
            raise LookupError


def getWeaponBurst(weaponname):
    with open("unit_data/weapons.json", "r") as read_file:
        weapons = json.load(read_file)
        for weapon in weapons:
            if(weapon["name"] == weaponname):
                return int(weapon["burst"])
        raise LookupError


def getWeaponAttr(weaponname):
    with open("unit_data/weapons.json", "r") as read_file:
        weapons = json.load(read_file)
        for weapon in weapons:
            if (weapon["name"] == weaponname):
                if "attr" in weapon:
                    return weapon["attr"]
                else:
                    return "default"
        raise LookupError


def getHackingBurst(programname):
    with open("unit_data/hacking.json", "r") as read_file:
        hacking = json.load(read_file)
        for program in hacking["Hacking Programs"]:
            if program["Name"] == programname:
                return int(program["Burst"])
