import pandas as pd
from numpy import nan


def do(paths: list[str, ...]):
    cols = ('folio', 'entidad', 'municipio', 'servicio')
    translate = {
        2015: {
            'folio': 'folio',
            'entidad': 'entidad',
            'municipio': 'municipio',
            'p1': 'servicio',
            'values': {1: True, 2: False, 0: nan}
        },
        2017: {
            'aps_folio': 'folio',
            'aps_entidad': 'entidad',
            'sa_agua_serv': 'servicio',
            'values': {0: True}
        },
        2019: {
            'folio': 'folio',
            'ag_servi': 'servicio',
            'values': {1: True, 2: False, 0: nan}
        },
        2021: {
            'folio': 'folio',
            'ag_servi': 'servicio',
            'values': {1: True, 2: False, 0: nan}
        }
    }
    db = []
    for (data_path, _), (cat_path, year) in paths:
        catalogue = pd.read_pickle(cat_path)
        c1, c2 = catalogue.columns.values
        estates = dict(zip(catalogue[c1], catalogue[c2]))
        data_v: pd.DataFrame = pd.read_pickle(data_path)
        keys = translate[year]
        data_v.columns = list(map(lambda x: keys.get(x, x), data_v.columns))
        folio = data_v.columns[0]
        data_v['entidad'] = data_v[folio].apply(lambda x: estates[int(str(x)[:-3])])
        data_v['municipio'] = data_v[folio].apply(lambda x: int(str(x)[-3:]))
        data_v['servicio'] = data_v['servicio'].apply(lambda x: keys['values'].get(x, x))
        data_v['ano'] = year
        data_v.dropna(inplace=True, axis='rows')
        data_v = data_v[[*cols]]
        db.append(data_v)
    db = pd.concat(db)
    return db


if __name__ == '__main__':
    import json
    import os

    os.chdir("../../")
    with open("data.json", 'r') as file:
        data = json.load(file)

    do(data['water_inegi'])
