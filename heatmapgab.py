import numpy as np
import datetime
import plotly.graph_objects as go
from plotly.offline import plot

trace = go.Heatmap(z = [[1, 20, 30],
                        [20, 1, 60],
                        [30, 60, 1]])
data = [trace]
plot(data, filename = 'basic-heatmap.html')