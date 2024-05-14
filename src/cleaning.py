from __future__ import annotations

import io
import json
import os
import zipfile
from typing import NamedTuple
from sources import multiline_input

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


def multiline_input_replacements(prompt: str) -> list[Replacements]:
    out = []
    while True:
        print("To finish enter ;")
        inp = input(prompt)
        if inp == ";":
            break

        out.append(Replacements(*inp.split(',')))
    return out


class CleaningMethod(NamedTuple):
    data_source: DataSource
    replacements: list[Replacements]
    columns: list[Replacements]
    drop_na: bool = True


with open('tempdata.json', 'r') as file:
    datta = json.load(file)

data = list(map(lambda x: DataSource(**x), datta))

for data_bite in data:
    df = pd.read_pickle(data_bite.data_file_location)
    print(data_bite.name)
    print(df.columns)
    cols = multiline_input_replacements('Columns to use and their new name separated by comma\n'
                                        'to exclude column, don\'t include it in the list\n'
                                        ' (column name,new column name): ')
    cols = dict(cols)
    df = df.rename(columns=cols)
    df = df[cols.values()]
    for col in df.columns:
        print(col)
        print('Unique values are', df[col].unique())
        val_to_drop = multiline_input('Values to drop: ')
        df.drop(df[df[col].astype(str).isin(val_to_drop)].index, inplace=True)

    print(df)
