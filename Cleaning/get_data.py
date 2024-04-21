import json
import pandas as pd
import zipfile
import io
import urllib.request as request
import os
import pickle
from chardet import detect


def read_data(data_url: str, data_type: tuple[str, ...], locs: list[str]) -> pd.DataFrame | pd.ExcelFile:
    if 'zip' in data_type:
        if not locs:
            raise ValueError(f"{data_url} is zip, but no data file specified")
        req = request.urlopen(data_url)
        myzip = zipfile.ZipFile(io.BytesIO(req.read()))
        files = myzip.namelist()
        for loc in locs:
            if loc not in files:
                raise ValueError(f"{loc} not in {files}")
            file = io.BytesIO(myzip.read(loc))
            data_url = file

            if 'xlsx' in data_type:
                ef = pd.ExcelFile(data_url)
                yield ef
            if 'csv' in data_type:
                meta = detect(myzip.read(loc))
                df = pd.read_csv(data_url, encoding=meta['encoding'])
                yield df
        return
    if 'xlsx' in data_type:
        ef = pd.ExcelFile(data_url)
        yield ef
    if 'csv' in data_type:
        df = pd.read_csv(data_url)

        yield df


os.chdir("../")
wcd = os.getcwd()

data_folder = os.path.join(wcd, "Data")

# read json file

with open("sources.json") as f:
    to_import = json.load(f)

data = to_import.keys()

# create data folder
if not os.path.isdir(data_folder):
    print("Creating data folder")
    os.mkdir(data_folder)

# store data location

store = dict()

# read urls

for d in data:
    sources = to_import[d].keys()
    path = os.path.join(data_folder, d)
    if not os.path.isdir(path):
        os.mkdir(os.path.join(path))
    for source in sources:
        store[f"{d}_{source}"] = []
        s_path = os.path.join(path, source)
        if not os.path.isdir(os.path.join(s_path)):
            os.mkdir(s_path)
        values = to_import[d][source]["data"]
        for value in values:
            v_type = value['type']
            year = value['year']
            url = value['url']
            temp = []
            location = value.get('data', [])
            df_efs = read_data(url, v_type, location)
            for df_ef, name in zip(df_efs, value['name']):
                if 'xlsx' in v_type:
                    xl_path = os.path.join(s_path, f"{name}")
                    if not os.path.isdir(xl_path):
                        os.mkdir(xl_path)
                    sheets = df_ef.sheet_names
                    for sheet in sheets:
                        file_name = os.path.join(xl_path, f"{sheet}.pkl")
                        temp.append((file_name, year))
                        with open(file_name, "wb") as file:
                            pickle.dump(df_ef.parse(sheet), file)
                if 'csv' in v_type:
                    file_name = os.path.join(s_path, f"{name}.pkl")
                    temp.append((file_name, year))
                    with open(file_name, "wb") as file:
                        pickle.dump(df_ef, file)
            store[f"{d}_{source}"].append(temp)

with open("data.json", "w") as file:
    json.dump(store, file)
