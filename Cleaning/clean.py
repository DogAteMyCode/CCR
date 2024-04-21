import json
import os
from inegi_water.clean import do as water_inegi_do

if __name__ == '__main__':
    os.chdir("../")

with open("Cleaning/data.json", 'r') as file:
    data = json.load(file)

water_inegi_do(data['water_inegi'])



