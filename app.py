import dash
from dash import ctx

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


position_colors = {
    "DF": "#636EFA",
    "DF,FW": "#EF553B",
    "DF,MF": "#00CC96",
    "FW": "#AB63FA",
    "FW,DF": "#FFA15A",
    "FW,MF": "#19D3F3",
    "GK": "#FF6692",
    "MF": "#B6E880",
    "MF,DF": "#FF97FF",
    "MF,FW": "#FECB52",
}

# For the basic layout of Dash, I have used the documentation "https://dash.plotly.com/layout" for reference.
# Initializing the Dash app
app = dash.Dash(__name__)
server = app.server

# Things listed in this will be displayed on the dashboard.
app.layout = html.Div(
    [
        # PAGE TITLE
        html.H1(
            "Defensive Performance Analysis Dashboard",
            style={
                "textAlign": "center",
                "marginBottom": "20px",
                "fontFamily": "Arial, sans-serif",
            },
        ),
        # MAIN CONTAINER
        html.Div(
            [
                # FILTER CARD
                html.Div(
                    [
                        html.Label(
                            "Select League",
                            style={
                                "fontWeight": "bold",
                                "display": "block",
                                "marginBottom": "8px",
                            },
                        ),
                        dcc.Dropdown(
                            id="league-filter",
                            options=[
                                {"label": league, "value": league}
                                for league in sorted(df["Comp"].unique())
                            ],
                            placeholder="Choose a league",
                        ),
                        html.Button(
                            "Reset Filters",
                            id="reset-button",
                            n_clicks=0,
                            style={
                                "marginTop": "12px",
                                "padding": "8px 14px",
                                "border": "none",
                                "borderRadius": "6px",
                                "backgroundColor": "#444",
                                "color": "white",
                                "cursor": "pointer",
                            },
                        ),
                    ],
                    style={
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "10px",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                        "marginBottom": "20px",
                    },
                ),
                # TOP ROW: SCATTER + SIDEBAR
                html.Div(
                    [
                        # SCATTER (LEFT)
                        html.Div(
                            [dcc.Graph(id="scatter-plot")],
                            style={
                                "width": "72%",
                                "backgroundColor": "white",
                                "padding": "15px",
                                "borderRadius": "10px",
                                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                            },
                        ),
                        # SIDEBAR (RIGHT)
                        html.Div(
                            [
                                html.H4("Legend", style={"marginBottom": "10px"}),
                                html.P("Color: Player Position"),
                                html.P("Size: Minutes Played"),
                                html.H4("Interactions", style={"marginTop": "16px"}),
                                html.P("• Select league to filter all views"),
                                html.P("• Click on a bar to filter by position"),
                                html.P("• Hover over points to see player details"),
                            ],
                            style={
                                "width": "25%",
                                "backgroundColor": "white",
                                "padding": "15px",
                                "borderRadius": "10px",
                                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                            },
                        ),
                    ],
                    style={"display": "flex", "gap": "20px", "marginBottom": "20px"},
                ),
                # BOTTOM ROW
                html.Div(
                    [
                        # BAR CHART CARD
                        html.Div(
                            [dcc.Graph(id="bar-chart")],
                            style={
                                "width": "50%",
                                "backgroundColor": "white",
                                "padding": "15px",
                                "borderRadius": "10px",
                                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                            },
                        ),
                        # TABLE CARD
                        html.Div(
                            [dcc.Graph(id="top-players-table")],
                            style={
                                "width": "50%",
                                "backgroundColor": "white",
                                "padding": "15px",
                                "borderRadius": "10px",
                                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "gap": "20px",
                        "marginBottom": "20px",
                    },
                ),
                # SMALL INFO BOX
                # html.Div(
                #     [
                #         html.H4("Legend", style={"marginBottom": "10px"}),
                #         html.P("Color: Player Position", style={"margin": "4px 0"}),
                #         html.P("Size: Minutes Played", style={"margin": "4px 0"}),
                #         html.H4(
                #             "Interactions",
                #             style={"marginTop": "16px", "marginBottom": "10px"},
                #         ),
                #         html.P(
                #             "• Select league to filter all views",
                #             style={"margin": "4px 0"},
                #         ),
                #         html.P(
                #             "• Click on a bar to filter by position",
                #             style={"margin": "4px 0"},
                #         ),
                #         html.P(
                #             "• Hover over points to see player details",
                #             style={"margin": "4px 0"},
                #         ),
                #     ],
                #     style={
                #         "backgroundColor": "white",
                #         "padding": "15px",
                #         "borderRadius": "10px",
                #         "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                #         "width": "320px",
                #     },
                # ),
            ],
            style={"maxWidth": "1200px", "margin": "0 auto", "padding": "20px"},
        ),
    ],
    style={"backgroundColor": "#f4f6f9", "minHeight": "100vh", "padding": "20px"},
)


# For the callback functionality, I have used the documentation "https://dash.plotly.com/basic-callbacks" for reference.
# We will be using callbacks to update the graphs whenever the league in the dropdown is changed.
@app.callback(
    [
        Output("scatter-plot", "figure"),
        Output("bar-chart", "figure"),
        Output("top-players-table", "figure"),
    ],
    [
        Input("league-filter", "value"),
        Input("bar-chart", "clickData"),
        Input("reset-button", "n_clicks"),
    ],
)
def update_dashboard(selected_league, click_data, reset_clicks):

    # If no league is selected, it will show the graph for all the leagues. Else, it will only keep the rows  where "Comp" matches the league.
    if selected_league is None:
        league_filtered_df = df
    else:
        league_filtered_df = df[df["Comp"] == selected_league]
    filtered_df = league_filtered_df.copy()

    # Filter data by clicked position from bar chart
    selected_position = None
    triggered_id = ctx.triggered_id

    if triggered_id == "bar-chart" and click_data and "points" in click_data:
        selected_position = click_data["points"][0]["x"]

    if selected_position:
        filtered_df = filtered_df[filtered_df["Pos"] == selected_position]

    # Used the documentation "https://plotly.com/python/line-and-scatter/" to create the scatter plot.
    # Using plotly to create scatter plot which displays the relationship between tackles per 90 and interceptions per 90.
    title_text = "Player Defensive Activity Distribution"

    if selected_position:
        title_text += f" | Position: {selected_position}"
    else:
        title_text += " | All Positions"
    scatter_fig = px.scatter(
        filtered_df,
        x="Tkl_per90",
        y="Int_per90",
        color="Pos",
        color_discrete_map=position_colors,
        size="Min",
        hover_name="Player",
        hover_data={
            "Pos": True,
            "Comp": True,
            "Min": True,
            "Tkl_per90": ":.2f",
            "Int_per90": ":.2f",
            "DefActions_per90": ":.2f",
        },
        title=title_text,
    )

    scatter_fig.update_traces(marker=dict(opacity=0.7))

    scatter_fig.update_layout(
        height=500,
        xaxis_title="Tackles per 90",
        yaxis_title="Interceptions per 90",
        title_font=dict(size=20),
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14),
        margin=dict(l=40, r=20, t=60, b=40),
    )

    # Used the documentation "https://plotly.com/python/bar-charts/" to create the bar chart.
    # Using plotly to create bar chart which shows the average defensive actions per 90 for each position.
    avg_by_position = league_filtered_df.groupby("Pos", as_index=False)[
        "DefActions_per90"
    ].mean()

    # Create custom bar colors
    if selected_position:
        custom_colors = []
        for pos in avg_by_position["Pos"]:
            if pos == selected_position:
                custom_colors.append(position_colors.get(pos, "#636EFA"))
            else:
                custom_colors.append("#D3D3D3")
    else:
        custom_colors = [
            position_colors.get(pos, "#636EFA") for pos in avg_by_position["Pos"]
        ]

    bar_fig = px.bar(
        avg_by_position,
        x="Pos",
        y="DefActions_per90",
        title="Defensive Contribution Across Player Positions",
    )

    bar_fig.update_traces(
        marker_color=custom_colors, marker_line_width=1.5, marker_line_color="black"
    )

    bar_fig.update_layout(
        xaxis_title="Player Position",
        yaxis_title="Average Defensive Actions per 90 Minutes",
        title_font=dict(size=18),
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14),
        height=350,
        margin=dict(l=40, r=20, t=60, b=40),
        showlegend=False,
    )

    # "https://plotly.com/python/table/" to create the table.
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

    table_fig.update_layout(
        title="Top Defensive Performers (Ranked by Actions per 90)",
        title_font=dict(size=18),
        height=350,
        margin=dict(l=10, r=10, t=60, b=10),
    )

    return scatter_fig, bar_fig, table_fig


# Run app
if __name__ == "__main__":
    app.run(debug=True)
