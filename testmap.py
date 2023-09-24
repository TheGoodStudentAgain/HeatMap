import plotly.graph_objects as go
from plotly.offline import plot
from math import ceil, floor
import pandas as pd
import numpy as np
from zipfile import ZipFile

with ZipFile('gtfs_stm.zip') as myzip:
    stop_times_df = pd.read_csv(myzip.open('stop_times.txt'))
    stops_df = pd.read_csv(myzip.open('stops.txt'))
    calendar_df = pd.read_csv(myzip.open('calendar.txt'))
    trips_df = pd.read_csv(myzip.open('trips.txt'))

merged_df = stop_times_df.merge(trips_df, on='trip_id').merge(calendar_df, on='service_id')

min_lat = stops_df['stop_lat'].min()
max_lat = stops_df['stop_lat'].max()
min_lon = stops_df['stop_lon'].min()
max_lon = stops_df['stop_lon'].max()

def getStopsInDegreeOnDegree(x, y, degree):
    return stops_df[(stops_df.stop_lat > x - degree/2) & (stops_df.stop_lat < x + degree/2) & (stops_df.stop_lon > y - degree/2) & (stops_df.stop_lon < y + degree/2)]

def getNbBusesPerStopAreaFilterWithTimeWindow(dateTime, time_window, x, y, degree):
    stops = getStopsInDegreeOnDegree(x, y, degree)
    time_window_start = pd.to_datetime(dateTime)
    time_window_end = time_window_start + pd.to_timedelta(time_window, unit='m')

    if stops.shape[0] == 0:
        return 0
    
    print(merged_df['arrival_time'] + ' ' + merged_df['start_date'].astype(str))

    merged_df['arrival_time'] = pd.to_datetime(merged_df['arrival_time'], format='%H:%M:%S', errors='coerce')
    merged_df['start_date'] = pd.to_datetime(merged_df['start_date'], format='%Y%m%d')
    merged_df['end_date'] = pd.to_datetime(merged_df['end_date'], format='%Y%m%d')

    merged_df['arrival_time'] = merged_df['arrival_time'].replace(
        pd.NaT, pd.to_datetime('00:00:00', format='%H:%M:%S') + pd.Timedelta(days=1))     

    print(merged_df.head(1))

    filtered_df = merged_df[
        (merged_df['arrival_time'] >= time_window_start) &
        (merged_df['arrival_time'] <= time_window_end) &
        (merged_df['start_date'] <= time_window_start) &
        (merged_df['end_date'] >= time_window_end) &
        (merged_df['stop_id'].isin(stops['stop_id']))]

    trips_in_time_window = filtered_df.shape[0]
    return trips_in_time_window


current_x = min_lat
current_y = min_lon
degree = 0.1
specific_dateTime = pd.to_datetime('2023-10-09 12:00:00')

xindex = 0
yindex = 0

min_lat_int = floor(min_lat/degree)
max_lat_int = ceil(max_lat/degree)
min_lon_int = floor(min_lon/degree)
max_lon_int = ceil(max_lon/degree)

listStats = [[0 for x in range(min_lon_int, max_lon_int)] for y in range(min_lat_int, max_lat_int)]


while (current_x < max_lat):
    while (current_y < max_lon):
        listStats[xindex][yindex] = getNbBusesPerStopAreaFilterWithTimeWindow(specific_dateTime, 15, current_x, current_y, degree)
        yindex += 1
        current_y += degree
    current_x += degree
    xindex += 1
    current_y = min_lon
    yindex = 0

data = np.array(listStats)
mask = data == 0
colors = np.where(mask, 'rgba(0,0,0,0)', data)
heatmap = go.Heatmap(z=colors, x=np.arange(min_lon_int, max_lon_int), y=np.arange(min_lat_int, max_lat_int))
data = [heatmap]
fig = go.Figure(data=data)
plot(fig, filename='heatmap.html', auto_open=True)