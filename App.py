import folium.features
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import time
from utils import basemaps, colormap_scales, get_color

# PREAMBLE

APP_TITLE = "CAKE visualizer 🎂"
APP_SUBTITLE = "By Adrian Mungroo"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎂",
    layout='wide'
    )
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

if 'list1' not in st.session_state:
    st.session_state['list1'] = []

# READING SELECT DATASETS

@st.cache_data
def load_data():
    data = gpd.read_file(f'./data/hex.geojson').to_crs(epsg=4326)
    return data

hex = load_data()

def main():    
    # DEFINING MAP STATE
    if 'center' not in st.session_state:
        st.session_state.center = [33.7689, -84.3434]
    if 'zoom' not in st.session_state:
        st.session_state.zoom = 11
    if 'last_interaction' not in st.session_state:
        st.session_state.last_interaction = time.time()
    if 'list1' not in st.session_state:
        st.session_state['list1'] = []
    if 'to_plot' not in st.session_state:
        st.session_state['to_plot'] = ''

    # MAKING MAIN COLUMNS
    main_column1, main_column2 = st.columns([0.3, 0.7])

    with main_column1:
        st.write('#### Map Options')
        with st.expander("Expand for map options"):
            basemap_choice = st.selectbox('Basemap', sorted(list(basemaps.keys())), index=4)  # OpenStreetMap as default
            color_choice = st.selectbox('Colormap Scales', colormap_scales, index=10)  # Reds as default
            opacity_choice = st.slider('Fill Opacity', min_value=0, max_value=100, value=40) / 100
            line_opacity_choice = st.slider('Line Opacity', min_value=0, max_value=100, value=5) / 100

        st.write('#### Data Options')
        sub_column1, sub_column2 = st.columns(2)
        with sub_column1:
            column_choice = st.selectbox('List of Attributes', [''] + list(hex.columns[1:-1]))
            if column_choice and column_choice not in st.session_state['list1']:
                st.session_state['list1'].append(column_choice)
                st.session_state['to_plot'] = column_choice
        with sub_column2:
            to_plot = st.selectbox('Loaded Datasets', st.session_state['list1'])
        
        

        data = hex

        st.write('#### Custom Query')
        query_string = st.text_area('Enter your custom query:', value='', height=100)
        if query_string:
            data = data.query(query_string)

    # MAKE MAP OBJECT
    data_json = data.to_json()

    m = folium.Map(prefer_canvas= True, zoom_control=False, tiles=basemaps[basemap_choice], attr='basemap-choice',
                   location=st.session_state.center, zoom_start=st.session_state.zoom)
    
    column_choice = to_plot
    if column_choice:
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
            tooltip=folium.GeoJsonTooltip(
                fields=list(hex.columns[1:-1]),  # 'name' or any other property in your GeoJSON, and column_choice for data values
                aliases=list(hex.columns[1:-1]),  # Optional: aliases for the fields
                localize=True,
                sticky=True
            ),
            name=f'{column_choice}'
        ).add_to(m)

    with main_column2:
        # c1,c2,c3 = st.columns(3)
        # with c1:
        #     st.write('#### Scenario control')
        # with c2:
        #     st.write('#### Radio Buttons')
        # with c3:
        #     st.write('#### Sliders')
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