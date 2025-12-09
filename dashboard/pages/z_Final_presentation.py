
import dash
from dash import html

dash.register_page(
    __name__,
    path="/presentation-video",
    name="Final Presentation Video",
)

layout = html.Div(
    className="page-container",
    children=[
        html.Div(
            className="glass-card",
            style={"marginBottom": "24px", "padding": "24px"},
            children=[
                html.H2("Final Presentation – Video"),
                html.P(
                    "This tab lets you watch our STA 160 final presentation directly inside "
                    "the Grid Sentinel dashboard.",
                    className="text-muted",
                    style={"fontSize": "0.95rem"},
                ),
            ],
        ),
        html.Div(
            className="glass-card",
            style={"padding": "24px", "textAlign": "center"},
            children=[
                html.H3("STA160 Final Presentation"),
                html.Video(
                    controls=True,
                    style={
                        "width": "100%",
                        "maxWidth": "960px",
                        "borderRadius": "12px",
                        "outline": "none",
                    },
                    children=[
                        html.Source(
                            src="/assets/STA160_finalpresentation.mp4",
                            type="video/mp4",
                        ),
                        "Your browser does not support the video tag.",
                    ],
                ),
                html.P(
                    "Tip: you can fullscreen the video using the control in the bottom-right corner.",
                    className="text-muted",
                    style={"marginTop": "12px", "fontSize": "0.85rem"},
                ),
            ],
        ),
    ],
)
