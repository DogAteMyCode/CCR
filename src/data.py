import json
import os.path

import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from unidecode import unidecode
from cleaning import CleaningMethod, DataSource
from sources import read_data_source


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
        db = read_data_source(source.data_source)

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
    print(data)
    if not os.path.isdir('figures'):
        os.mkdir('figures')
    # db_data: gpd.GeoDataFrame = data['factibilidad hidrica']
    # print(db_data.geometry)
    # db_data['n_id'] = range(len(db_data))
    #
    # fig = px.choropleth_mapbox(data_frame=db_data, geojson=db_data.geometry,
    #                            locations='n_id', featureidkey='id',
    #                            color='factibilidad hidrica',
    #                            color_discrete_sequence=['red', 'yellow', 'orange', 'green'],
    #                            mapbox_style="carto-positron",
    #                            opacity=0.5, center={"lat": 19.3657, "lon": -99.1318}, zoom=9.3,
    #                            hover_data=['delegacion'], title='Factibilidad hídrica en la ciudad de méxico')
    # fig.update_geos(fitbounds="locations")
    # # fig.show()

    # fig.write_image('figures/factibilidad_hidrica.png', width=650, height=650, scale=15, engine='orca')
    # del db_data

    # db_data = data['consumo']
    # geo_data = gpd.read_file('alcaldias.json')
    # mapping = dict(zip(tuple(map(lambda x: unidecode(x.lower()), geo_data['NOMGEO'])), geo_data['NOMGEO']))
    # db_data['alcaldia'] = tuple(map(lambda x: mapping[unidecode(x.lower())], db_data['alcaldia']))
    # # for i in sorted(db_data['frequency'].unique()):
    # month_freq = db_data.groupby('alcaldia')[['suma de consumo por colonia en m3 bimestral', 'promedio de consumo por colonia en m3 bimestral', 'promedio por numero de viviendas']].mean()
    # geo_data.rename(columns={'NOMGEO': 'alcaldia'}, inplace=True)
    # merge = pd.merge(geo_data, month_freq, on=['alcaldia'])
    #
    # merge['n_id'] = range(len(merge))
    #
    #
    # fig = px.choropleth_mapbox(data_frame=merge, geojson=merge.geometry,
    #                            locations='n_id',
    #                            featureidkey='id',
    #                            color='promedio por numero de viviendas',
    #                            mapbox_style="carto-positron",
    #                            opacity=0.5,
    #                            center={"lat": 19.3457, "lon": -99.1318}, zoom=8.5,
    #                            title=f'Promedio de consumo de agua en m3 bimestral por vivienda'
    #                            )
    #
    # fig.write_image('figures/consumo.png', width=650, height=650, scale=15, engine='orca')
    # del db_data

    db_data = data['violencia por colonia']
    db_data['n_id'] = range(len(db_data))

    print(db_data.columns)

    fig = px.choropleth_mapbox(data_frame=db_data, geojson=db_data.geometry,
                               locations='n_id', featureidkey='id',
                               color='marginalidad y violencia',
                               mapbox_style="carto-positron",
                               opacity=0.5, center={"lat": 19.3657, "lon": -99.1318}, zoom=9.0,
                               hover_data=['alcaldia', 'colonia'], title='Violencia en la ciudad de méxico')
    fig.update_geos(fitbounds="locations")
    # fig.show()

    fig.write_image('figures/violencia.png', width=650, height=650, scale=15, engine='orca')

