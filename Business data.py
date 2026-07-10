import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import osmnx as ox

sensors = pd.read_csv("Sensor_Location.csv")

centres = {
    "Central": (-2.592, 51.453), #2
    "East": (-2.555, 51.457), #42
    "North": (-2.616, 51.479) #63
}

radius_m = 1200 

mean_lat = sensors["Latitude"].mean()

lat_to_m = 111000
lon_to_m = 111000 * np.cos(np.deg2rad(mean_lat))

def distance_m(lon1, lat1, lon2, lat2):
    dx = (lon1 - lon2) * lon_to_m
    dy = (lat1 - lat2) * lat_to_m
    return np.sqrt(dx**2 + dy**2)

sensor_clusters = []

for _, row in sensors.iterrows():
    distances = {
        name: distance_m(row["Longitude"], row["Latitude"], clon, clat)
        for name, (clon, clat) in centres.items()
    }
    
    closest_cluster = min(distances, key=distances.get)
    
    if distances[closest_cluster] <= radius_m:
        sensor_clusters.append(closest_cluster)
    else:
        sensor_clusters.append("Outlier")

sensors["Cluster"] = sensor_clusters

print("\nSensor count per cluster:")
print(sensors.groupby("Cluster").size())

#Getting business data from openstreetsmap

place = "Bristol, UK"

tags = {
    "amenity": ["cafe", "restaurant", "bar", "pub"],
    "shop": True
}

businesses = ox.features_from_place(place, tags)
businesses = businesses.reset_index()

#Cleaning data
businesses = businesses[businesses.geometry.type == "Point"]

businesses["Longitude"] = businesses.geometry.x
businesses["Latitude"] = businesses.geometry.y

businesses["Type"] = np.where(
    businesses["amenity"].notna(),
    businesses["amenity"],
    businesses["shop"]
)

print("Total businesses downloaded:", len(businesses))

business_clusters = []

for _, row in businesses.iterrows():
    distances = {
        name: distance_m(row["Longitude"], row["Latitude"], clon, clat)
        for name, (clon, clat) in centres.items()
    }
    
    closest_cluster = min(distances, key=distances.get)
    
    if distances[closest_cluster] <= radius_m:
        business_clusters.append(closest_cluster)
    else:
        business_clusters.append("Outlier")

businesses["Cluster"] = business_clusters

print("\nBusiness count per cluster:")
print(businesses.groupby("Cluster").size())

#Business density
area_km2 = np.pi * (1.2 ** 2) 

business_counts = businesses.groupby("Cluster").size()
business_density = business_counts / area_km2

print("\nBusiness density (per km²):")
print(business_density)


plt.figure()

# Plot businesses
for name, group in businesses.groupby("Cluster"):
    plt.scatter(group["Longitude"], group["Latitude"], s=10, alpha=0.5)

# Plot sensors
for name, group in sensors.groupby("Cluster"):
    plt.scatter(group["Longitude"], group["Latitude"], 
                marker="x", s=80)

# Draw cluster circles
theta = np.linspace(0, 2*np.pi, 200)

for name, (clon, clat) in centres.items():
    circle_lon = clon + (radius_m / lon_to_m) * np.cos(theta)
    circle_lat = clat + (radius_m / lat_to_m) * np.sin(theta)
    
    plt.plot(circle_lon, circle_lat)
    plt.scatter(clon, clat, marker="o")

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Sensor Clusters and Leisure Businesses")
plt.gca().set_aspect("equal", adjustable="box")
plt.show()