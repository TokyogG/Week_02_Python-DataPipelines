import math
import threading
import time
from collections import deque

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from src.sensors.mpu6050 import MPU6050

# ---- CONFIG -----------------------------------------------------

SAMPLE_RATE_HZ = 50
WINDOW_SECONDS = 10
BUFFER_LEN = SAMPLE_RATE_HZ * WINDOW_SECONDS
REFRESH_MS = 200  # 5 FPS

buffer = deque(maxlen=BUFFER_LEN)


# ---- SENSOR THREAD ----------------------------------------------

def sensor_loop():
    sensor = MPU6050()
    period = 1.0 / SAMPLE_RATE_HZ
    print(f"[INFO] Starting sensor loop at {SAMPLE_RATE_HZ} Hz")

    while True:
        sample = sensor.read()
        sample["t"] = time.time()
        buffer.append(sample)
        # debug: show that sensor is alive
        print("[SENSOR]", sample)
        time.sleep(period)


threading.Thread(target=sensor_loop, daemon=True).start()


def buffer_to_arrays():
    if not buffer:
        return None
    data = list(buffer)
    t = np.array([d["t"] for d in data])
    ax = np.array([d["accel_x"] for d in data])
    ay = np.array([d["accel_y"] for d in data])
    az = np.array([d["accel_z"] for d in data])
    gx = np.array([d["gyro_x"] for d in data])
    gy = np.array([d["gyro_y"] for d in data])
    gz = np.array([d["gyro_z"] for d in data])
    temp = np.array([d["temp_c"] for d in data])
    return t, ax, ay, az, gx, gy, gz, temp


def compute_kpis(ax, ay, az, gx, gy, gz, temp):
    accel_mag = np.sqrt(ax**2 + ay**2 + az**2)
    gyro_mag = np.sqrt(gx**2 + gy**2 + gz**2)

    rms_accel = float(np.sqrt(np.mean(accel_mag**2)))
    peak_gyro = float(np.max(np.abs(gyro_mag)))
    mean_temp = float(np.mean(temp))

    state = "STILL"
    if rms_accel > 2.0:
        state = "MOVING"
    if rms_accel > 5.0:
        state = "SHAKING"

    return rms_accel, peak_gyro, mean_temp, state


def latest_pitch_roll(ax, ay, az):
    # Use last sample
    gax, gay, gaz = ax[-1] / 9.81, ay[-1] / 9.81, az[-1] / 9.81
    roll = math.atan2(gay, gaz)
    pitch = math.atan2(-gax, math.sqrt(gay**2 + gaz**2))
    # exaggerate slightly
    return pitch * 1.5, roll * 1.5


def make_cube(pitch, roll):
    s = 0.5
    verts = np.array([
        [-s, -s, -s],
        [ s, -s, -s],
        [ s,  s, -s],
        [-s,  s, -s],
        [-s, -s,  s],
        [ s, -s,  s],
        [ s,  s,  s],
        [-s,  s,  s],
    ])

    Rx = np.array([
        [1, 0, 0],
        [0, math.cos(roll), -math.sin(roll)],
        [0, math.sin(roll),  math.cos(roll)],
    ])
    Ry = np.array([
        [ math.cos(pitch), 0, math.sin(pitch)],
        [ 0,               1, 0],
        [-math.sin(pitch), 0, math.cos(pitch)],
    ])

    R = Ry @ Rx
    Rv = verts @ R.T

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]

    xs, ys, zs = [], [], []
    for i, j in edges:
        xs += [Rv[i, 0], Rv[j, 0], None]
        ys += [Rv[i, 1], Rv[j, 1], None]
        zs += [Rv[i, 2], Rv[j, 2], None]

    fig = go.Figure(
        data=[go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(width=6))]
    )
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-1, 1], visible=False),
            yaxis=dict(range=[-1, 1], visible=False),
            zaxis=dict(range=[-1, 1], visible=False),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#111827",
    )
    return fig


# ---- DASH APP ---------------------------------------------------

app = Dash(__name__)

card_style = {
    "backgroundColor": "#1f2933",
    "color": "#e5e7eb",
    "padding": "10px 12px",
    "margin": "4px",
    "borderRadius": "8px",
    "minWidth": "160px",
    "textAlign": "center",
}

app.layout = html.Div(
    style={"backgroundColor": "#111827", "color": "#e5e7eb", "padding": "12px"},
    children=[
        html.H2("Live Sensor Dashboard – PRO", style={"marginBottom": "8px"}),
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "marginBottom": "8px"},
            children=[
                html.Div(
                    [html.Div("RMS Accel (m/s²)", style={"fontSize": "0.8rem"}),
                     html.Div(id="kpi-rms", style={"fontSize": "1.4rem"})],
                    style=card_style,
                ),
                html.Div(
                    [html.Div("Peak Gyro (°/s)", style={"fontSize": "0.8rem"}),
                     html.Div(id="kpi-gyro", style={"fontSize": "1.4rem"})],
                    style=card_style,
                ),
                html.Div(
                    [html.Div("Temp (°C)", style={"fontSize": "0.8rem"}),
                     html.Div(id="kpi-temp", style={"fontSize": "1.4rem"})],
                    style=card_style,
                ),
                html.Div(
                    [html.Div("Motion State", style={"fontSize": "0.8rem"}),
                     html.Div(id="kpi-state", style={"fontSize": "1.4rem"})],
                    style=card_style,
                ),
            ],
        ),
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "8px"},
            children=[
                dcc.Graph(id="ts-graph", style={"height": "70vh"}),
                dcc.Graph(id="cube-graph", style={"height": "70vh"}),
            ],
        ),
        dcc.Interval(id="timer", interval=REFRESH_MS, n_intervals=0),
    ],
)


@app.callback(
    [
        Output("ts-graph", "figure"),
        Output("cube-graph", "figure"),
        Output("kpi-rms", "children"),
        Output("kpi-gyro", "children"),
        Output("kpi-temp", "children"),
        Output("kpi-state", "children"),
    ],
    Input("timer", "n_intervals"),
)
def update(n):
    arrays = buffer_to_arrays()
    if arrays is None:
        empty = go.Figure().update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827"
        )
        return empty, empty, "-", "-", "-", "No data"

    t, ax, ay, az, gx, gy, gz, temp = arrays
    t_rel = t - t[0]

    # debug: show callback is running
    print("[DASH]", n, "samples:", len(t))

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.4, 0.4, 0.2],
        subplot_titles=("Acceleration (m/s²)", "Gyro (°/s)", "Temperature (°C)"),
    )

    fig.add_trace(go.Scatter(x=t_rel, y=ax, mode="lines", name="accel_x"), row=1, col=1)
    fig.add_trace(go.Scatter(x=t_rel, y=ay, mode="lines", name="accel_y"), row=1, col=1)
    fig.add_trace(go.Scatter(x=t_rel, y=az, mode="lines", name="accel_z"), row=1, col=1)

    fig.add_trace(go.Scatter(x=t_rel, y=gx, mode="lines", name="gyro_x"), row=2, col=1)
    fig.add_trace(go.Scatter(x=t_rel, y=gy, mode="lines", name="gyro_y"), row=2, col=1)
    fig.add_trace(go.Scatter(x=t_rel, y=gz, mode="lines", name="gyro_z"), row=2, col=1)

    fig.add_trace(go.Scatter(x=t_rel, y=temp, mode="lines", name="temp_c"), row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#e5e7eb"),
        hovermode="x unified",
        margin=dict(l=50, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(title_text="Time (s, last 10s)", row=3, col=1)

    rms_accel, peak_gyro, mean_temp, state = compute_kpis(ax, ay, az, gx, gy, gz, temp)
    pitch, roll = latest_pitch_roll(ax, ay, az)
    cube_fig = make_cube(pitch, roll)

    return (
        fig,
        cube_fig,
        f"{rms_accel:0.2f}",
        f"{peak_gyro:0.1f}",
        f"{mean_temp:0.2f}",
        state,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8051)