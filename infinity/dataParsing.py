import json


optional = {"Shock Immunity", "Immunity: POS", "Total Immunity", "Sixth Sense L1", "Sixth Sense L2", "Surprise Shot L1",
            "Surprise Shot L2", "Surprise Attack", "Marksmanship L1", "Marksmanship L2", "Poison", "Martial Arts L1"
            , "Martial Arts L2", "Martial Arts L3", "Martial Arts L4", "Martial Arts L5"}


def getArmyUnits(armyname):
    unit_names = ""
    with open("infinityStats/" + armyname + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for profile in units:
            if("obsolete" in profile.keys()):
                continue
            print(profile["isc"])


class Unit:
    def __init__(self, army, name, child):
        self.army = army.lower()[0:4]
        self.name = name
        self.child = child

        # Unit skills and equipment are divided into those that are obligatory and those that are optional
        self.obligs: set = set({})
        self.options: set = set({})
        with open("infinityStats/" + self.army + "_units.json", "r") as read_file:
            units = json.load(read_file)
            for profile in units:
                if ("obsolete" in profile):
                    continue
                elif (profile["name"] == name):
                    if "spec" in profile:
                        for spec in profile["spec"]:
                            if spec in optional:
                                self.options.add(spec)
                            else:
                                self.obligs.add(spec)
                    for child in profile["childs"]:
                        if child["name"] == child:
                            if "spec" in child:
                                for spec in child["spec"]:
                                    if spec in optional:
                                        options.add(spec)
                                    else:
                                        obligs.add(spec)

    def getStat(self, stat):
        with open("infinityStats/" + self.army + "_units.json", "r") as read_file:
            units = json.load(read_file)
            for profile in units:
                if ("obsolete" in profile.keys()):
                    continue
                elif (profile["name"] == self.name):
                    return profile[stat]
            raise LookupError



def getAmmoTypes(weaponname):
    with open("infinityStats/weapons.json", "r") as read_file:
        weapons = json.load(read_file)
        for weapon in weapons:
            if(weapon["name"] == weaponname):
                return weapon["ammo"].split("+")
        raise LookupError




