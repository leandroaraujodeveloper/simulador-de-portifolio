# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from financial import getReturns, getEfficientFrontier
import dash_bootstrap_components as dbc

app = Dash(external_stylesheets=[dbc.themes.COSMO])

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

controls = dbc.Card(
    [
    dbc.CardHeader("Parâmetros para as Simulações de Portifólio"),
    dbc.CardBody(
        [
    dbc.Label("Selecione o intervalo do histórico das ações:"),
    html.Div([
        
        dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(1995, 8, 5),
        max_date_allowed=date(2022, 9, 19),
        initial_visible_month=date(2017, 8, 5),
        start_date=date(2018, 1, 1),
        end_date=date(2018, 12, 31),
     ),
    html.Div(id='output-container-date-picker-range'),
    ]),
    dbc.Label("Selecione o numero de portfólios simulados:"),
    dbc.Input(
        id="input_range_2", type="number", placeholder="input with range of portfolios",
        min=100, max=100000, step=100, value=100,
    ),
    ]),
    ], body=True, color="primary", outline=True)

app.layout =dbc.Container(children=[
    html.H1(children='Simulador de rendimento de ativos de portifólio'),

    html.H2(children='''
        A melhor ferramenta inteligente para simulação  de alocação de portifólios.
    '''),
    html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col([dcc.Graph(id='example-graph'), dcc.Graph(id="scatter-graph"),], md=8),
            ],
            align="top",
        ),

], )
@app.callback(
    Output('example-graph', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_graph(start_date, end_date):
    start, end = '2018-01-01', '2018-12-31'
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y-%m-%d')
        start = start_date_string
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y-%m-%d')
        end = end_date_string
    returns = getReturns(start, end)
    fig = px.line(returns)
    return fig

@app.callback(
    Output('scatter-graph', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input("input_range_2", "value"))
def update_scatter(start_date, end_date, n_portfolios):
    start, end = '', ''
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y-%m-%d')
        start = start_date_string
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y-%m-%d')
        end = end_date_string
    retornos = getReturns(start, end)
    ef = getEfficientFrontier(retornos, n_portfolios)
    fig = px.scatter_3d(ef, x='volatilidade', y='retornos', z='indice_de_sharpe', 
        color='volatilidade',  # set color to an array/list of desired values
        color_continuous_scale='Viridis',   # choose a colorscale
        opacity=0.8
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
