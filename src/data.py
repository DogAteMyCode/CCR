import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from cleaning import CleaningMethod, DataSource


class Data:
    clean_sources: dict[str, CleaningMethod]
    keys: tuple
    names: tuple

    def __init__(self, file: str):
        with open(file, 'r') as f:
            clean_sources = json.load(f)
        self.keys = tuple(clean_sources.keys())
        names = []
        for key in self.keys:
            clean_sources[key]["data_source"] = DataSource(**clean_sources[key]["data_source"])
            clean_sources[key] = CleaningMethod(**clean_sources[key])
            names.append(clean_sources[key].data_source.name)

        self.clean_sources = clean_sources
        self.names = tuple(names)

    def __getitem__(self, item):
        ind = self.names.index(item)
        key = self.keys[ind]
        return self.get_db(key)

    def get_db(self, key):
        source = self.clean_sources[key]
        db = pd.read_pickle(source.data_source.data_file_location)
        cols = source.columns
        db = db.rename(columns=cols)
        db = db[cols.values()]
        for col, drop in source.col_values_to_drop.items():
            db.drop(db[db[col].astype(str).isin(drop)].index, inplace=True)

        if source.drop_na:
            db.dropna(axis='index', inplace=True)

        return db

    def __str__(self):
        return str(self.names)

    def __repr__(self):
        return str(self.names)


if __name__ == '__main__':
    data = Data('cleaning.json')
    print(data['consumo'])
    print(data)
