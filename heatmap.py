import plotly.express as px
import pandas as pd
from zipfile import ZipFile

with ZipFile('gtfs_stm.zip') as myzip:
    stops_df = pd.read_csv(myzip.open('stops.txt'))

print(stops_df.head(1))

def getSmallestLatLon(): # South-West
    return stops_df[['stop_lat', 'stop_lon']].min()

def getBiggestLatLon(): # North-East
    return stops_df[['stop_lat', 'stop_lon']].max()

def getStopWithLat(x):
    return stops_df[stops_df.stop_lat == x]

def getStopWithLon(y):
    return stops_df[stops_df.stop_lon == y]

def getStopFromLatLon(x, y):
    return stops_df[(stops_df.stop_lat == x) & (stops_df.stop_lon == y)]

def getNbStopsIn100x100m(x, y):
    return stops_df[(stops_df.stop_lat > x -0.0005) & (stops_df.stop_lat < x + 0.0005) & (stops_df.stop_lon > y - 0.0005) & (stops_df.stop_lon < y + 0.0005)].shape[0]

latLongmin = getSmallestLatLon()
latLongmax = getBiggestLatLon()