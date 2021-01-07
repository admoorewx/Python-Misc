import folium
from folium.features import DivIcon
from branca.element import Element
from Metars import bulkMetars
from wx_utilities import C2F, roundTime
import datetime
from string import Template
import numpy as np

def tempColor(temp):
    colors = [
        "darkviolet", # -60 to -20
        "indigo", # -19 to -10
        "navy", # -9 to 0
        "mediumblue", # 0 to 20
        "dodgerblue", # 21 to 32
        "teal", # 33 to 40
        "lightseagreen", # 40 to 50
        "mediumseagreen", # 50 to 60
        "green", # 60 to 70
        "gold", # 70 to 80
        "orange", # 80 to 90
        "firebrick", # 90 to 100
        "deeppink", # 100 to 110
        "fuchisa" #110+
    ]
    if temp <= -20:
        color = colors[0]
    elif temp > -20 and temp <= -10:
        color = colors[1]
    elif temp > -10 and temp <= 0:
        color = colors[2]
    elif temp > 0 and temp <= 20:
        color = colors[3]
    elif temp > 20 and temp <= 32:
        color = colors[4]
    elif temp > 32 and temp <= 40:
        color = colors[5]
    elif temp > 40 and temp <= 50:
        color = colors[6]
    elif temp > 50 and temp <= 60:
        color = colors[7]
    elif temp > 60 and temp <= 70:
        color = colors[8]
    elif temp > 70 and temp <= 80:
        color = colors[9]
    elif temp > 80 and temp <= 90:
        color = colors[10]
    elif temp > 90 and temp <= 100:
        color = colors[11]
    elif temp > 100 and temp <= 110:
        color = colors[12]
    elif temp > 110:
        color = colors[13]
    else:
        print("Warning: Could not find appropriate color!")
        color = "white"
    return color

def dewpColor(dewp):
    colors = [
        "chocolate", # below 20 F
        "sandybrown", # 20 to 30 F
        "goldenrod", # 30 to 40
        "olive", # 40 to 45
        "darkolivegreen", # 45 to 50
        "teal", # 50 to 55
        "limegreen", # 55 to 60
        "mediumseagreen", # 60 to 65
        "seagreen", # 65 to 70
        "green", # 70 to 75
        "blue", # 75 to 80
        "indigo" # 80+
    ]
    if dewp <= 20:
        color = colors[0]
    elif dewp > 20 and dewp <= 30:
        color = colors[1]
    elif dewp > 30 and dewp <= 40:
        color = colors[2]
    elif dewp > 40 and dewp <= 45:
        color = colors[3]
    elif dewp > 45 and dewp <= 50:
        color = colors[4]
    elif dewp > 50 and dewp <= 55:
        color = colors[5]
    elif dewp > 55 and dewp <= 60:
        color = colors[6]
    elif dewp > 60 and dewp <= 65:
        color = colors[7]
    elif dewp > 65 and dewp <= 70:
        color = colors[8]
    elif dewp > 70 and dewp <= 75:
        color = colors[9]
    elif dewp > 75 and dewp <= 80:
        color = colors[10]
    elif dewp > 80:
        color = colors[11]
    else:
        print("Warning: Could not find appropriate color!")
        color = "white"
    return color


def createMap(obDensity=0):



    m = folium.Map(location=[40.,-100],
                   tiles="Stamen Toner",
                   zoom_start=5)


    radar_time = roundTime(datetime.datetime.utcnow(),300)
    if radar_time > datetime.datetime.utcnow():
        radar_time = radar_time - datetime.timedelta(seconds=300)
    radar_time = datetime.datetime.strftime(radar_time,"%Y-%m-%dT%H:%M:00Z")

    radar = folium.raster_layers.WmsTileLayer(
        url="https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0q-t.cgi",
        layers='nexrad-n0q-wmst',
        fmt="image/png",
        transparent=True,
        name="CONUS Base Reflectivity",
        time=radar_time,
        opacity=0.75)

    # radar = folium.raster_layers.WmsTileLayer(
    #     url="https://nowcoast.noaa.gov/arcgis/services/nowcoast/radar_meteo_imagery_nexrad_time/MapServer/WMSServer?",
    #     layers='1',
    #     fmt='image/png',
    #     transparent=True)
    radar.add_to(m)
    folium.TileLayer('cartodbdark_matter').add_to(m)
    folium.TileLayer('openstreetmap').add_to(m)
    #folium.TileLayer('MapQuest Open Aerial').add_to(m)
    tempPoints = folium.FeatureGroup(name="Surface Temperatures")
    dewpPoints = folium.FeatureGroup(name="Surface Dewpoints",show=False)

    if obDensity == 0:
        metars = bulkMetars()
    else:
        metars = bulkMetars()[::obDensity]

    fontsize = 9 # Font size of the temp/dewpoints; anything bigger than 12 will look bad
    windmarkers = []
    for ob in metars:
        try:
            temp = int(round(C2F(ob.temps[0]),0))
            color = tempColor(temp)
            text = " ".join(ob.rawObs[0])

            folium.map.Marker(
                [ob.lat, ob.lon],
                icon=DivIcon(
                    icon_size=(5,5),
                    icon_anchor=(25,15),
                    html='<div style="font-size:'+str(fontsize)+'pt; color:'+color+'; text-shadow:0 0 2px White;">'+str(temp)+'</div>',
                    ),
                tooltip=text,
                ).add_to(tempPoints)
        except:
            pass # Ignore the case where the temp is missing

        # Try to add the dewpoints
        try:
            dewp = int(round(C2F(ob.dewps[0]),0))
            color = dewpColor(dewp)
            text = " ".join(ob.rawObs[0])
            folium.map.Marker(
                [ob.lat, ob.lon],
                icon=DivIcon(
                    icon_size=(5,5),
                    icon_anchor=(25,3),
                    html='<div style="font-size:'+str(fontsize)+'pt; color:'+color+'; text-shadow:0 0 2px White;">'+str(dewp)+'</div>',
                    ),
                tooltip=text
                ).add_to(dewpPoints)
        except:
            pass # Ignore the case where the dewp is missing

        # Try to add the surface winds
        try:
            if ob.wspds[0] is np.nan or ob.wdirs[0] is np.nan:
                pass
            else:
                windbarbjs = Template(''' \
                var icon = L.WindBarb.icon({lat: $lat, deg: $dir, speed: $speed, pointRadius: 5, strokeWidth: 1, strokeLength: 15, barbSpaceing: 4, barbHeight: 10, fillColor: 'gray'}); \n \
                var marker = L.marker([$lat,$lon], {icon: icon}); \n \
                WindList.push(marker); \n \
                ''')
                windbarbjs = windbarbjs.safe_substitute({
                    'lat': str(ob.lat),
                    'lon': str(ob.lon),
                    'dir': str(ob.wdirs[0]),
                    'speed': str(ob.wspds[0]),
                })
                windmarkers.append(windbarbjs)
        except:
            continue

    tempPoints.add_to(m)
    dewpPoints.add_to(m)
    folium.LayerControl().add_to(m)


    # Get the HTML from the Folium Map
    html = m.get_root().render().splitlines()
    # Find the location of the </body> tag and insert the reguired JS script tag for the wind barbs
    # Also look for the layer_control id number so we can add the "winds" overlay
    for line in html:
        if "</body>" in line:
            bodyloc = html.index(line)
        if "L.control.layers(" in line:
            jsLayerControl = 'var LC = L.control.layers('
            newline = line.replace("L.control.layers(",jsLayerControl)
            loc = html.index(line)
            html[loc] = newline

    # Javascript lines that need to be added into the HTML in certain locations
    windlist = "            var WindList = [];\n"
    windlayer= "            var winds = L.layerGroup(WindList); \n"
    addwindlayer="          LC.addOverlay(winds,'Surface Winds'); \n"
    jsSRCtag = '\n<script src="./Leaflet.windbarb-master/src/leaflet-windbarb.js"></script>\n'
    jsend = '</script>'

    # adding in the JS lines where needed.
    windmarkers.insert(0,windlist)
    windmarkers.append(windlayer)
    windmarkers.append(addwindlayer)
    html.insert(bodyloc+1,jsSRCtag)
    # Remove the old </script> tag so we can add in additional lines
    html = html[:-1]
    # add in each of the wind markers
    for wind in windmarkers:
        html.append(wind)
    # add in the final </script> tag
    html.append(jsend)
    #print(("\n").join(html))
    # Write the HTML code to an HTML file
    htmlfile = open("folium.html",'w')
    for line in html:
        htmlfile.write(line+"\n")
    htmlfile.close()
    #m.save("folium.html")

createMap(10)
