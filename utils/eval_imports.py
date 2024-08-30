# Imports for Evals
import datetime
import time
import geopy
import folium
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import shapely
from shapely.geometry import LineString, Point, Polygon
from thefuzz import process, fuzz
from utils.geocoder import get_geo_location

# Create a dictionary for namespace with imported modules
import_namespace = {
    'datetime': datetime,
    'time': time,
    'geopy': geopy,
    'folium': folium,
    'gpd': gpd,
    'matplotlib': matplotlib,
    'plt': plt,
    'np': np,
    'pd': pd,
    'plotly': plotly,
    'px': px,
    'shapely': shapely,
    'LineString': LineString,
    'Point': Point,
    'Polygon': Polygon,
    'process': process,
    'fuzz': fuzz,
    'get_geo_location': get_geo_location,
    "result": None
}