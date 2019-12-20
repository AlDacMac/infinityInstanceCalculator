import json

with open("infinityStats/alep_units.json", "r") as read_file:
   data = json.load(read_file)



def getArmyUnits(armyname):
    unit_names = ""
    with open("infinityStats/" + armyname + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for profile in units:
            if("obsolete" in profile.keys()):
                continue
            print(profile["isc"])


def getUnitBS(armyname, unitname):
    with open("infinityStats/" + armyname + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for profile in units:
            if ("obsolete" in profile.keys()):
                continue
            elif(profile["isc"] == unitname):
                return profile["bs"]
        raise LookupError


def getAmmoTypes(weaponname):
    with open("infinityStats/weapons.json", "r") as read_file:
        weapons = json.load(read_file)
        for weapon in weapons:
            if(weapon["name"] == weaponname):
                return weapon["ammo"].split("+")
        raise LookupError
