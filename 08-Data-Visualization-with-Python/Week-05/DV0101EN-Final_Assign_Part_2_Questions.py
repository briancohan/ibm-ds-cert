#!/usr/bin/env python
# coding: utf-8
"""
Date: The date of the observation.
Recession: A binary variable indicating recession perion; 1 means it was recession, 0 means it was normal.
Automobile_Sales: The number of vehicles sold during the period.
GDP: The per capita GDP value in USD.
Unemployment_Rate: The monthly unemployment rate.
Consumer_Confidence: A synthetic index representing consumer confidence, which can impact consumer spending and automobile purchases.
Seasonality_Weight: The weight representing the seasonality effect on automobile sales during the period.
Price: The average vehicle price during the period.
Advertising_Expenditure: The advertising expenditure of the company.
Vehicle_Type: The type of vehicles sold; Supperminicar, Smallfamiliycar, Mediumfamilycar, Executivecar, Sports.
Competition: The measure of competition in the market, such as the number of competitors or market share of major manufacturers.
Month: Month of the observation extracted from Date.
Year: Year of the observation extracted from Date.
"""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

data = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
)

app = dash.Dash(__name__)

app.title = "Automobile Sales Statistics Dashboard"

YEARLY_STATS = "Yearly Statistics"
RECESSION_STATS = "Recession Period Statistics"

DIV_SELECT_YEAR = "select-year"
DIV_OUTPUT_CONTAINER = "output-container"
DIV_DROPDOWN_STATS = "dropdown-statistics"

dropdown_options = [
    {
        "label": YEARLY_STATS,
        "value": YEARLY_STATS,
    },
    {
        "label": RECESSION_STATS,
        "value": RECESSION_STATS,
    },
]

year_list = [i for i in range(1980, 2024, 1)]

app.layout = html.Div(
    [
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={
                "color": "#503D36",
                "font-size": 24,
            },
        ),
        html.Div(
            [
                html.Label("Select Statistics:"),
                dcc.Dropdown(
                    id=DIV_DROPDOWN_STATS,
                    options=dropdown_options,
                    value="Select Statistics",
                    placeholder="Select a report type",
                    style={
                        "width": "80%",
                        "padding": "3px",
                        "font-size": "20px",
                        "text-align-last": "center",
                    },
                ),
            ]
        ),
        html.Div(
            dcc.Dropdown(
                id=DIV_SELECT_YEAR,
                options=[{"label": i, "value": i} for i in year_list],
                value="...",
            )
        ),
        html.Div(
            [
                html.Div(
                    id=DIV_OUTPUT_CONTAINER,
                    className="chart-grid",
                    style={"display": "flex"},
                ),
            ]
        ),
    ]
)


@app.callback(
    Output(component_id=DIV_SELECT_YEAR, component_property="disabled"),
    Input(component_id=DIV_DROPDOWN_STATS, component_property="value"),
)
def update_input_container(selected_statistics):
    return selected_statistics == RECESSION_STATS


@app.callback(
    Output(component_id=DIV_OUTPUT_CONTAINER, component_property="children"),
    [
        Input(component_id=DIV_SELECT_YEAR, component_property="value"),
        Input(component_id=DIV_DROPDOWN_STATS, component_property="value"),
    ],
)
def update_output_container(input_year, selected_statistics):
    if selected_statistics == RECESSION_STATS:

        recession_data = data[data["Recession"] == 1]

        R_chart1_data = (
            recession_data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        )
        R_chart2_data = (
            recession_data.groupby(["Year", "Vehicle_Type"])["Automobile_Sales"]
            .mean()
            .reset_index()
        )
        R_chart3_data = (
            recession_data.groupby(["Vehicle_Type"])["Advertising_Expenditure"]
            .sum()
            .reset_index()
        )
        R_chart4_data = (
            recession_data.groupby(["Year"])["unemployment_rate"].mean().reset_index()
        )

        # Plot 1 Automobile sales fluctuate over Recession Period (year wise)
        R_chart1 = px.line(
            R_chart1_data,
            x="Year",
            y="Automobile_Sales",
            title="Average Automobile Sales fluctuation over Recession Period",
        )

        # Plot 2 Calculate the average number of vehicles sold by vehicle type
        R_chart2 = px.line(
            R_chart2_data,
            x="Year",
            y="Automobile_Sales",
            color="Vehicle_Type",
            title="Average Automobile Sales fluctuation over Recession Period",
        )

        # Plot 3 Pie chart for total expenditure share by vehicle type during recessions
        R_chart3 = px.pie(
            R_chart3_data,
            values="Advertising_Expenditure",
            names="Vehicle_Type",
            title="Total Advertisement Expenditure during Recession Period",
        )

        # Plot 4 bar chart for the effect of unemployment rate on vehicle type and sales
        R_chart4 = px.bar(
            R_chart4_data,
            x="Year",
            y="unemployment_rate",
            title="Average Unemployment Rate over Recession Period",
        )

        charts = [R_chart1, R_chart2, R_chart3, R_chart4]

    elif input_year and selected_statistics == YEARLY_STATS:
        yearly_data = data[data["Year"] == input_year]

        Y_chart1_data = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        Y_chart3_data = (
            yearly_data.groupby("Month")["Automobile_Sales"].mean().reset_index()
        )
        Y_chart4_data = (
            yearly_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
            .sum()
            .reset_index()
        )

        # plot 1 Yearly Automobile sales using line chart for the whole period.
        Y_chart1 = px.line(
            Y_chart1_data,
            x="Year",
            y="Automobile_Sales",
            title="Average Automobile Sales over the years",
        )

        # Plot 2 Total Monthly Automobile sales using line chart.
        Y_chart2 = px.line(
            yearly_data,
            x="Month",
            y="Automobile_Sales",
            title=f"Automobile Sales over the months in the year {input_year}",
        )

        # Plot bar chart for average number of vehicles sold during the given year
        Y_chart3 = px.bar(
            Y_chart3_data,
            x="Month",
            y="Automobile_Sales",
            title=f"Average Vehicles Sold by Vehicle Type in the year {input_year}",
        )

        # Total Advertisement Expenditure for each vehicle using pie chart
        Y_chart4 = px.pie(
            Y_chart4_data,
            values="Advertising_Expenditure",
            names="Vehicle_Type",
            title=f"Total Advertisement Expenditure during the year {input_year}",
        )

        charts = [Y_chart1, Y_chart2, Y_chart3, Y_chart4]

    else:
        return None

    return [
        html.Div(
            className="chart-item",
            children=[
                html.Div(children=dcc.Graph(figure=charts[0])),
                html.Div(children=dcc.Graph(figure=charts[1])),
            ],
            style={},
        ),
        html.Div(
            className="chart-item",
            children=[
                html.Div(children=dcc.Graph(figure=charts[2])),
                html.Div(children=dcc.Graph(figure=charts[3])),
            ],
            style={},
        ),
    ]


if __name__ == "__main__":
    app.run_server(debug=True)
