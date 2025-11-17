import streamlit as st
import folium
import numpy as np
import math
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import time

st.set_page_config(page_title="Gaussian Plume Model", layout="wide")

# -------------------------------------------
# SIMPLE GAUSSIAN PLUME FUNCTION
# -------------------------------------------
def plume(lat0, lon0, Q, U, wind_from, H):

    wind_to = (wind_from + 180) % 360

    x = np.linspace(100, 15000, 100)
    y = np.linspace(-7500, 7500, 100)
    X, Y = np.meshgrid(x, y)

    sy = 0.08 * X
    sz = 0.06 * X

    C = (Q / (2 * np.pi * U * sy * sz)) * \
        np.exp(-0.5 * (Y/sy)**2) * \
        np.exp(-0.5 * (H/sz)**2)

    C[X < 100] = 0

    angle = math.radians(wind_to)

    dx = X * math.cos(angle) - Y * math.sin(angle)
    dy = X * math.sin(angle) + Y * math.cos(angle)

    lat = lat0 + dy / 111000
    lon = lon0 + dx / (111000 * math.cos(math.radians(lat0)))

    cmax = C.max()

    heat = [
        [lat[i, j], lon[i, j], float(C[i, j]/cmax)]
        for i in range(100) for j in range(100)
        if C[i, j] > cmax * 0.001
    ]

    m = folium.Map(location=[lat0, lon0], zoom_start=8)
    HeatMap(heat, radius=15, blur=12).add_to(m)
    folium.Marker([lat0, lon0], popup="Source").add_to(m)

    return m


# -------------------------------------------
# ANIMATION FUNCTION (VERY SIMPLE)
# -------------------------------------------
def animate_plume(lat0, lon0, Q, U, wind_from, H):

    container = st.empty()

    for factor in np.linspace(0.1, 1.0, 15):

        x = np.linspace(100, 15000, 100)
        y = np.linspace(-7500, 7500, 100)
        X, Y = np.meshgrid(x, y)

        sy = 0.08 * X * factor
        sz = 0.06 * X * factor

        C = (Q / (2 * np.pi * U * sy * sz)) * \
            np.exp(-0.5 * (Y/sy)**2) * \
            np.exp(-0.5 * (H/sz)**2)

        C[X < 100] = 0
        angle = math.radians((wind_from + 180) % 360)

        dx = X * math.cos(angle) - Y * math.sin(angle)
        dy = X * math.sin(angle) + Y * math.cos(angle)

        lat = lat0 + dy / 111000
        lon = lon0 + dx / (111000 * math.cos(math.radians(lat0)))

        cmax = C.max()
        heat = [
            [lat[i, j], lon[i, j], float(C[i, j]/cmax)]
            for i in range(100) for j in range(100)
            if C[i, j] > cmax * 0.001
        ]

        m = folium.Map(location=[lat0, lon0], zoom_start=8)
        HeatMap(heat, radius=15, blur=12).add_to(m)
        folium.Marker([lat0, lon0], popup="Source").add_to(m)

        with container:
            st_folium(m, width=1100, height=600)

        time.sleep(0.25)


# -------------------------------------------
# UI INPUTS (VERY SIMPLE)
# -------------------------------------------
st.title("Gaussian Plume Simulation (Simple Version)")

case = st.selectbox("Choose Case Study", ["Fukushima", "Chernobyl"])

if case == "Fukushima":
    lat0, lon0 = 37.421, 141.032
else:
    lat0, lon0 = 51.389, 30.099

Q = st.number_input("Emission Rate (Q)", value=1e13)
U = st.number_input("Wind Speed (U)", value=4.0)
wind_from = st.slider("Wind Direction (°)", 0, 360, 135)
H = st.number_input("Release Height (H)", value=80.0)

if st.button("Generate Plume"):
    m = plume(lat0, lon0, Q, U, wind_from, H)
    st_folium(m, width=1100, height=600)

if st.button("Animate Plume Spread"):
    st.write("Animating plume spread...")
    animate_plume(lat0, lon0, Q, U, wind_from, H)
