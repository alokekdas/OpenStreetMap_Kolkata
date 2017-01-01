import numpy as np
import pandas as pd
%pylab inline
import matplotlib.pyplot as plt
import sqlite3

""" Start working with the DB created separately with OSM data """
conn = sqlite3.connect("Kolkata.db")
c = conn.cursor()

""" The following two lists will hold the lat/lon information of the nodes """
lat_list = []
lon_list = []

""" Extract university location information from the nodes_tags table """
c.execute("select id from nodes_tags where key='amenity' and value='university'")
info_nodes = c.fetchall()
for node in info_nodes:
    for node_lat, node_lon in c.execute('select lat, lon from nodes where id = ?', node):
        lat_list.append(node_lat)
        lon_list.append(node_lon)
#df = pd.DataFrame({'lat':lat_list, 'lon':lon_list})
#plt.plot(df['lat'], df['lon'], 'ro')    

""" Extract university location information from the ways_tags and ways_nodes tables """
c.execute("select id from ways_tags where key='amenity' and value='university'")
info_way_tags = c.fetchall()
for way_id in info_way_tags:
    """ Create a list of nodes that this id is linked with """
    list_of_nodes = []
    for node_id in c.execute('select node_id from ways_nodes where id = ?', way_id):
        list_of_nodes.append(node_id)

    """ Iterate over these node elements and find out their location information """
    for my_node in list_of_nodes:
        for node_lat, node_lon in c.execute("select lat, lon from nodes where id = ?", my_node):
            lat_list.append(node_lat)
            lon_list.append(node_lon)

""" 
    Now that we have extracted the location information for all the nodes related to
    university, we are ready to plot them 
"""
df = pd.DataFrame({'lat':lat_list, 'lon':lon_list})
        
plt.plot(df['lat'], df['lon'], 'g^')
plt.xlabel('Lattitude')
plt.ylabel('Longitude')
plt.title('Location of universities')
conn.close()