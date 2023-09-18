import plotly.express as px
import pandas as pd
from zipfile import ZipFile

with ZipFile('gtfs_stm.zip') as myzip:
    stops_df = pd.read_csv(myzip.open('stops.txt'))

min_lat = stops_df['stop_lat'].min()
max_lat = stops_df['stop_lat'].max()
min_lon = stops_df['stop_lon'].min()
max_lon = stops_df['stop_lon'].max()

def getNbStopsInDegreeOnDegree(x, y, degree):
    return stops_df[(stops_df.stop_lat > x - degree/2) & (stops_df.stop_lat < x + degree/2) & (stops_df.stop_lon > y - degree/2) & (stops_df.stop_lon < y + degree/2)].shape[0]


