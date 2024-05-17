from __future__ import annotations

import io
import json
import os
import sys
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
        try:
            out.append(Replacements(*inp.split(',')))
        except TypeError:
            print(f"Not enough parameters {inp.split(',')}", file=sys.stderr)
    return out


class CleaningMethod(NamedTuple):
    data_source: DataSource | dict[str, str | None]
    col_values_to_drop: dict[str, list[str]]
    columns: list[Replacements] | dict[str, str]
    drop_na: bool = True


if __name__ == "__main__":
    with open('tempdata.json', 'r') as file:
        datta = json.load(file)

    data = list(map(lambda x: DataSource(**x), datta))

    cleaning_methods = dict()

    try:
        with open('cleaning.json', 'r', encoding='utf-8') as file:
            miau = json.load(file)
    except FileNotFoundError:
        miau = dict()

    for data_bite in data:

        df = pd.read_pickle(data_bite.data_file_location)
        print(data_bite.name)
        print(df.columns)
        print(miau.get(data_bite.data_file_location, []))

        skip = input('skip (y, n): ') in ['y', 'Y']
        if skip:
            continue
        cols = multiline_input_replacements('Columns to use and their new name separated by comma\n'
                                            'to exclude column, don\'t include it in the list\n'
                                            ' (column name,new column name): ')
        cols = dict(cols)
        df = df.rename(columns=cols)
        df = df[cols.values()]
        droppity = dict()
        for col in df.columns:
            print(col)
            print('Unique values are', df[col].unique())
            val_to_drop = multiline_input('Values to drop: ')
            droppity[col] = val_to_drop
            df.drop(df[df[col].astype(str).isin(val_to_drop)].index, inplace=True)

        drop_na = input("Drop na (y, n): ") in ['y', 'Y']
        if drop_na:
            df.dropna(axis='index', inplace=True)
        print(df)

        cleaning_methods[data_bite.data_file_location] = CleaningMethod(data_bite._asdict(), droppity, cols,
                                                                        drop_na)._asdict()

    miau.update(cleaning_methods)
    for k in miau.keys():
        if isinstance(miau[k]['data_source'], list):
            miau[k]['data_source'] = DataSource(*miau[k]['data_source'])._asdict()
    with open('cleaning.json', 'w', encoding='utf-8') as file:
        json.dump(miau, file)
