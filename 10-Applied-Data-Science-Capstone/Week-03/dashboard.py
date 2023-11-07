import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv"
df = pd.read_csv(url)
# (56, 13)
# Flight Number
# Date
# Time (UTC)
# Booster Version
# Launch Site
# Payload
# Payload Mass (kg)
# Orbit
# Customer
# Landing Outcome
# class
# Lat
# Long

app = dash.Dash(__name__)
app.title = "SpaceX Launch Records Dashboard"
app.layout = html.Div(
    [
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        html.Div(
            [
                html.Label('Select Launch Site:'),
                dcc.Dropdown(
                    id='site-dropdown',
                    options=[
                        {'label': 'All Sites', 'value': 'ALL'},
                        *[{ 'label': site, 'value': site } for site in df['Launch Site'].unique()]
                    ],
                    value='ALL',
                    placeholder='Select a Launch Site here',
                    searchable=True,
                ),
                html.Div(dcc.Graph(id='success-pie-chart'))
            ]
        ),
        html.Div(
            [
                dcc.RangeSlider(
                    id='payload-slider',
                    min=0,
                    max=df['Payload Mass (kg)'].max(),
                    step=1000,
                    value=[df['Payload Mass (kg)'].min(), df['Payload Mass (kg)'].max()]
                ),
                html.Div(dcc.Graph(id='success-payload-scatter-chart'))
            ]
        )
    ]
)

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(site):
    if site == 'ALL':
        fig = px.pie(
            df,
            values='class',
            names='Launch Site',
            title='Total Success Launches By Site'
        )
    else:
        fig = px.pie(
            df.loc[df['Launch Site'] == site, 'class'].value_counts().sort_index().reset_index(),
            values='count',
            names='class',
            title=f'Total Success Launches for Site {site}'
        )
    return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(site, payload):
    _df = df.loc[
        (df['Payload Mass (kg)'] >= payload[0]) &
        (df['Payload Mass (kg)'] <= payload[1])
    ]

    if site == 'ALL':
        fig = px.scatter(
            df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version',
            title='Correlation Between Payload and Success for All Sites'
        )
    else:
        fig = px.scatter(
            df.loc[
                (df['Launch Site'] == site) &
                (df['Payload Mass (kg)'] >= payload[0]) &
                (df['Payload Mass (kg)'] <= payload[1])
            ],
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version',
            title=f'Correlation Between Payload and Success for Site {site}'
        )
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
