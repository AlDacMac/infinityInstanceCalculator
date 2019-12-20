#!/usr/bin/env python
"""This script moves weapons from the base profile of units into the childs."""

import sys
import simplejson as json
from collections import OrderedDict

def inherits_from_childs(profile):
    # If the profile is tagged as independent, it inherits nothing
    if "independent" in profile:
        return False

    # Seed-Embryos inherit nothing
    if "Seed-Embryo" in profile["spec"]:
        return False

    # TAG pilots inherit nothing from their base
    if "Pilot" in profile["spec"]:
        return False

    # CrazyKoalas are just equipment
    if profile["name"] == "CrazyKoala":
        return False

    # All others inherit base weapons
    return True

if len(sys.argv) != 2:
    print "Usage: ", sys.argv[0], " <input file>";
    sys.exit(1)

filename = sys.argv[1]

print "Reading from: " + filename
with open(filename, "r") as f:
    data = json.load(f, object_pairs_hook=OrderedDict)
     
for unit in data:
    print unit["name"]

    if "ccw" in unit:
        base_ccw = unit["ccw"]
        del unit["ccw"]
    else:
        base_ccw = []

    if "bsw" in unit:
        base_bsw = unit["bsw"]
        del unit["bsw"]
    else:
        base_bsw = []

    if "profiles" in unit:
        # Collect set of weapons that the main profile shares with all non-
        # independent profiles.
        main_profile = unit["profiles"][0]
        print "  ", main_profile.get("name", unit["name"])

        profile_ccw = main_profile.get("ccw", [])
        main_profile["ccw"] = []

        profile_bsw = main_profile.get("bsw", [])
        main_profile["bsw"] = []

        for alt_profile in unit["profiles"][1:]:
            print "  ", alt_profile["name"]
            if inherits_from_childs(alt_profile):
                # remove any weapons from profile_* not shared by this profile
                alt_ccw = alt_profile.get("ccw", [])
                main_ccw = []
                for ccw in profile_ccw:
                    if ccw in alt_ccw:
                        # Both share this weapon
                        alt_ccw.remove(ccw)
                    else:
                        # This is in the main profile only
                        main_ccw.append(ccw)
                # Put any main-profile-only weapons back in the main profile
                for ccw in main_ccw:
                    main_profile["ccw"].append(ccw)
                    profile_ccw.remove(ccw)

                # remove any weapons from profile_* not shared by this profile
                alt_bsw = alt_profile.get("bsw", [])
                main_bsw = []
                for bsw in profile_bsw:
                    if bsw in alt_bsw:
                        # Both share this weapon
                        alt_bsw.remove(bsw)
                    else:
                        # This is in the main profile only
                        main_bsw.append(bsw)
                # Put any main-profile-only weapons back in the main profile
                for bsw in main_bsw:
                    main_profile["bsw"].append(bsw)
                    profile_bsw.remove(bsw)

            else:
                # apply the base weapons
                alt_ccw = alt_profile.get("ccw", [])
                alt_profile["ccw"] = base_ccw + alt_ccw

                alt_bsw = alt_profile.get("bsw", [])
                alt_profile["bsw"] = base_bsw + alt_bsw
    else:
        profile_ccw = []
        profile_bsw = []

    # apply to every child
    for child in unit["childs"]:
        child_ccw = child.get("ccw", [])
        child["ccw"] = base_ccw + profile_ccw + child_ccw

        child_bsw = child.get("bsw", [])
        child["bsw"] = base_bsw + profile_bsw + child_bsw

print "Writing to: " + filename
with open(filename, "w") as outfile:
    json.dump(data, outfile, indent=2, separators=(",", ": "))


