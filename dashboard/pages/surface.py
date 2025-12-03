import dash
from dash import html, dcc
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from functools import lru_cache

from model import load_master

dash.register_page(__name__, path="/surface", name="Price Surface")

# --- Data preparation -----------------------------------------------------


@lru_cache(maxsize=1)
def get_surface_data():
    """
    Lazily load and preprocess the master EQR data used for the 3D surface.

    Returns (df, price_col).
    """
    try:
        df = load_master()

        # Ensure datetime exists and is parsed
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        else:
            datetime_cols = [
                c for c in df.columns if "date" in c.lower() or "time" in c.lower()
            ]
            if datetime_cols:
                df["datetime"] = pd.to_datetime(
                    df[datetime_cols[0]], errors="coerce"
                )
            else:
                df["datetime"] = pd.NaT

        df = df.dropna(subset=["datetime"])

        # Choose price column
        if "standardized_price" in df.columns:
            price_col = "standardized_price"
        elif "charge" in df.columns:
            price_col = "charge"
        else:
            price_col = None

        return df, price_col

    except Exception as e:
        print(f"Error preparing surface data: {e}")
        return pd.DataFrame(), None


@lru_cache(maxsize=1)
def build_surface_figure():
    """
    Build the 3D price surface figure.

    Cached so the heavy 3D figure construction only happens once per process.
    """
    df, price_col = get_surface_data()

    if df.empty or price_col is None:
        return go.Figure().update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={"visible": False},
            yaxis={"visible": False},
        )

    # 1. Create a pivot table: Index=Hour, Columns=Month, Values=Price
    df = df.copy()
    df["month"] = df["datetime"].dt.month
    df["hour"] = df["datetime"].dt.hour

    pivot = df.pivot_table(
        index="hour", columns="month", values=price_col, aggfunc="mean"
    )

    # Fill missing values to ensure smooth surface
    pivot = pivot.interpolate(method="linear", axis=0).fillna(0)

    # X = Months (1..12), Y = Hours (0..23)
    x_vals = pivot.columns
    y_vals = pivot.index
    z_vals = pivot.values

    # --- HOLOGRAPHIC STYLE SURFACE ---
    fig = go.Figure(
        data=[
            go.Surface(
                z=z_vals,
                x=x_vals,
                y=y_vals,
                colorscale="Electric",  # Neon / Cyberpunk scale
                opacity=0.9,
                contours_z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor="limegreen",
                    project_z=True,  # Casts the heatmap shadow on the floor
                ),
                colorbar=dict(title="Price ($)", thickness=15, x=0.9),
            )
        ]
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(
            text="Hourly Price Terrain (Hologram)",
            x=0.5,
            font=dict(family="Orbitron", size=20, color="#22d3ee"),
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        scene=dict(
            # Turn off background walls to make it float
            xaxis=dict(
                title="Month",
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(34, 211, 238, 0.2)",  # Faint cyan grid
                showbackground=False,
                tickmode="linear",
                dtick=1,
            ),
            yaxis=dict(
                title="Hour of Day",
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(34, 211, 238, 0.2)",
                showbackground=False,
            ),
            zaxis=dict(
                title="Price ($)",
                backgroundcolor="rgba(0,0,0,0)",
                gridcolor="rgba(34, 211, 238, 0.2)",
                showbackground=False,
            ),
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.2)),  # Nice isometric view
        ),
    )

    return fig


# --- Layout ---------------------------------------------------------------


def layout():
    return html.Div(
        style={"maxWidth": "1200px", "margin": "16px auto 32px auto", "padding": "0 16px"},
        children=[
            html.Div(
                className="glass-card",
                children=[
                    html.H2("Market Price Topography"),
                    html.P(
                        "3D Holographic view of average prices across time of day and year. "
                        "Rotate the model to spot structural high-price ridges.",
                        className="text-muted",
                        style={"fontSize": "0.9rem"},
                    ),
                    dcc.Graph(
                        id="price-surface",
                        className="dash-graph",
                        style={"height": "75vh", "borderRadius": "16px"},
                        config={"displayModeBar": False},
                        figure=build_surface_figure(),
                    ),
                ],
            ),
        ],
    )
