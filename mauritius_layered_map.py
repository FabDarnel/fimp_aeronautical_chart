import folium
import json
import numpy as np
import math
import csv
import matplotlib.pyplot as plt
from folium.plugins import MousePosition
import pandas as pd

# read the waypoint csv dataset 
waypoint_df = pd.read_csv('waypoint_coordinates_1.csv')
point = waypoint_df["waypoint"].tolist()


# convert the latitude values to a numerical format
def convert_latitude(latitude):
    hemisphere = latitude[-1]
    degrees = int(latitude[:-1])
    decimal_degrees = degrees / 100
    if hemisphere == 'S':
        decimal_degrees = -decimal_degrees
    return decimal_degrees

# Convert the latitude values to decimal degrees
lat = [convert_latitude(latitude) for latitude in waypoint_df["lat"]]
lon = [float(longitude[:-1]) for longitude in waypoint_df["lon"]]
point = waypoint_df["waypoint"]

tma_waypoints = ["TIBAG", "OKMAR", 
             "DURDA", "DUNRI", 
             "TIDUM", "UNPUG", 
             "TIKOL", "OKBOG", 
             "TEVOD", "UVARI", 
             "EXIPU", "UTROD", 
             "IMRUL", "ATLOP", 
             "PASAR", "SOBAT", 
             "EPTEK", "RASMA", 
             "NIBIS"]

lat = []
lon = []

with open('tma_waypoint.csv', 'r') as file:
    reader = csv.reader(file)
    headers = next(reader)
    for row in reader:
        if row[0] in tma_waypoints:
            lat_degrees = int(row[1][:-1][:2])
            lat_minutes = int(row[1][:-1][2:])
            lat.append(-1 * (lat_degrees + lat_minutes / 60))
            
            lon_degrees = int(row[2][:-1][:3])
            lon_minutes = int(row[2][:-1][3:])
            lon.append(lon_degrees + lon_minutes / 60)


# Check if the number of waypoints and their coordinates match
if len(tma_waypoints) != len(lat) or len(tma_waypoints) != len(lon):
    print("Error: The number of waypoints and their coordinates do not match.")
    exit()

plt.scatter(lon, lat)

for i, point in enumerate(tma_waypoints):
    plt.annotate(point, (lon[i], lat[i]))

# New FIMP ARP coordinates
fimp_arp = [-20.430000, 57.683056]  # 20°25'48"S 057°40'59"E

# First Information Reporting (FIR) boundary coordinates
fir_boundary_coords = [
    [-10.000, 55.500], [-19.000, 55.500],
    [-22.333, 57.000], [-45.000, 57.000],
    [-45.000, 75.000], [-6.000, 75.000],
    [-6.000, 60.000], [-10.000, 60.000],
    [-10.000, 55.500], [-10.000, 55.500]
]

# Center point of the circle (DVOR/DME "PLS")
PLS_lat, PLS_lon = -20.2512, 57.3944

# Radius of the circle
radius = 150  # NM

# Generate the points that define the circle
PLS_arc_lat = [PLS_lat - radius / 60 * math.cos(math.radians(angle)) for angle in range(90, 220)]
PLS_arc_lon = [PLS_lon + radius / 60 * math.sin(math.radians(angle)) for angle in range(90, 220)]

# Combine the circle points with the boundary points
tma_coords = [
    [-23.135, 57.000], [-22.850, 58.288],
    # Arc of a circle with a radius of 150 NM centered on the DVOR/DME "PLS" (20.2512 S, 57.3944 E)
    *zip(PLS_arc_lat, PLS_arc_lon),
    [-18.325, 55.813], [-18.326, 55.500],
    # Along the FIR boundary
    [-19.000, 55.500], [-22.333, 57.000],
    [-23.135, 57.000]
]

# [-17.653, 57.053]

# Create a Folium map centered around the FIMP ARP point
m = folium.Map(location=fimp_arp, zoom_start=5)

# Create a feature group for the base map
base_map = folium.FeatureGroup(name='Base Map')

# Create a feature group for the FIR boundary
fir_boundary = folium.FeatureGroup(name='FIR Boundary')

# Create a feature group for the TMA layer
tma = folium.FeatureGroup(name='TMA')

# Create a feature group for the TMA waypoints
waypoint_layer = folium.FeatureGroup(name='TMA Waypoints')

# Add the FIR boundary to the map as a polygon in the "FIR Boundary" feature group
folium.Polygon(locations=fir_boundary_coords, color='red').add_to(fir_boundary)

# Add the marker for the FIMP ARP point to the "Base Map" feature group
folium.Marker(fimp_arp).add_to(base_map)

# Add the TMA layer to the map as a polygon in the "TMA" feature group
folium.Polygon(locations=tma_coords, color='blue').add_to(tma)

# Plot each waypoint on the map
for i in range(len(lat)):
    if i < len(point):
        folium.Marker(location=[lat[i], lon[i]], popup=f'{point[i]}<br>{lat[i]}, {lon[i]}').add_to(m)
    else:
        folium.Marker(location=[lat[i], lon[i]], popup=f'{lat[i]}, {lon[i]}').add_to(m)


# Loop through the TMA waypoints and add a marker for each one
for i, point in enumerate(tma_waypoints):
    folium.Marker([lat[i], lon[i]], popup=point).add_to(waypoint_layer)
    folium.Marker([lat[i], lon[i]], popup=f'{point}<br>{lat[i]}, {lon[i]}').add_to(waypoint_layer)
    folium.Marker([lat[i], lon[i]], popup=point, tooltip=f'{point}<br>{lat[i]}, {lon[i]}').add_to(waypoint_layer)

# Create a MousePosition plugin
formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
MousePosition(
    position="topright",
    separator=" | ",
    empty_string="NaN",
    lng_first=True,
    num_digits=20,
    prefix="Coordinates:",
    lat_formatter=formatter,
    lng_formatter=formatter,
).add_to(m)

# Add the "Base Map" and "FIR Boundary" feature groups to the map
base_map.add_to(m)
fir_boundary.add_to(m)

# Add the "TMA" feature group to the map
tma.add_to(m)

# Add the TMA waypoints feature group to the map
waypoint_layer.add_to(m)

# Add a layer control to allow the user to toggle the visibility of the "Base Map" and "FIR Boundary" layers
folium.LayerControl().add_to(m)

# Display the map
m.save('fir_boundary_map.html')
