import glob
import polars as pl

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- TUNABLES ----------------------------------------------------
SAMPLE_RATE_HZ = 20          # match logger_v2.py
WINDOW_SECONDS = 10          # show last N seconds
MAX_FILES_TO_READ = 5        # safety so we don't read entire history
REFRESH_MS = 200             # dashboard refresh interval (200 ms = 5 FPS)
# -----------------------------------------------------------------


def load_latest_window():
    """Load the last WINDOW_SECONDS of data from the newest Parquet files."""
    files = sorted(glob.glob("data/parquet/*.parquet"))
    if not files:
        return pl.DataFrame()

    # Read only the last few files to keep it snappy
    files_to_read = files[-MAX_FILES_TO_READ:]

    df_list = []
    for f in files_to_read:
        try:
            df_list.append(pl.read_parquet(f))
        except Exception as e:
            print(f"[WARN] Could not read {f}: {e}")

    if not df_list:
        return pl.DataFrame()

    df = pl.concat(df_list)

    # How many samples to keep for the rolling window
    window_samples = int(SAMPLE_RATE_HZ * WINDOW_SECONDS)
    if df.height > window_samples:
        df = df.tail(window_samples)

    return df


app = Dash(__name__)

app.layout = html.Div(
    style={"backgroundColor": "#f8fafc", "padding": "10px"},
    children=[
        html.H2("Live Sensor Dashboard", style={"marginBottom": "10px"}),
        dcc.Graph(id="live-graph", style={"height": "90vh"}),
        dcc.Interval(id="timer", interval=REFRESH_MS, n_intervals=0),
    ],
)


@app.callback(
    Output("live-graph", "figure"),
    Input("timer", "n_intervals"),
)
def update_graph(n):
    df = load_latest_window()
    if df.is_empty():
        return go.Figure(layout_title_text="Waiting for data…")

    # X-axis: you can switch to timestamp if you prefer
    x = list(range(df.height))

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.4, 0.4, 0.2],
        subplot_titles=("Acceleration (m/s²)", "Gyro (°/s)", "Temperature (°C)"),
    )

    # --- Accel subplot -------------------------------------------------
    fig.add_trace(
        go.Scatter(x=x, y=df["accel_x"], mode="lines", name="accel_x"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=x, y=df["accel_y"], mode="lines", name="accel_y"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=x, y=df["accel_z"], mode="lines", name="accel_z"),
        row=1,
        col=1,
    )

    # --- Gyro subplot --------------------------------------------------
    fig.add_trace(
        go.Scatter(x=x, y=df["gyro_x"], mode="lines", name="gyro_x"),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=x, y=df["gyro_y"], mode="lines", name="gyro_y"),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=x, y=df["gyro_z"], mode="lines", name="gyro_z"),
        row=2,
        col=1,
    )

    # --- Temp subplot --------------------------------------------------
    fig.add_trace(
        go.Scatter(x=x, y=df["temp_c"], mode="lines", name="temp_c"),
        row=3,
        col=1,
    )

    fig.update_layout(
        margin=dict(l=50, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        hovermode="x unified",
    )

    fig.update_xaxes(title_text=f"Samples (last {WINDOW_SECONDS}s)", row=3, col=1)

    return fig


if __name__ == "__main__":
    # host=0.0.0.0 so you can view from your laptop
    app.run(host="0.0.0.0", port=8050)