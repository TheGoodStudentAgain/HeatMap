import pandas as pd
import plotly.express as px

data = {
    'Latitude': [37.7749, 34.0522, 40.7128],  # Exemple de coordonnées
    'Longitude': [-122.4194, -118.2437, -74.0060],
    'Valeur': [10, 20, 30],  # Exemple de valeurs pour la heatmap
}

df = pd.DataFrame(data)

fig = px.scatter_mapbox(
    df,
    lat='Latitude',
    lon='Longitude',
    hover_data=['Valeur'],  # Données à afficher au survol
    center={'lat': 37.7749, 'lon': -122.4194},  # Coordonnées du centre de la carte
    zoom=10,  # Niveau de zoom initial
)

heatmap_trace = px.density_mapbox(
    df,
    lat='Latitude',
    lon='Longitude',
    z='Valeur',  # Valeurs à afficher dans la heatmap
    radius=20,  # Rayon de la heatmap
    color_continuous_scale='Viridis',  # Colormap
    opacity=0.6,  # Opacité de la heatmap
)

fig.add_trace(heatmap_trace)
fig.show()