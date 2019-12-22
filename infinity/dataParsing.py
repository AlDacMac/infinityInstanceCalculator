import json


optional = {"Shock Immunity", "Immunity: POS", "Total Immunity", "Sixth Sense L1", "Sixth Sense L2", "Surprise Shot L1",
            "Surprise Shot L2", "Surprise Attack", "Marksmanship L1", "Marksmanship L2", "Poison"}


def getArmyUnits(armyname):
    unit_names = ""
    with open("infinityStats/" + armyname + "_units.json", "r") as read_file:
        units = json.load(read_file)
        for profile in units:
            if("obsolete" in profile.keys()):
                continue
            print(profile["isc"])


class Profile:
    def __init__(self, army, isc, child):
        self.army = army.lower()[0:4]
        self.isc = isc
        self.child = child
        # Unit skills and equipment are divided into those that are obligatory and those that are optional
        obligs: set = set({})
        options: set = set({})
        with open("infinityStats/" + self.army + "_units.json", "r") as read_file:
            units = json.load(read_file)
            for profile in units:
                if ("obsolete" in profile):
                    continue
                elif (profile["isc"] == self.isc):
                    if "spec" in profile:
                        for spec in profile["spec"]:
                            if spec in optional:
                                options.add(spec)
                            else:
                                obligs.add(spec)
                    for child in profile["childs"]:
                        if child["name"] == self.child:
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
                elif (profile["isc"] == self.isc):
                    return profile[stat]
            raise LookupError



def getAmmoTypes(weaponname):
    with open("infinityStats/weapons.json", "r") as read_file:
        weapons = json.load(read_file)
        for weapon in weapons:
            if(weapon["name"] == weaponname):
                return weapon["ammo"].split("+")
        raise LookupError




