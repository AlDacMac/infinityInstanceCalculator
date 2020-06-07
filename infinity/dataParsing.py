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


def getUnitStat(army, unitName, stat):
    with open("infinityStats/" + army.lower()[0:4] + "_units.json", "r") as read_file:
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
    with open("infinityStats/" + armyName.lower()[0:4] + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for unit in units:
            if ("obsolete" in unit.keys()):
                continue
            elif (unit["name"] == unitName):
                for stat in statNames:
                    unitStats[stat] = unit[stat]
                return unitStats
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


# TODO Fix this for all the funky no ammo weapons
def getAmmoTypes(weaponname):
    if(weaponname in {"Jammer", "Sepsitor", "Forward Observer"}):
        return weaponname
    elif(weaponname == "Sepsitor Plus"):
        return "Sepsitor"
    else:
        with open("infinityStats/weapons.json", "r") as read_file:
            weapons = json.load(read_file)
            for weapon in weapons:
                if(weapon["name"] == weaponname):
                    return weapon["ammo"].split("+")
            raise LookupError


def getWeaponBurst(weaponname):
    with open("infinityStats/weapons.json", "r") as read_file:
        weapons = json.load(read_file)
        for weapon in weapons:
            if(weapon["name"] == weaponname):
                return int(weapon["burst"])
        raise LookupError


def getWeaponAttr(weaponname):
    with open("infinityStats/weapons.json", "r") as read_file:
        weapons = json.load(read_file)
        for weapon in weapons:
            if (weapon["name"] == weaponname):
                if "attr" in weapon:
                    return weapon["attr"]
                else:
                    return "default"
        raise LookupError


def getHackingBurst(programname):
    with open("infinityStats/hacking.json", "r") as read_file:
        hacking = json.load(read_file)
        for program in hacking["Hacking Programs"]:
            if program["Name"] == programname:
                return int(program["Burst"])
