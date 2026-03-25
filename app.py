import dash

# ctx lets us know which input trigerred the callback.
from dash import ctx

# Importing dcc i.e dash core components for dropdown and graph elements.
from dash import dcc, html

# They are used for callbacks. Automatically updates the ouput when input is changed.
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

# Changing short position names to full names for better readibility.
position_label_map = {
    "DF": "Defender",
    "MF": "Midfielder",
    "FW": "Forward",
    "GK": "Goalkeeper",
    "DF,MF": "Defender / Midfielder",
    "MF,DF": "Midfielder / Defender",
    "DF,FW": "Defender / Forward",
    "FW,DF": "Forward / Defender",
    "MF,FW": "Midfielder / Forward",
    "FW,MF": "Forward / Midfielder",
}
# Display-friendly position labels used in hover text and tables.
df["Position Label"] = df["Pos"].map(position_label_map).fillna(df["Pos"])

# We are using this to assign fixed colors for each position. This is done to maintain consistency accross the dashboard.
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

# Reference: Dash layout documentation
# "https://dash.plotly.com/layout" for reference.
# Initializing the Dash app
app = dash.Dash(__name__)
server = app.server

# Things listed in this will be displayed on the dashboard.
app.layout = html.Div(
    [
        # It will create thetop heading of the dashboard.
        html.H1(
            "Defensive Performance Analysis Dashboard",
            style={
                "textAlign": "center",
                "marginBottom": "20px",
                "fontFamily": "Arial, sans-serif",
            },
        ),
        # Main container, it will include all the components of the dashboard.
        html.Div(
            [
                # It will contain a label, dropdown for league selection and the reset button to clear all the filters.
                html.Div(
                    [
                        # Label for the dropdown
                        html.Label(
                            "Select League",
                            style={
                                "fontWeight": "bold",
                                "display": "block",
                                "marginBottom": "8px",
                            },
                        ),
                        # Dropdown for league selection.
                        dcc.Dropdown(
                            id="league-filter",
                            options=[
                                {"label": league, "value": league}
                                for league in sorted(df["Comp"].unique())
                            ],
                            placeholder="Choose a league",
                        ),
                        # Reset filter button
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
                # This container will contain scatter plot on the left side and the legend on the right side.
                html.Div(
                    [
                        # Scatter Plot
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
                        # Legend
                        # Updated the legend text after peer feedback so that the legend is more detailed and informative.
                        html.Div(
                            [
                                html.H4("Legend", style={"marginBottom": "10px"}),
                                html.P(
                                    "Color Encoding:",
                                    style={"fontWeight": "bold", "marginBottom": "4px"},
                                ),
                                html.P(
                                    "Each color represents a player position "
                                    "(Defender, Midfielder, Forward, Goalkeeper, or hybrid roles).",
                                    style={
                                        "marginTop": "0",
                                        "marginBottom": "10px",
                                        "lineHeight": "1.5",
                                    },
                                ),
                                html.P(
                                    "Size Encoding:",
                                    style={"fontWeight": "bold", "marginBottom": "4px"},
                                ),
                                html.P(
                                    "Larger markers represent players with more minutes played.",
                                    style={
                                        "marginTop": "0",
                                        "marginBottom": "10px",
                                        "lineHeight": "1.5",
                                    },
                                ),
                                html.H4(
                                    "Interactions",
                                    style={"marginTop": "16px", "marginBottom": "10px"},
                                ),
                                html.P(
                                    "• Select a league to filter all views",
                                    style={"margin": "4px 0"},
                                ),
                                html.P(
                                    "• Click a bar to filter by position",
                                    style={"margin": "4px 0"},
                                ),
                                html.P(
                                    "• Hover over points to view detailed player statistics",
                                    style={"margin": "4px 0"},
                                ),
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
                # This contaier will contain the br chart on the left side and the table for top 10 players on the right side.
                html.Div(
                    [
                        # Bar Chart
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
                        # Top 10 Players Table
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
            ],
            style={"maxWidth": "1200px", "margin": "0 auto", "padding": "20px"},
        ),
    ],
    style={"backgroundColor": "#f4f6f9", "minHeight": "100vh", "padding": "20px"},
)


# Reference: Dash basic callbacks documentation
# "https://dash.plotly.com/basic-callbacks" for reference.
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

    # If no league is selected, it will show the graph for all the leagues. Else, keep only the rows of the selected league. Then create a copy of the filtered dataframe for further filtering.
    if selected_league is None:
        league_filtered_df = df
    else:
        league_filtered_df = df[df["Comp"] == selected_league]
    filtered_df = league_filtered_df.copy()

    # This will check what caused the callback to trigger.
    selected_position = None
    # Reference: Dash advanced callbacks documentation
    # https://dash.plotly.com/advanced-callbacks
    triggered_id = ctx.triggered_id

    # Reference: Stack Overflow discussion on handling clickData in Dash graphs
    #   https://stackoverflow.com/questions/61308628/dash-plotly-clickdata-to-filter-dataframe
    if triggered_id == "bar-chart" and click_data and "points" in click_data:
        clicked_position_label = click_data["points"][0]["x"]
        reverse_position_map = {v: k for k, v in position_label_map.items()}
        selected_position = reverse_position_map.get(
            clicked_position_label, clicked_position_label
        )

    if selected_position:
        filtered_df = filtered_df[filtered_df["Pos"] == selected_position]

    title_text = "Player Defensive Activity Distribution"

    # In the title the user will see the full position name when selecting a bar graph instead of the short position code.
    if selected_position:
        title_text += f" | Position: {position_label_map.get(selected_position, selected_position)}"
    else:
        title_text += " | All Positions"

    # Reference: Plotly scatter plot documentation
    # "https://plotly.com/python/line-and-scatter/".
    # Using plotly to create scatter plot which displays the relationship between tackles per 90 and interceptions per 90.
    # Scatter plot creation
    scatter_fig = px.scatter(
        filtered_df,
        x="Tkl_per90",
        y="Int_per90",
        color="Pos",
        color_discrete_map=position_colors,
        size="Min",
        hover_name="Player",
        custom_data=[
            "Position Label",
            "Comp",
            "Min",
            "Tkl_per90",
            "Int_per90",
            "DefActions_per90",
        ],
        hover_data={
            "Pos": False,
            "Comp": True,
            "Min": True,
            "Tkl_per90": ":.2f",
            "Int_per90": ":.2f",
            "DefActions_per90": ":.2f",
        },
        title=title_text,
    )

    # This is used to make the overlapping points more visible.
    scatter_fig.update_traces(
        marker=dict(opacity=0.7),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Position: %{customdata[0]}<br>"
            "League: %{customdata[1]}<br>"
            "Minutes Played: %{customdata[2]}<br>"
            "Tackles per 90: %{customdata[3]}<br>"
            "Interceptions per 90: %{customdata[4]}<br>"
            "Defensive Actions per 90: %{customdata[5]}<extra></extra>"
        ),
    )

    # update_layout is used to control the chart height, axis , title, margin etc.
    scatter_fig.update_layout(
        height=500,
        xaxis_title="Tackles per 90",
        yaxis_title="Interceptions per 90",
        title_font=dict(size=20),
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14),
        margin=dict(l=40, r=20, t=60, b=40),
    )

    # It groups players by position and computes the average defensive actions per 90 for each position.
    avg_by_position = league_filtered_df.groupby(
        ["Pos", "Position Label"], as_index=False
    )["DefActions_per90"].mean()

    # If a bar is selected in the bar chart, that bar keeps it original color while the other bars are grayed out.
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

    # Reference: Plotly bar chart documentation
    # "https://plotly.com/python/bar-charts/".
    # Using plotly to create bar chart which shows the average defensive actions per 90 for each position.
    bar_fig = px.bar(
        avg_by_position,
        x="Position Label",
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
    # Reference: Plotly table documentation
    # "https://plotly.com/python/table/"
    # Top 10 players table
    top_10 = filtered_df.sort_values("DefActions_per90", ascending=False).head(10)

    table_fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "Player",
                        "Position",
                        "Tackles/90",
                        "Interceptions/90",
                        "Defensive Actions/90",
                    ],
                    fill_color="lightgray",
                    align="center",
                    font=dict(size=13),
                    height=32,
                ),
                cells=dict(
                    values=[
                        top_10["Player"],
                        top_10["Position Label"],
                        top_10["Tkl_per90"].round(2),
                        top_10["Int_per90"].round(2),
                        top_10["DefActions_per90"].round(2),
                    ],
                    align="center",
                    height=28,
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
