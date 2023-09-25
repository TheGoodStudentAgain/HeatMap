import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from math import ceil, floor
import pandas as pd
import numpy as np
from zipfile import ZipFile
from PIL import Image
import time
import glob

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
degree = 0.01

xindex = 0
yindex = 0

min_lat_int = floor(min_lat/degree)
max_lat_int = ceil(max_lat/degree)
min_lon_int = floor(min_lon/degree)
max_lon_int = ceil(max_lon/degree)

listStats = [[0 for x in range(min_lon_int, max_lon_int)] for y in range(min_lat_int, max_lat_int)]

specific_dateTime = pd.to_datetime('2023-09-05 5:40:00')
programStartTime = time.time()

index = 1
while index <= 100:
    print("Image " + str(index) + " out of 100")
    while (current_x < max_lat):
        while (current_y < max_lon):
            listStats[xindex][yindex] = getNbBusesPerStopAreaFilterWithTimeWindow(specific_dateTime + pd.to_timedelta(15 * index-1, unit="m") , 15, current_x, current_y, degree)
            yindex += 1
            current_y += degree
        current_x += degree
        xindex += 1
        current_y = min_lon
        yindex = 0
    current_x = min_lat
    xindex = 0
    
    data = np.array(listStats)
    mask = data == 0
    colors = np.where(mask, 'rgba(0,0,0,0)', data)
    heatmap = go.Heatmap(z=colors)
    data = [heatmap]
    image = Image.open('map2.jpg')
    layout = go.Layout(
        images= [
            go.layout.Image(
                source=image,
                x=0,
                y=0,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="bottom",
                sizex=1,
                sizey=1,
                opacity=0.5,
        )],
        title='STM stops heatmap',
        width=880,
        height=800,
    )
    figure = go.Figure(data, layout)
    pio.write_image(figure, 'gif/heatmap{}.png'.format(index))
    index += 1
    print("Time elapsed: " + str(time.time() - programStartTime))
    print("Estimated time remaining: " + str((time.time() - programStartTime) * (100 - index) / index))

image_files = sorted(glob.glob('gif/heatmap*.png'))

images = []
for image_file in image_files:
    img = Image.open(image_file)
    images.append(img)


images[0].save('gif/heatmap_animation.gif', save_all=True, append_images=images[1:], duration=15, loop=0)
