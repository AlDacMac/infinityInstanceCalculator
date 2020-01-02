import json


optional = {"Shock Immunity", "Immunity: POS", "Total Immunity", "Sixth Sense L1", "Sixth Sense L2", "Surprise Shot L1",
            "Surprise Shot L2", "Surprise Attack", "Marksmanship L1", "Marksmanship L2", "Poison", "Martial Arts L1"
            , "Martial Arts L2", "Martial Arts L3", "Martial Arts L4", "Martial Arts L5"}


def getArmyUnits(armyname):
    unit_names = []
    with open("infinityStats/" + armyname.lower()[0:4] + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for profile in units:
            if("obsolete" in profile.keys()):
                continue
            # print(profile["name"])
            unit_names.append(profile["name"])
    return unit_names


def getAmmoTypes(weaponname):
    with open("infinityStats/weapons.json", "r") as read_file:
        weapons = json.load(read_file)
        for weapon in weapons:
            if(weapon["name"] == weaponname):
                return weapon["ammo"].split("+")
        raise LookupError


def getUnitStat(armyname, unitname, stat):
    with open("infinityStats/" + armyname.lower()[0:4] + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for profile in units:
            if ("obsolete" in profile.keys()):
                continue
            elif (profile["name"] == unitname):
                return profile[stat]
        raise LookupError


def populateUnitSpec(armyname, unitname, obligs, options):
    with open("infinityStats/" + armyname.lower()[0:4] + "_units.json", "r") as read_file:
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
