# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from financial import getReturns, getEfficientFrontier
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

server = app.server

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
app.title = 'Simulador de Ativos'
controls = dbc.Card(
    [
    dbc.CardHeader("Parâmetros para as Simulações de Portifólio"),
    dbc.CardBody(
        [
    dbc.Label("Selecione as ações:"),
    dcc.Dropdown(
        ['META', 'TSLA', 'TWTR', 'MSFT', 'AAPL', 'LMT'],
        ['META', 'TSLA'],
        multi=True,
        id="tickers"
    ),
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

app.layout = dbc.Container(children=[
    html.H1(children='Simulador de rendimento de ativos de portifólio'),

    html.H2(children='''
        A melhor ferramenta inteligente para simulação  de alocação de portifólios.
    '''),
    html.Hr(),
        dbc.Row(
            [
                dbc.Col([controls,
                        html.H3("Carteira com as menores porcentagens"),
                        dbc.Table(id="mytable"),
                        dbc.Table(id="mytable-assets"),
                        html.H3("Carteira com as maiores porcentagens"),
                        dbc.Table(id="mytable-max"),
                        dbc.Table(id="mytable-assets-max")], md=4),
                dbc.Col([dcc.Graph(id='example-graph'), dcc.Graph(id="scatter-graph")], md=8),
            ],
            align="top",
        ),
    html.Div(id='portfolio')

], )
@app.callback(
    Output('example-graph', 'figure'),
    Input('tickers', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_graph(tickers, start_date, end_date):
    start, end = '2018-01-01', '2018-12-31'
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y-%m-%d')
        start = start_date_string
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y-%m-%d')
        end = end_date_string
    returns = getReturns(tickers, start, end)
    fig = px.line(returns)
    return fig

@app.callback(
    Output('scatter-graph', 'figure'),
    Input('tickers', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input("input_range_2", "value"))
def update_scatter(tickers, start_date, end_date, n_portfolios):
    start, end = '', ''
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y-%m-%d')
        start = start_date_string
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y-%m-%d')
        end = end_date_string
    retornos = getReturns(tickers, start, end)
    ef, std, mean, max, min, weights = getEfficientFrontier(tickers, retornos, n_portfolios)


    fig = px.scatter_matrix(ef,
        color='volatilidade',
        color_continuous_scale='Viridis',
        opacity=0.8
    )

    return fig

@app.callback(
    Output('mytable', 'children'),
    Input('tickers', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input("input_range_2", "value"))
def update_table(tickers, start_date, end_date, n_portfolios):
    start, end = '', ''
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y-%m-%d')
        start = start_date_string
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y-%m-%d')
        end = end_date_string
    retornos = getReturns(tickers, start, end)
    ef, std, mean, max, min, weights = getEfficientFrontier(tickers, retornos, n_portfolios)
    retornos = f"{100 * min['retornos']:.2f}%"
    volatilidade = f"{100 * min['volatilidade']:.2f}%"
    indice_de_sharpe = f"{100 * min['indice_de_sharpe']:.2f}%"

    table_header = [
    html.Thead(html.Tr([html.Th("Retornos"), html.Th("Volatilidade"), html.Th("Indice de Sharpe")]))
    ]
    return table_header + [html.Tbody([html.Tr([html.Td([retornos]), html.Td([volatilidade]), html.Td([indice_de_sharpe])])])]

@app.callback(
    Output('mytable-assets', 'children'),
    Input('tickers', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input("input_range_2", "value"))
def update_table_assets(tickers, start_date, end_date, n_portfolios):
    start, end = '', ''
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y-%m-%d')
        start = start_date_string
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y-%m-%d')
        end = end_date_string
    retornos = getReturns(tickers, start, end)
    df, std, mean, max, min, weights = getEfficientFrontier(tickers, retornos, n_portfolios)

    header_content = []
    td_content = []
    for x, y in zip(tickers, weights[np.argmin(df.volatilidade)]):
        header_content.append(html.Th(x))
        td_content.append(html.Td([f'{100*y:.2f}%']))

    table_header = [
    html.Thead(html.Tr(header_content))
    ]
    return table_header + [html.Tbody([html.Tr(td_content)])]

@app.callback(
    Output('mytable-assets-max', 'children'),
    Input('tickers', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input("input_range_2", "value"))
def update_table_assets_max(tickers, start_date, end_date, n_portfolios):
    start, end = '', ''
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y-%m-%d')
        start = start_date_string
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y-%m-%d')
        end = end_date_string
    retornos = getReturns(tickers, start, end)
    df, std, mean, max, min, weights = getEfficientFrontier(tickers, retornos, n_portfolios)

    header_content = []
    td_content = []
    for x, y in zip(tickers, weights[np.argmax(df.volatilidade)]):
        header_content.append(html.Th(x))
        td_content.append(html.Td([f'{100*y:.2f}%']))
        # print(f'{100*y:.2f}%', end="", flush=True)
    # , volatilidade, indice_de_sharpe
    table_header = [
    html.Thead(html.Tr(header_content))
    ]
    return table_header + [html.Tbody([html.Tr(td_content)])]


@app.callback(
    Output('mytable-max', 'children'),
    Input('tickers', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input("input_range_2", "value"))
def update_table_max(tickers, start_date, end_date, n_portfolios):
    start, end = '', ''
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y-%m-%d')
        start = start_date_string
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y-%m-%d')
        end = end_date_string
    retornos = getReturns(tickers, start, end)
    ef, std, mean, max, min, weights = getEfficientFrontier(tickers, retornos, n_portfolios)
    retorno = f"{100 * max['retornos']:.2f}%"
    volatilidade = f"{100 * max['volatilidade']:.2f}%"
    indice_de_sharpe = f"{100 * max['indice_de_sharpe']:.2f}%"

    table_header = [
    html.Thead(html.Tr([html.Th("Retornos"), html.Th("Volatilidade"), html.Th("Indice de Sharpe")]))
    ]
    return table_header + [html.Tbody([html.Tr([html.Td([retorno]), html.Td([volatilidade]), html.Td([indice_de_sharpe])])])]

if __name__ == '__main__':
    app.run_server(debug=True)
