import streamlit as st
import folium
from folium.plugins import HeatMap
import numpy as np
import math
from streamlit_folium import st_folium

st.set_page_config(page_title="Gaussian Plume Simulation", layout="wide")

def plume(lat0, lon0, Q, U, wind_from, H):
    wind_to = (wind_from + 180) % 360

    x = np.linspace(100, 15000, 100)
    y = np.linspace(-7500, 7500, 100)
    X, Y = np.meshgrid(x, y)

    sy = 0.08 * X
    sz = 0.06 * X

    C = (Q / (2 * np.pi * U * sy * sz)) * \
        np.exp(-0.5 * (Y / sy)**2) * \
        np.exp(-0.5 * (H / sz)**2)

    C[X < 100] = 0

    angle = math.radians(wind_to)
    dx = X * math.cos(angle) - Y * math.sin(angle)
    dy = X * math.sin(angle) + Y * math.cos(angle)

    lat = lat0 + dy / 111000
    lon = lon0 + dx / (111000 * math.cos(math.radians(lat0)))

    heat = [
        [lat[i, j], lon[i, j], float(C[i, j])]
        for i in range(100) for j in range(100)
        if C[i, j] > C.max() * 0.001
    ]

    m = folium.Map(location=[lat0, lon0], zoom_start=8)
    HeatMap(heat, radius=18, blur=12).add_to(m)
    folium.Marker([lat0, lon0], popup="Source").add_to(m)

    return m

st.title("☢ Gaussian Plume Simulation Web App")
st.write("Model & visualize nuclear contamination plumes using Python + Streamlit.")

st.sidebar.header("Simulation Parameters")

location = st.sidebar.selectbox("Select Case Study", ("Fukushima Daiichi (Japan)", "Chernobyl (Ukraine)"))

if location == "Fukushima Daiichi (Japan)":
    lat0, lon0 = 37.421, 141.032
elif location == "Chernobyl (Ukraine)":
    lat0, lon0 = 51.389, 30.099

Q = st.sidebar.number_input("Emission Rate (Q)", value=1e13)
U = st.sidebar.number_input("Wind Speed (U)", value=4.0)
wind_from = st.sidebar.slider("Wind From (°)", 0, 360, 135)
H = st.sidebar.number_input("Release Height (H)", value=80.0)

st.sidebar.write("Click to simulate:")

if st.sidebar.button("Generate Plume"):
    st.subheader(f"Plume Simulation: {location}")
    m = plume(lat0, lon0, Q, U, wind_from, H)
    st_data = st_folium(m, width=1200, height=650)
else:
    st.info("Select parameters and click **Generate Plume**.")
