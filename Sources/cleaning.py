from __future__ import annotations

import io
import json
import os
import zipfile
from typing import NamedTuple

import pandas as pd
from chardet import detect
import urllib.request as request


class DataSource(NamedTuple):
    name: str
    data_location: str
    data_file_type: str
    data_file_location: str
    data_sheet_name: str | None
    data_location_z: str | None
    data_file_type_z: str | None


class Replacements(NamedTuple):
    value: str | int | float
    replacement: str | int | float


class CleaningMethod(NamedTuple):
    data_source: DataSource
    replacements: list[Replacements]
    drop_na: bool = True


with open('tempdata.json', 'r') as file:
    datta = json.load(file)

data = list(map(lambda x: DataSource(**x), datta))

for data_bite in data:
    df = pd.read_pickle(data_bite.data_file_location)
    print(data_bite.name)
    print(df.columns)
