import os
import pandas as pd
import geopandas as gpd
import plotly.express as px
from unidecode import unidecode
from data import Data
import json
import warnings
import zipfile

data = Data('cleaning.json')

if not os.path.isdir('figures'):
    os.mkdir('figures')
db_data: gpd.GeoDataFrame = data['factibilidad hidrica']
db_data['n_id'] = range(len(db_data))

db_data['colonia'] = db_data.nombre

fig_factibilidad = px.choropleth_mapbox(data_frame=db_data, geojson=db_data.geometry,
                                        locations='n_id', featureidkey='id',
                                        color='factibilidad hidrica',
                                        color_discrete_sequence=['red', 'yellow', 'orange', 'green'],
                                        mapbox_style="carto-darkmatter",
                                        opacity=0.5, center={"lat": 19.3657, "lon": -99.1318}, zoom=8.8,
                                        hover_data=['delegacion', 'colonia'],
                                        title='Factibilidad hídrica en la ciudad de méxico',
                                        template='cerulean+plotly_dark',
                                        height=500,
                                        )
fig_factibilidad.update_geos(fitbounds="locations")
# fig_factibilidad.show()

# fig_factibilidad.write_image('figures/factibilidad_hidrica.png', width=650, height=650, scale=15, engine='orca')
del db_data

db_data = data['consumo']
geo_data = gpd.read_file('alcaldias.json')
mapping = dict(zip(tuple(map(lambda x: unidecode(x.lower()), geo_data['NOMGEO'])), geo_data['NOMGEO']))
db_data['alcaldia'] = tuple(map(lambda x: mapping[unidecode(x.lower())], db_data['alcaldia']))
# for i in sorted(db_data['frequency'].unique()):
month_freq = db_data.groupby('alcaldia')[
    ['suma de consumo por colonia en m3 bimestral', 'promedio de consumo por colonia en m3 bimestral',
     'promedio por numero de viviendas']].mean()
geo_data.rename(columns={'NOMGEO': 'alcaldia'}, inplace=True)
merge = pd.merge(geo_data, month_freq, on=['alcaldia'])

merge['n_id'] = range(len(merge))

fig_consumo = px.choropleth_mapbox(data_frame=merge, geojson=merge.geometry,
                                   locations='n_id',
                                   featureidkey='id',
                                   color='promedio por numero de viviendas',
                                   mapbox_style="carto-darkmatter",
                                   opacity=0.5,
                                   center={"lat": 19.3357, "lon": -99.1318}, zoom=8.5,
                                   title=f'Promedio de consumo de agua en m3 bimestral por vivienda',
                                   template='cerulean+plotly_dark',
                                   height=500,
                                   hover_data=['alcaldia']
                                   )

# fig_consumo.write_image('figures/consumo.png', width=650, height=650, scale=15, engine='orca')
del db_data

db_data = data['violencia por colonia']
db_data['n_id'] = range(len(db_data))

fig_violencia = px.choropleth_mapbox(data_frame=db_data, geojson=db_data.geometry,
                                     locations='n_id', featureidkey='id',
                                     color='marginalidad y violencia',
                                     color_continuous_scale='jet',
                                     mapbox_style="carto-darkmatter",
                                     opacity=0.5, center={"lat": 19.3657, "lon": -99.1318}, zoom=9,
                                     hover_data=['alcaldia', 'colonia'], title='Violencia en la ciudad de méxico',
                                     template='cerulean+plotly_dark',
                                     height=1000, width=600)
fig_violencia.update_geos(fitbounds="locations")
# fig.show()

# fig_violencia.write_image('figures/violencia.png', width=650, height=650, scale=15, engine='orca')
del db_data

#######################################################################################################################

# Ignorar warnings
warnings.filterwarnings('ignore')

# Leer el archivo JSON
with zipfile.ZipFile('contaminantes_2022.zip') as f:
    data_contaminantes = json.loads(f.read('contaminantes_2022.json'))

# Cargar el archivo GeoJSON de la Ciudad de México
with open('alcaldias_cdmx.json', encoding='utf-8') as file:
    cdmx_geojson = json.load(file)

# Añadir coordenadas geográficas para las estaciones
station_coords = {
    "AJU": {'lat': 19.154286, 'lon': -99.162611},  # Ajusco
    "AJM": {'lat': 19.272161, 'lon': -99.207744},  # Ajusco Medio
    "BJU": {'lat': 19.370464, 'lon': -99.159596},  # Benito Juárez
    "CAM": {'lat': 19.468404, 'lon': -99.169794},  # Camarones
    "COY": {'lat': 19.350258, 'lon': -99.157101},  # Coyoacán
    "CCA": {'lat': 19.326111, 'lon': -99.176111},  # Centro de Ciencias de la Atmósfera
    "CUA": {'lat': 19.365313, 'lon': -99.291705},  # Cuajimalpa
    "FAC": {'lat': 19.482473, 'lon': -99.243524},  # FES Acatlán
    "FAR": {'lat': 19.473692, 'lon': -99.046176},  # FES Aragón
    "GAM": {'lat': 19.4827, 'lon': -99.094517},  # Gustavo A. Madero
    "HGM": {'lat': 19.411617, 'lon': -99.152207},  # Hospital General de México
    "INN": {'lat': 19.291968, 'lon': -99.38052},  # Investigaciones Nucleares
    "IZT": {'lat': 19.384413, 'lon': -99.117641},  # Iztacalco
    "LPR": {'lat': 19.534727, 'lon': -99.11772},  # La Presa
    "LOM": {'lat': 19.403, 'lon': -99.242062},  # Lomas
    "LLA": {'lat': 19.578792, 'lon': -99.039644},  # Los Laureles
    "MER": {'lat': 19.42461, 'lon': -99.119594},  # Merced
    "MGH": {'lat': 19.40405, 'lon': -99.20266},  # Miguel Hidalgo
    "MPA": {'lat': 19.1769, 'lon': -98.990189},  # Milpa Alta
    "NEZ": {'lat': 19.393734, 'lon': -99.028212},  # Nezahualcóyotl
    "PED": {'lat': 19.325146, 'lon': -99.204136},  # Pedregal
    "SAG": {'lat': 19.532968, 'lon': -99.030324},  # San Agustín
    "SFE": {'lat': 19.357357, 'lon': -99.262865},  # Santa Fe
    "SAC": {'lat': 19.34561, 'lon': -99.009381},  # Santiago Acahualtepec
    "SJA": {'lat': 19.452592, 'lon': -99.086095},  # San Juan Aragón
    "TAH": {'lat': 19.246459, 'lon': -99.010564},  # Tláhuac
    "TLA": {'lat': 19.529077, 'lon': -99.204597},  # Tlalnepantla
    "TLI": {'lat': 19.602542, 'lon': -99.177173},  # Tultitlán
    "UIZ": {'lat': 19.360794, 'lon': -99.07388},  # UAM Iztapalapa
    "UAX": {'lat': 19.304441, 'lon': -99.103629},  # UAM Xochimilco
    "XAL": {'lat': 19.525995, 'lon': -99.0824}  # Xalostoc
}

# Definir lista de contaminantes y sus unidades
contaminants = list(data_contaminantes['pollutionMeasurements']['date']['2022-01-01 01:00'].keys())
contaminant_units = {
    'CO': 'ppm',
    'NO': 'ppb',
    'NO2': 'ppb',
    'NOX': 'ppb',
    'O3': 'ppb',
    'PM10': 'µg/m³',
    'SO2': 'ppb',
    'PM2.5': 'µg/m³',
    'PMCO': 'µg/m³'
}

# Crear una lista para almacenar los datos del contaminante
contaminants_data = []

# Iterar sobre las estaciones
for date_time, measurements in data_contaminantes['pollutionMeasurements']['date'].items():
    # Iterar sobre los contaminantes
    for contaminant in contaminants:
        # Obtener la fecha y los datos del contaminante para esa fecha
        contaminant_station_data = measurements.get(contaminant)
        if contaminant_station_data:
            # Iterar sobre las estaciones y sus respectivos valores del contaminante
            for station, value in contaminant_station_data.items():
                if value != '':
                    # Agregar el valor a la lista de datos de O3
                    contaminants_data.append({'Station': station, contaminant: float(value)})

# Convertir los datos en un DataFrame
df = pd.DataFrame(contaminants_data)

# Calcular el promedio del contaminante para cada estación
df = df.groupby('Station').mean().reset_index()

# Filtrar el DataFrame para incluir solo las estaciones de la CDMX
df = df[df['Station'].isin(station_coords.keys())]
df['lat'] = df['Station'].apply(lambda x: station_coords[x]['lat'])
df['lon'] = df['Station'].apply(lambda x: station_coords[x]['lon'])


def plot_contaminants_cdmx(df, contaminant):
    # Crear una copia del Data Frame sin nans para ese contaminante en particular
    df_contaminant = df[['Station', contaminant, 'lat', 'lon']].dropna(subset=[contaminant])

    # Crear la gráfica de mapa con Plotly
    fig = px.scatter_mapbox(
        df_contaminant,
        lat='lat',
        lon='lon',
        size=contaminant,
        color=contaminant,
        hover_name='Station',
        color_continuous_scale=px.colors.sequential.Plasma,
        size_max=17,
        mapbox_style="carto-darkmatter",
        opacity=0.7,
        center={"lat": 19.3657, "lon": -99.1318},
        zoom=8.8,
        title=f'Concentración promedio de {contaminant} en la Ciudad de México (2022)',
        height=600,
        width=600,
        template='cerulean+plotly_dark'
    )

    # Añadir el contorno de la Ciudad de México y aspectos de visualización
    fig.update_layout(
        margin={"r": 20, "t": 50, "l": 20, "b": 20},
        coloraxis_colorbar=dict(
            title=f"Concentración de {contaminant} ({contaminant_units[contaminant]})",
            titleside="right",
            tickmode="array",
            ticks="outside"
        ),
        mapbox=dict(
            layers=[{
                'source': cdmx_geojson,
                'type': 'line',
                'color': 'white',
                'opacity': 0.4,
                'line': {'width': 2}
            }]
        ),
    )

    return fig


# Contaminantes de interés para el análisis
analyzed_contaminants = ['O3', 'CO']

# Iterar para graficar cada concentración promedio de contaminante
figure_O3 = plot_contaminants_cdmx(df, 'O3')
figure_CO = plot_contaminants_cdmx(df, 'CO')

# ### Índice de Necesidades Básicas Insatisfechas (NBI)

nbi_df = data['necesidades basicas']

# Definir los niveles de insatisfacción y sus valores numéricos
nbi_levels = {
    'Pobreza muy alta': 6,
    'Pobreza alta': 5,
    'Pobreza moderada': 4,
    'Satisfaccion mínima': 3,
    'Estrato medio': 2,
    'Estrato alto': 1
}

# Mapear los valores alfanuméricos a numéricos
nbi_df['nbi_value'] = nbi_df['e_nbi'].map(nbi_levels)

# Calcular el promedio ponderado por alcaldía
nbi_promedio = nbi_df.groupby('alcaldia').apply(
    lambda x: (x['nbi_value'] * x['pop_tot']).sum() / x['pop_tot'].sum()).reset_index(name='nbi_promedio')
print(nbi_promedio)


def plot_nbi_cdmx(df, title, geojson):
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations='alcaldia',
        featureidkey='properties.NOMGEO',
        color='nbi_promedio',
        color_continuous_scale=px.colors.sequential.Viridis_r,
        range_color=(2.7, 4.3),
        mapbox_style="carto-darkmatter",
        zoom=8.8,
        center={"lat": 19.3657, "lon": -99.1318},
        opacity=0.5,
        labels={'nbi_value': 'Nivel de Insatisfacción'},
        title=title,
        height=600,
        template='cerulean+plotly_dark'
    )

    fig.update_layout(
        margin={"r": 20, "t": 50, "l": 20, "b": 20},
        coloraxis_colorbar=dict(
            title=f"NBI Promedio por Alcaldía",
            titleside="right",
            tickmode="array",
            ticks="outside"
        ),
    )

    return fig


# Graficar el índice de insatisfacción por alcaldía
figure_necesidades = plot_nbi_cdmx(nbi_promedio, 'Índice de Necesidades Básicas Insatisfechas (NBI)', cdmx_geojson)

#######################################################################################################################

ids_alcaldias_df = data['indice de desarrollo']

# Definir la escala de colores personalizada
estrato_colors = {
    'Muy bajo': '#870000',  # Vino
    'Bajo': '#DF0000',  # Rojo
    'Medio': '#FA4711',  # Naranja
    'Alto': '#FF995E',  # Amarillo dorado
    'Muy alto': '#FFC5A4'  # Amarillo
}

# Asignar el color correspondiente a cada estrato en una nueva columna
ids_alcaldias_df['color'] = ids_alcaldias_df['E_IDS_V'].map(estrato_colors)


# Crear una función para graficar el IDS por manzanas
def plot_ids_alcaldias(df, title, geojson):
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations='alcaldia',
        featureidkey='properties.NOMGEO',
        color='E_IDS_V',
        color_discrete_map=estrato_colors,
        mapbox_style="carto-darkmatter",
        zoom=8.8,
        center={"lat": 19.3657, "lon": -99.1318},
        opacity=0.5,
        labels={'E_IDS_V': 'IDS'},
        title=title,
        height=600,
        template='cerulean+plotly_dark'
    )

    return fig


# Graficar el IDS por alcaldia
figure_desarrollo = plot_ids_alcaldias(ids_alcaldias_df, 'Índice de Desarrollo Social por Alcaldía (2020)', cdmx_geojson)

#######################################################################################################################


import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

external_stylesheets = [dbc.themes.CERULEAN, dbc.themes.DARKLY]

app = Dash('', external_stylesheets=external_stylesheets)

app.layout = dbc.Container([
    dbc.Row([
        html.Hr()
    ]),
    dbc.Row([
        html.H4('Correlación entre acceso al agua, violencia, contaminación y acceso a recursos'),
        html.Hr()
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=fig_violencia),
        ]),
        dbc.Col([
            dcc.Graph(figure=fig_consumo),
            dcc.Graph(figure=fig_factibilidad)
        ])
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(figure=figure_O3), dcc.Graph(figure=figure_CO)]),
        dbc.Col([dcc.Graph(figure=figure_necesidades), dcc.Graph(figure=figure_desarrollo)])
    ]),
    dbc.Row([
        dbc.ListGroup([
            dbc.ListGroupItem([
                dbc.CardLink([
                    html.H6('Factibilidad hídrica'),
                ], href="https://datos.cdmx.gob.mx/dataset/factibilidad-hidrica")
            ]),
            dbc.ListGroupItem([
                dbc.CardLink([
                    html.H6('Consumo'),
                ],
                    href="https://datos.cdmx.gob.mx/dataset/consumo-habitacional-promedio-bimestral-de-agua-por-colonia-m3")
            ]),
            dbc.ListGroupItem([
                dbc.CardLink([
                    html.H6('Marginalidad y Violencia'),
                ],
                    href="https://datos.cdmx.gob.mx/dataset/grado-de-marginalidad-y-violencia-urbana-por-colonia-en-la-ciudad-de-mexico")
            ]),
            dbc.ListGroupItem([
                dbc.CardLink([
                    html.H6('Necesidades Básicas Insatisfechas'),
                ],
                    href="https://datos.cdmx.gob.mx/dataset/nbi-en-la-ciudad-de-mexico-por-grupos-de-edad-y-sexo-2020")
            ]),
            dbc.ListGroupItem([
                dbc.CardLink([
                    html.H6('Calidad del Aire'),
                ],
                    href="http://www.aire.cdmx.gob.mx/default.php?opc=%27aKBhnmI=%27&opcion=aw==")
            ]),
            dbc.ListGroupItem([
                dbc.CardLink([
                    html.H6('Indice de Desarrollo'),
                ],
                    href="https://evalua.cdmx.gob.mx/principales-atribuciones/medicion-del-indice-de-desarrollo-social-de-las-unidades-territoriales/medicion-del-indice-de-desarrollo-social-de-las-unidades-territoriales/bases-de-datos")
            ])
        ])
    ])
])

app.run_server(debug=True)
