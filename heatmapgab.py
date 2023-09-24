import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from math import ceil, floor
import pandas as pd
import numpy as np
from zipfile import ZipFile
from PIL import Image
import glob

with ZipFile('gtfs_stm.zip') as myzip:
    stops_df = pd.read_csv(myzip.open('stops.txt'))

min_lat = stops_df['stop_lat'].min()
max_lat = stops_df['stop_lat'].max()
min_lon = stops_df['stop_lon'].min()
max_lon = stops_df['stop_lon'].max()

def getNbStopsInDegreeOnDegree(x, y, degree):
    return stops_df[(stops_df.stop_lat > x - degree/2) & (stops_df.stop_lat < x + degree/2) & (stops_df.stop_lon > y - degree/2) & (stops_df.stop_lon < y + degree/2)].shape[0]

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

index = 1
while index <= 5:
    while (current_x < max_lat):
        while (current_y < max_lon):
            listStats[xindex][yindex] = getNbStopsInDegreeOnDegree(current_x, current_y, degree)
            yindex += 1
            current_y += degree
        current_x += degree
        xindex += 1
        current_y = min_lon
        yindex = 0

    print(len(listStats), len(listStats[0]))

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
    pio.write_image(figure, 'heatmap{}.png'.format(index))
    index += 1

image_files = sorted(glob.glob('heatmap*.png'))

images = []
for image_file in image_files:
    img = Image.open(image_file)
    images.append(img)


images[0].save('heatmap_animation.gif', save_all=True, append_images=images[1:], duration=500, loop=0)
