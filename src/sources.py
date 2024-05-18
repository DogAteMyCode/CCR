from __future__ import annotations

import io
import json
import os
import zipfile
from typing import NamedTuple

import pandas as pd
import geopandas as gpd
from chardet import detect
import urllib.request as request


def read_csv_file(file_s: str) -> pd.DataFrame:
    df = pd.read_csv(file_s)
    return df


def read_csv_file_bytes(file_s: io.BytesIO, encoding) -> pd.DataFrame:
    df = pd.read_csv(file_s, encoding=encoding)
    return df


def read_xlsx_file(file_s: str | io.BytesIO) -> dict[str, pd.DataFrame]:
    ef = pd.ExcelFile(file_s)
    return {key: df for key, df in [(sn, ef.parse(sn)) for sn in ef.sheet_names]}


def read_zip_file(file_s: str) -> zipfile.ZipFile:
    req = request.urlopen(file_s)
    myzip = zipfile.ZipFile(io.BytesIO(req.read()))
    return myzip


def multiline_input(prompt: str) -> list[str]:
    out = []
    while True:
        print("To finish enter ;")
        inp = input(prompt)
        if inp == ";":
            break
        out.append(inp)
    return out


class DataSource(NamedTuple):
    name: str
    data_location: str
    data_file_type: str
    data_sheet_name: str | None
    data_location_z: str | None
    data_file_type_z: str | None
    data_file_location: str | None = None


def read_data_source(data_source: DataSource) -> pd.DataFrame | gpd.GeoDataFrame:
    try:
        db = pd.read_pickle(data_source.data_file_location)
        return db
    except FileNotFoundError:
        if not os.path.isdir('TempData'):
            os.mkdir('TempData')
        if data_source.data_file_type == "xlsx":
            excel_file = read_xlsx_file(data_source.data_location)
            db = excel_file[data_source.data_sheet_name]
            db.to_pickle(data_source.data_file_location)
            return db

        elif data_source.data_file_type == "csv":
            db = read_csv_file(data_source.data_location)
            db.to_pickle(data_source.data_file_location)
            return db

        elif data_source.data_file_type == "geojson":
            db = gpd.read_file(data_source.data_location)
            db.to_pickle(data_source.data_file_location)
            return db

        if data_source.data_file_type == "zip":
            zip_data_ = read_zip_file(data_source.data_location)
            file_data = io.BytesIO(zip_data_.read(data_source.data_location_z))

            if data_source.data_file_type_z == "xlsx":
                excel_file = read_xlsx_file(file_data)
                db = excel_file[data_source.data_sheet_name]
                db.to_pickle(data_source.data_file_location)
                return db

            elif data_source.data_file_type_z == "csv":
                metadata = detect(zip_data_.read(data_source.data_location_z))
                db = read_csv_file_bytes(file_data, metadata['encoding'])
                db.to_pickle(data_source.data_file_location)
                return db

            elif data_source.data_file_type_z == "geojson":
                if data_source.data_file_type_z.endswith('.shp'):
                    os.mkdir('temp')
                    tempPathP = os.path.join('temp', data_source.data_location_z)
                    zip_data_.extractall('temp')
                    db = gpd.read_file(tempPathP)
                else:
                    os.mkdir('temp')
                    tempPathP = os.path.join('temp', data_source.data_location_z.split('/')[-1])

                    with open(tempPathP, 'xb') as f:
                        f.write(file.getbuffer().tobytes())
                    db = gpd.read_file(tempPathP)
                db.to_pickle(data_source.data_file_location)
                return db


if __name__ == "__main__":
    locations = multiline_input("Enter file url: ")
    file_types = []

    for location in locations:
        if location.endswith('.zip'):
            file_types.append('zip')
        elif location.endswith('.csv'):
            file_types.append('csv')
        elif location.endswith('.xlsx') or location.endswith('.xls') or location.endswith('xlsb'):
            file_types.append('xlsx')
        elif location.endswith('json') or location.endswith('.geojson') or location.endswith('.shp'):
            file_types.append('geojson')

    data: list[DataSource] = list()
    data_frames: list[pd.DataFrame] = list()

    for location, file_type in zip(locations, file_types):
        print(location)
        if file_type == "xlsx":
            ef = read_xlsx_file(location)
            print("sheets, ", ef.keys())
            keys_to_use = input("Enter sheets to use (comma separated): ").split(',')
            names_to_use = input("Enter names to use (comma separated): ").split(',')
            for key, name in zip(keys_to_use, names_to_use):
                df = ef[key]
                ds = DataSource(name, location, 'xlsx', key, None, None)
                data_frames.append(df)
                data.append(ds)

        elif file_type == "csv":
            name_to_use = input("Enter name to use: ")
            df = read_csv_file(location)
            ds = DataSource(name_to_use, location, 'csv', None, None, None)
            data_frames.append(df)
            data.append(ds)

        elif file_type == "geojson":
            name_to_use = input("Enter name to use: ")
            df = gpd.read_file(location)
            ds = DataSource(name_to_use, location, 'geojson', None, None, None)
            data_frames.append(df)
            data.append(ds)

        if file_type == "zip":
            zip_data = read_zip_file(location)
            files = zip_data.namelist()
            locations_zip = multiline_input(f"{str(files)}\nEnter locations: ")
            file_types_zip = []
            for location_z in locations_zip:
                print(location_z)
                if location_z.endswith('.csv'):
                    file_types_zip.append('csv')
                elif location_z.endswith('.xlsx') or location.endswith('.xls') or location.endswith('xlsb'):
                    file_types_zip.append('xlsx')
                elif location_z.endswith('json') or location_z.endswith('.geojson') or location_z.endswith('.shp'):
                    file_types_zip.append('geojson')
            for location_z, file_type_z in zip(locations_zip, file_types_zip):
                file = io.BytesIO(zip_data.read(location_z))
                print(location_z)
                if file_type_z == "xlsx":
                    ef = read_xlsx_file(file)
                    print("sheets, ", ef.keys())
                    keys_to_use = input("Enter sheets to use (comma separated): ").split(',')
                    names_to_use = input("Enter names to use (comma separated): ").split(',')
                    for key, name in zip(keys_to_use, names_to_use):
                        df = ef[key]
                        ds = DataSource(name, location, 'zip', key, location_z, 'xlsx')
                        data_frames.append(df)
                        data.append(ds)

                elif file_type_z == "csv":
                    name_to_use = input("Enter name to use: ")
                    meta = detect(zip_data.read(location_z))
                    df = read_csv_file_bytes(file, meta['encoding'])
                    ds = DataSource(name_to_use, location, 'zip', None, location_z, 'csv')
                    data_frames.append(df)
                    data.append(ds)

                elif file_type_z == "geojson":
                    name_to_use = input("Enter name to use: ")
                    if location_z.endswith('.shp'):
                        os.mkdir('temp')
                        tempPath = os.path.join('temp', location_z)
                        zip_data.extractall('temp')
                        df = gpd.read_file(tempPath)
                    else:
                        os.mkdir('temp')
                        tempPath = os.path.join('temp', location_z.split('/')[-1])

                        with open(tempPath, 'xb') as f:
                            f.write(file.getbuffer().tobytes())
                        df = gpd.read_file(tempPath)
                    import shutil
                    shutil.rmtree('temp')
                    ds = DataSource(name_to_use, location, 'csv', None, location_z, 'geojson')
                    data_frames.append(df)
                    data.append(ds)

    data_dict = [d._asdict() for d in data]

    if not os.path.isdir('Test'):
        os.mkdir('Test')
    for dictionary, data_frame in zip(data_dict, data_frames):
        if dictionary['data_file_type_z'] is not None:
            path = os.path.join('Test',
                                f'{dictionary["name"]}-{hash(DataSource(**dictionary))}-{dictionary["data_file_type_z"]}.pkl')
        else:
            path = os.path.join('Test',
                                f'{dictionary["name"]}-{hash(DataSource(**dictionary))}-{dictionary["data_file_type"]}.pkl')
        dictionary['data_file_location'] = path
        data_frame.to_pickle(path)

    with open("tempdata.json", 'r', encoding='utf-8') as f:
        temp_data = json.load(f)

    with open("tempdata.json", 'w', encoding='utf-8') as f:
        json.dump(data_dict + temp_data, f)
