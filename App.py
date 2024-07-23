import folium.features
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import time
from utils import basemaps, colormap_scales, get_color

# PREAMBLE

APP_TITLE = "CAKE visualizer demo 🎂"
APP_SUBTITLE = "By Adrian Mungroo"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎂",
    layout='wide'
    )
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

# READING SELECT DATASETS

@st.cache_data
def load_data(hexel_level):
    data = gpd.read_file(f'./data/hex{hexel_level}.geojson').to_crs(epsg=4326)
    return data

hex7 = load_data(7)
hex8 = load_data(8)

column_list = ['energybrdn', 'HRS2020']

def main():
    # DEFINING MAP STATE
    if 'center' not in st.session_state:
        st.session_state.center = [33.7689, -84.3434]
    if 'zoom' not in st.session_state:
        st.session_state.zoom = 11
    if 'last_interaction' not in st.session_state:
        st.session_state.last_interaction = time.time()

    # MAKING MAIN COLUMNS
    main_column1, main_column2 = st.columns([0.3, 0.7])

    with main_column1:
        st.write(
            '### Map Options'
        )

        sub_column1, sub_column2 = st.columns(2)
        with sub_column1:
            basemap_choice = st.selectbox('Basemap',  sorted(list(basemaps.keys())), index=4) # OpenStreetMap as default
            opacity_choice = st.slider('Fill Opacity', min_value=0, max_value=100, value=40)/100
        with sub_column2:
            color_choice = st.selectbox('Colormap Scales', colormap_scales, index=10) # Reds as default
            line_opacity_choice = st.slider('Line Opacity', min_value=0, max_value=100, value=5)/100

        st.write('### Data Options')
        sub_column1, sub_column2 = st.columns(2)
        with sub_column1:
            hexel_level = st.selectbox('Hexel Level', ['Large','Small'])
        with sub_column2:
            column_choice = st.selectbox('List of Attributes', column_list)

        data = hex7 if hexel_level == 'Large' else hex8

        st.write('### Custom Query')
        query_string = st.text_area('Enter your custom query:', value='', height=10)
        if query_string:
            data = data.query(query_string)

    # MAKE MAP OBJECT
    data_json = data.to_json()

    m = folium.Map(prefer_canvas= True, zoom_control=False, tiles=basemaps[basemap_choice], attr='basemap-choice',
                   location=st.session_state.center, zoom_start=st.session_state.zoom)
        
    min_value = data[column_choice].min()
    max_value = data[column_choice].max()  

    def style_function(feature):
        value = feature['properties'][column_choice]
        color = get_color(value, min_value, max_value, colormap_scales[color_choice])
        return {
            'fillColor': color,
            'color': 'black',
            'weight': line_opacity_choice,
            'fillOpacity': opacity_choice
        }  
    
    folium.GeoJson(
        data_json,
        style_function=style_function,
        name=f'{column_choice}'
    ).add_to(m)

    with main_column2:
        map_object = st_folium(m, width = 1250, height = 600)

    # UPDATING MAP STATE

    # current_time = time.time()
    # debounce_time = 3

    # if map_object:
    #     if current_time - st.session_state.last_interaction > debounce_time:
    #         st.session_state.center = [map_object['center']['lat'], map_object['center']['lng']]
    #         st.session_state.zoom = map_object['zoom']
    #         st.session_state.last_interaction = current_time

if __name__ == "__main__":
    main()