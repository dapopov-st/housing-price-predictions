
# Import streamlit pandas and geopandas
import streamlit as st
import pandas as pd
import geopandas as gpd

# Import folium and related plugins
import folium
from folium import Marker
from folium.plugins import MarkerCluster

# Geopy's Nominatim
from geopy.geocoders import Nominatim

# Scipy's Spatial
from scipy import spatial


import requests
from io import StringIO
from io import BytesIO


import json


# Get the data from url and request it as json file


@st.cache
def load_data():
    """Load the test files with model predictions, subsampling a fraction of it for
    display purposes"""
    # path = '../data/test_and_pred_cap_rate.csv' #path for linear model
    path = "../data/test_and_tree_pred_cap_rate.csv"
    df = pd.read_csv(path)
    df['Latitude'] = df['lats']
    df['Longitude'] = df['longs']
    df = df.drop(['lats', 'longs'], axis=1)
    # randomly subsamble 10% of the houses for less clutter on the map
    df_ = df.sample(frac=0.2, replace=False, random_state=42)
    return df_


def load_ames_data():
    """Load GeoJSON city boundary for Ames, Iowa"""
    # Stored on Google Drive. If getting permission denied errors, store this on your own Google Drive
    original_url_ames = "https://drive.google.com/file/d/1ipjGTVEApKw05eiUFSNVQqPg8a3o8UvJ/view?usp=sharing"

    file_id_ames = original_url_ames.split('/')[-2]
    dwn_url_ames = 'https://drive.google.com/uc?export=download&id=' + file_id_ames
    url_ames = requests.get(dwn_url_ames).content
    return url_ames


def convert_address(address):
    """Only used to load Ames, Iowa or seach for custom address.  Other locations
    have been preloaded into the csv file to reduce latency"""
    # Here we use Nominatin to convert address to a latitude/longitude coordinates"
    geolocator = Nominatim(user_agent="my_app")  # using open street map API
    Geo_Coordinate = geolocator.geocode(address)
    lat = Geo_Coordinate.latitude
    lon = Geo_Coordinate.longitude
    # Convert the lat long into a list and store is as point
    point = [lat, lon]
    return point


def handle_custom_point(point, df):
    unk_lat = 42.003590
    unk_long = -93.660759

    df_lat = round(df['Latitude'], 5)
    df_long = round(df['Longitude'], 5)
    search_lat = round(point[0], 5)
    search_long = round(point[1], 5)

    mask = ((df_lat == search_lat) & (
        df_long == search_long)).any()
    if mask:
        obs = df.loc[(df_lat == search_lat) & (
            df_long == search_long)].iloc[0]

        location_ = [search_lat, search_long]

        pred_price = round(obs.loc['preds'])
        area = round(obs.loc['GrLivArea_x'])
        qual = round(obs.loc['OverallQual_x'])
        yr_built = round(obs.loc['YearBuilt_x'])
        address = obs.loc['Full_Addr']
        owner = obs.loc['MA_Ownr1'] if obs['MA_Ownr1'] != 'NaN' else "Unknown"
        cap_r = round(obs.loc['cap_rate'], 3)

        return folium.Marker(location=location_,
                             popup="""
                        <i>Predicted price: </i> <br> <b>${}</b> </i> <br>
                        <i>Predicted cap rate: </i> <br> <b>{}%</b> </i> <br>
                        <i> Sqft: </i><b><br>{}</b> <br></i>
                        <i> Quality: </i> <br> <b>{}</b> <br></i>
                        <i> Year built: </i> <br> <b>{}</b> <br></i>
                        <i> Owner: </i> <br> <b>{}</b> <br></i>
                        <i> Address: </i> <br> <b>{}</b> <br></i>

                        """.format(pred_price, cap_r*100, area, qual, yr_built, owner, address),
                             icon=folium.Icon(color='orange', icon="info-sign"))

    else:
        print("Address not found")

        return folium.Marker(location=[unk_lat, unk_long],
                             popup="""
                        <i>Address not yet in database </i> <br> <b>{}</b> </i>
                        """.format(" "),
                             icon=folium.Icon(color='black', icon="info-sign"))


def display_map(point, df, oakl_geojson):
    isu_lat = 42.0267
    isu_long = -93.651619

    m = folium.Map(point,
                   zoom_start=11, tiles="OpenStreetMap")

    # Add polygon boundary to folium map
    folium.GeoJson(oakl_geojson, style_function=lambda x: {'color': 'blue', 'weight': 2.5, 'fillOpacity': 0},
                   name='Ames').add_to(m)

  # Add marker for location in selected subset of the test set

    for i in range(len(df)):
        obs = df.iloc[i]
        location_ = [obs.loc['Latitude'], obs.loc['Longitude']]
        pred_price = round(obs.loc['preds'])
        area = round(obs.loc['GrLivArea_x'])
        qual = round(obs.loc['OverallQual_x'])
        #central_air = 'Yes' if round(obs.loc['CentralAir_Y']) == 1 else 'No'
        yr_built = round(obs.loc['YearBuilt_x'])
        address = obs.loc['Full_Addr']
        owner = obs.loc['MA_Ownr1'] if obs.loc['MA_Ownr1'] != 'NaN' else "Unknown"
        #dist = obs.loc["distToUI"]
        cap_r = round(obs.loc['cap_rate'], 3)

        if cap_r < 0:
            color_ = 'darkred'
        elif cap_r < 0.05:
            color_ = 'lightblue'
        elif cap_r < 0.1:
            color_ = 'blue'
        else:
            color_ = 'darkblue'
        # if dist < 0.8:  # .5 mile+ campus size adjustment
        #     color_ = "green"
        # elif dist < 1.3:
        #     color_ = "lightgreen"
        # else:
        #     color_ = 'blue'

        folium.Marker(location=location_,
                      popup="""
                  <i>Predicted price: </i> <br> <b>${}</b> </i> <br>
                  <i>Predicted cap rate: </i> <br> <b>{}%</b> </i> <br>
                  <i> Sqft: </i><b><br>{}</b> <br></i>
                  <i> Quality: </i> <br> <b>{}</b> <br></i>
                  <i> Year built: </i> <br> <b>{}</b> <br></i>
                  <i> Owner: </i> <br> <b>{}</b> <br></i>
                  <i> Address: </i> <br> <b>{}</b> <br></i>

                  """.format(pred_price, cap_r*100, area, qual, yr_built, owner, address),
                      icon=folium.Icon(color=color_, icon="info-sign")).add_to(m)

    folium.Marker(location=[isu_lat, isu_long],
                  popup="""
                  <i>Iowa State University: </i> <br> <b>{}</b> </i>
                  """.format('Ames,Iowa'),
                  icon=folium.Icon(color="gray", icon="info-sign")).add_to(m)

    folium.CircleMarker(
        location=[isu_lat, isu_long],
        radius=50,
        popup="Iowa State University",
        color="#3186cc",
        fill=True,
        fill_color="#3186cc",
    ).add_to(m)

    # Handle custom point
    custom_marker = handle_custom_point(point, df)
    custom_marker.add_to(m)

    return st.markdown(m._repr_html_(), unsafe_allow_html=True)

# Adding a background to streamlit page


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def main():
    # Load csv data
    # df_data = load_data()

    # Change to load my data!
    df_data = load_data()

    # Load geoJSON file using json.loadas
    oakl_json = load_ames_data()
    oakl_json = oakl_json.decode("utf-8")
    oakl_geojson = json.loads(oakl_json)

    # For the page display, create headers and subheader, and get an input address from the user
    local_css("style.css")
    st.header("Investing in College Real Estate in Ames, Iowa")
    st.text("")
    st.markdown('<p class="big-font">This app reports price prediction for homes in Ames, Iowa based on machine learning and estimates expected profit margins from college rentals based on real estate studies.</p>', unsafe_allow_html=True)
    st.text("")

    address = st.text_input(
        "Starting Location", "Ames, IA 50011")

    coordinates = convert_address(address)

    # Call the display_map function by passing coordinates, dataframe and geoJSON file
    st.text("")
    display_map(coordinates, df_data, oakl_geojson)


if __name__ == "__main__":
    main()
