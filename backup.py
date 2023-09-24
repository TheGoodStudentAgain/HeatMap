import plotly.graph_objects as go
from plotly.offline import plot
from math import ceil, floor
import pandas as pd
import numpy as np
from zipfile import ZipFile

def normalize_time(time_str):
    hours = int(time_str[:2])
    minutes = int(time_str[3:5])
    seconds = int(time_str[6:8])
    if hours >= 24:
        return f'{hours-24:02d}:{minutes:02d}:{seconds:02d}'
    else:
        return f'{hours:02d}:{minutes:02d}:{seconds:02d}'

def getStopsInDegreeOnDegree(x, y, degree):
    return stops_df[(stops_df.stop_lat > x - degree/2) & (stops_df.stop_lat < x + degree/2) & (stops_df.stop_lon > y - degree/2) & (stops_df.stop_lon < y + degree/2)]

def getNbBusesPerStopAreaFilterWithTimeWindow(dateTime, time_window, x, y, degree):
    stops = getStopsInDegreeOnDegree(x, y, degree)
    time_window_start = pd.to_datetime(dateTime)
    time_window_end = time_window_start + pd.to_timedelta(time_window, unit='m')

    if stops.shape[0] == 0:
        return 0

    day_name = time_window_start.date().strftime("%A").lower()
    string_date = time_window_start.date().strftime('%Y%m%d')
    int_date = int(string_date)

    string_time_start = time_window_start.time().strftime('%H:%M:%S')
    string_time_end = time_window_end.time().strftime('%H:%M:%S')

    merged_df_filtered = merged_df[
        (merged_df['start_date'] <= int_date) &
        (merged_df['end_date'] >= int_date) &
        (merged_df[day_name] == 1)]
    
    time_start = pd.to_datetime(string_time_start, format='%H:%M:%S')
    time_end = pd.to_datetime(string_time_end, format='%H:%M:%S')

    filtered_df = merged_df_filtered[
        (merged_df_filtered['arrival_time'] >= time_start) &
        (merged_df_filtered['arrival_time'] <= time_end)]
    
    stopseries = stops['stop_id'].values
    filtered_df_stop_filter = filtered_df[filtered_df['stop_id'].isin(stopseries)]

    trips_in_time_window = filtered_df_stop_filter.shape[0]
    return trips_in_time_window

with ZipFile('gtfs_stm.zip') as myzip:
    stop_times_df = pd.read_csv(myzip.open('stop_times.txt'))
    stops_df = pd.read_csv(myzip.open('stops.txt'))
    calendar_df = pd.read_csv(myzip.open('calendar.txt'))
    trips_df = pd.read_csv(myzip.open('trips.txt'))

merged_df = stop_times_df.merge(trips_df, on='trip_id').merge(calendar_df, on='service_id')
merged_df['arrival_time'] = merged_df['arrival_time'].apply(normalize_time)
merged_df['arrival_time'] = pd.to_datetime(merged_df['arrival_time'], format='%H:%M:%S')
merged_df['stop_id'] = merged_df['stop_id'].astype(str)

min_lat = stops_df['stop_lat'].min()
max_lat = stops_df['stop_lat'].max()
min_lon = stops_df['stop_lon'].min()
max_lon = stops_df['stop_lon'].max()

current_x = min_lat
current_y = min_lon
degree = 0.1

xindex = 0
yindex = 0

min_lat_int = floor(min_lat/degree)
max_lat_int = ceil(max_lat/degree)
min_lon_int = floor(min_lon/degree)
max_lon_int = ceil(max_lon/degree)

listStats = [[0 for x in range(min_lon_int, max_lon_int)] for y in range(min_lat_int, max_lat_int)]

specific_dateTime = pd.to_datetime('2023-09-05 5:40:00')

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
heatmap = go.Heatmap(z=colors)
data = [heatmap]
heatmap = go.Heatmap(z=colors)
data = [heatmap]
fig = go.Figure(data=data)
plot(fig, filename='heatmap.html', auto_open=True)
