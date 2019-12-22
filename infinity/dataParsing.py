import json


optional = {""}


class Profile:
    def __init__(self, army, isc, child):
        self.army = army.lower()[0:4]
        self.isc = isc
        self.child = child

    def getStat(self, stat):
        with open("infinityStats/" + self.army + "_units.json", "r") as read_file:
            units = json.load(read_file)
            for profile in units:
                if ("obsolete" in profile.keys()):
                    continue
                elif (profile["isc"] == self.isc):
                    return profile[stat]
            raise LookupError

    def getunitspec(self):
        specs: set = set({})
        with open("infinityStats/" + self.army + "_units.json", "r") as read_file:
            units = json.load(read_file)
            for profile in units:
                if ("obsolete" in profile):
                    continue
                elif (profile["isc"] == self.isc):
                    if "spec" in profile:
                        for spec in profile["spec"]:
                            specs.add(spec)
                    for child in profile["childs"]:
                        if child["name"] == self.child:
                            if "spec" in child:
                                for spec in child["spec"]:
                                    specs.add(spec)
        return specs


def getArmyUnits(armyname):
    unit_names = ""
    with open("infinityStats/" + armyname + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for profile in units:
            if("obsolete" in profile.keys()):
                continue
            print(profile["isc"])


def getAmmoTypes(weaponname):
    with open("infinityStats/weapons.json", "r") as read_file:
        weapons = json.load(read_file)
        for weapon in weapons:
            if(weapon["name"] == weaponname):
                return weapon["ammo"].split("+")
        raise LookupError




