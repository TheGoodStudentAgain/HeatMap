import plotly.express as px

df = px.data.carshare()
print(df['centroid_lon'])
print(df['centroid_lat'])
print(df)


fig = px.scatter_mapbox(df,
                        lon = df['centroid_lon'],
                        lat = df['centroid_lat'],
                        zoom = 10,
                        color = df['peak_hour'],
                        size = df['car_hours'],
                        width = 1200,
                        height = 900,
                        title = 'text',
                        )

fig.update_layout(mapbox_style = 'open-street-map')
fig.update_layout(margin = {'r':0, 't':50, 'l':0, 'b':10})
fig.show()