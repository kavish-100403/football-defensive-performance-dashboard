import dash

# Importing dcc i.e dash core components for dropdown and graph elements.
from dash import dcc, html

#
from dash.dependencies import Input, Output

# We will be using plotly for scatter and charts.
import plotly.express as px

# We will be using this to make table for top 10 players.
import plotly.graph_objects as go
import pandas as pd

# Loading the football dataset
df = pd.read_csv("dataset.csv")

# Keeping only useful columns which will give us insights about the defensive performance of the players and dropping the rest of the columns.
df = df[["Player", "Pos", "Comp", "Min", "Tkl", "Int", "Clr"]]

# Removing players with low playing time as players who have played less than 300 minutes will not provide meaningful insgihts and may act as outliers in our analysis.
df = df[df["Min"] > 300]

# Creating per 90 metrics to compare players fairly regardless of their total playing time.
df["Tkl_per90"] = df["Tkl"] / (df["Min"] / 90)
df["Int_per90"] = df["Int"] / (df["Min"] / 90)
df["DefActions_per90"] = (df["Tkl"] + df["Int"] + df["Clr"]) / (df["Min"] / 90)

# Initializing the Dash app
app = dash.Dash(__name__)

# Things listed in this will be displayed on the dashboard.
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


# We will be using callbacks to update the graphs whenever the league in the dropdown is changed.
@app.callback(
    [
        Output("scatter-plot", "figure"),
        Output("bar-chart", "figure"),
        Output("top-players-table", "figure"),
    ],
    Input("league-filter", "value"),
)
def update_dashboard(selected_league):

    # If no league is selected, it will show the graph for all the leagues. Else, it will only keep the rows  where "Comp" matches the league.
    if selected_league is None:
        filtered_df = df
    else:
        filtered_df = df[df["Comp"] == selected_league]

    # Using plotly to create scatter plot which displays the relationship between tackles per 90 and interceptions per 90.
    scatter_fig = px.scatter(
        filtered_df,
        x="Tkl_per90",
        y="Int_per90",
        color="Pos",
        size="Min",
        hover_name="Player",
        title="Tackles per 90 vs Interceptions per 90",
    )

    # Using plotly to create bar chart which shows the average defensive actions per 90 for each position.
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
