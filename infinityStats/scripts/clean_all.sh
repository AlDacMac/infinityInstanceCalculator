#!/bin/bash

# immediately exit on an error
set -e

for i in ../*_units.json; do
    echo "Cleaning $i"
    ./clean_json.py $i
done

for i in ../*_army.json; do
    echo "Cleaning $i"
    ./clean_json.py $i
done

echo "Cleaning ../weapons.json"
./clean_weapons.py ../weapons.json
