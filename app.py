import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Load football dataset
df = pd.read_csv("dataset.csv")

# Keep only useful columns
df = df[["Player", "Pos", "Comp", "Min", "Tkl", "Int", "Clr"]]

# Remove players with low playing time
df = df[df["Min"] > 300]

# Create per 90 metrics
df["Tkl_per90"] = df["Tkl"] / (df["Min"] / 90)
df["Int_per90"] = df["Int"] / (df["Min"] / 90)
df["DefActions_per90"] = (df["Tkl"] + df["Int"] + df["Clr"]) / (df["Min"] / 90)

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div(
    [
        html.H1("Defensive Performance Analysis Dashboard"),
        html.Label("Select League"),
        dcc.Dropdown(
            id="league-filter",
            options=[
                {"label": league, "value": league}
                for league in sorted(df["Comp"].unique())
            ],
            placeholder="Choose a league",
        ),
        dcc.Graph(id="scatter-plot"),
        dcc.Graph(id="bar-chart"),
        dcc.Graph(id="top-players-table"),
    ]
)


# Callback to update all views
@app.callback(
    [
        Output("scatter-plot", "figure"),
        Output("bar-chart", "figure"),
        Output("top-players-table", "figure"),
    ],
    Input("league-filter", "value"),
)
def update_dashboard(selected_league):

    # Filter data
    if selected_league is None:
        filtered_df = df
    else:
        filtered_df = df[df["Comp"] == selected_league]

    # Scatterplot
    scatter_fig = px.scatter(
        filtered_df,
        x="Tkl_per90",
        y="Int_per90",
        color="Pos",
        size="Min",
        hover_name="Player",
        title="Tackles per 90 vs Interceptions per 90",
    )

    # Bar chart
    avg_by_position = filtered_df.groupby("Pos", as_index=False)[
        "DefActions_per90"
    ].mean()

    bar_fig = px.bar(
        avg_by_position,
        x="Pos",
        y="DefActions_per90",
        color="Pos",
        title="Average Defensive Actions per 90 by Position",
    )

    # Top 10 players table
    top_10 = filtered_df.sort_values("DefActions_per90", ascending=False).head(10)

    table_fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["Player", "Position", "Tkl/90", "Int/90", "Def Actions/90"],
                    fill_color="lightgray",
                    align="left",
                ),
                cells=dict(
                    values=[
                        top_10["Player"],
                        top_10["Pos"],
                        top_10["Tkl_per90"].round(2),
                        top_10["Int_per90"].round(2),
                        top_10["DefActions_per90"].round(2),
                    ],
                    align="left",
                ),
            )
        ]
    )

    table_fig.update_layout(title="Top 10 Defensive Players")

    return scatter_fig, bar_fig, table_fig


# Run app
if __name__ == "__main__":
    app.run(debug=True)
