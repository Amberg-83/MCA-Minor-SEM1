import streamlit as st
import folium
import numpy as np
import math
import time
from folium.plugins import HeatMap

st.set_page_config(page_title="Gaussian Plume Model", layout="wide")

# -------------------------------------------
# Helper function to show folium map permanently
# -------------------------------------------
def show_map(m):
    html = m.get_root().render()
    st.components.v1.html(html, height=600)

# -------------------------------------------
# Simple Gaussian Plume Function
# -------------------------------------------
def plume(lat0, lon0, Q, U, wind_from, H):

    wind_to = (wind_from + 180) % 360

    x = np.linspace(100, 15000, 100)
    y = np.linspace(-7500, 7500, 100)
    X, Y = np.meshgrid(x, y)

    sy = 0.08 * X
    sz = 0.06 * X

    C = (Q / (2 * np.pi * U * sy * sz)) * \
        np.exp(-(Y**2)/(2*sy**2)) * \
        np.exp(-(H**2)/(2*sz**2))

    C[X < 100] = 0

    angle = math.radians(wind_to)
    dx = X * math.cos(angle) - Y * math.sin(angle)
    dy = X * math.sin(angle) + Y * math.cos(angle)

    lat = lat0 + dy/111000
    lon = lon0 + dx/(111000 * math.cos(math.radians(lat0)))

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
# Simple Animation
# -------------------------------------------
def animate_plume(lat0, lon0, Q, U, wind_from, H):
    container = st.empty()

    for factor in np.linspace(0.2, 1.0, 12):
        m = plume(lat0, lon0, Q*factor, U, wind_from, H)

        with container:
            show_map(m)

        time.sleep(0.3)

# -------------------------------------------
# UI
# -------------------------------------------
st.title("Gaussian Plume Simulation (Stable Version)")

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
    show_map(m)

if st.button("Animate Plume Spread"):
    animate_plume(lat0, lon0, Q, U, wind_from, H)
