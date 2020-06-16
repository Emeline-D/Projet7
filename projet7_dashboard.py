# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
import json
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import numpy as np

df = pd.read_csv('data_model_dashboard.csv', sep='\t')
print (df.columns)

clients = df["SK_ID_CURR"]
threshold = 0.14

fi = pd.read_csv('feature_importance.csv', sep='\t')
fi = fi.sort_values(by="importance", ascending=False)
print (fi)
available_indicators = fi["feature"]

y_value = int(df[df['SK_ID_CURR'] == 115304]['INSTAL_PAYMENT_PERC_MAX'])
y_target = int(df[df['SK_ID_CURR'] == 115304]['TARGET_adj'])
y_min = df['INSTAL_PAYMENT_PERC_MAX'].min()
y_max = df['INSTAL_PAYMENT_PERC_MAX'].max()
figure_curves = ff.create_distplot([df[df['TARGET_adj'] == 0][
    'INSTAL_PAYMENT_PERC_MAX'],
                                  df[df['TARGET_adj'] == 1][
                                      'INSTAL_PAYMENT_PERC_MAX']],
                                  ['Score=0', 'Score=1'],
                                  show_hist=False,
                                  show_rug=False)
figure_curves.add_trace(
        go.Scatter(
            x=[float(df[df['SK_ID_CURR'] == 115304][
                'INSTAL_PAYMENT_PERC_MAX']),
               float(df[df['SK_ID_CURR'] == 115304]['INSTAL_PAYMENT_PERC_MAX'])
               ],
            y=[figure_curves['data'][y_target]['y'].min(),
               figure_curves['data'][y_target]['y'].max()],
            mode="lines",
            line=go.scatter.Line(color="gray"),
            name='Client',
            showlegend=True
        )
    )

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Create server variable with Flask server object for use with gunicorn
server = app.server


app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in clients],
                value=115304,
                style={
                    'borderBottom': 'thin lightgrey solid',
                    'backgroundColor': 'rgb(250, 250, 250)',
                    'padding': '10px 5px',
                    'text-align': 'center',
                }
            ),
        ], className="six columns"),
        html.Div([
            dcc.Dropdown(
                id='crossfilter-var-column',
                options=[{'label': i, 'value': i}
                         for i in available_indicators],
                value='INSTAL_PAYMENT_PERC_MAX',
                style={
                       'borderBottom': 'thin lightgrey solid',
                       'backgroundColor': 'rgb(250, 250, 250)',
                       'padding': '10px 5px',
                       'text-align': 'center',
                }
            )
         ], className="six columns"),
    ], className="row"),
    html.Div([
        dcc.Textarea(
            id='textarea-example',
            value='Score = ',
            style={
                'width': '100%',
                'height': '100%',
                'resize': 'none',
                'border': '2px solid black',
                'text-align': 'center',
                'font-size': '40px'}
        ),
    ]),
    html.Div([
        html.Div([
            dcc.Graph(
                id='feature_importance',
                figure={
                    'data': [
                        {
                         'x': fi['importance'],
                         'y': fi['feature'],
                         'type': 'bar',
                         'orientation':'h'
                        }
                    ],
                    'layout': go.Layout(
                        xaxis={'title': 'Importance'},
                        yaxis={'title': 'Feature'},
                        hovermode='closest',
                        width=100,
                    )
                }
            )
        ], className="six columns"),
        html.Div([
            dcc.Graph(
                id='graph_three_curves',
                figure=figure_curves
            )
         ], className="six columns"),
    ], className="row"),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='crossfilter-var1-column',
                options=[{'label': i, 'value': i}
                         for i in available_indicators],
                value='INSTAL_PAYMENT_PERC_MAX'
            )
        ], className="six columns"),
        html.Div([
            dcc.Dropdown(
                id='crossfilter-var2-column',
                options=[{'label': i, 'value': i}
                         for i in available_indicators],
                value='INSTAL_PAYMENT_PERC_MAX'
            )
        ], className="six columns")
    ], className="row"),
    dcc.Graph(
        id='graph_two_variables',
        figure={
            'data': [
                {
                    'x': df[df['TARGET_adj'] == 0]['TARGET'],
                    'y': df[df['TARGET_adj'] == 0]['INSTAL_PAYMENT_PERC_MAX'],
                    'name': 'Score = 0',
                    'mode': 'markers',
                    'marker': {'size': 12, 'color': 'blue', 'opacity': 0.5}
                },
                {
                    'x': df[df['TARGET_adj'] == 1]['TARGET'],
                    'y': df[df['TARGET_adj'] == 1]['INSTAL_PAYMENT_PERC_MAX'],
                    'name': 'Score = 1',
                    'mode': 'markers',
                    'marker': {'size': 12, 'color': 'orange', 'opacity': 0.5}
                },
                {
                    'x': df[df['SK_ID_CURR'] == 115304]['TARGET'],
                    'y': df[df['SK_ID_CURR'] == 115304][
                        'INSTAL_PAYMENT_PERC_MAX'],
                    'name': 'ID Client',
                    'mode': 'markers',
                    'marker': {'size': 12, 'color': 'Chartreuse', 'opacity': 1}
                }
            ],
            'layout': go.Layout(
                xaxis={'title': 'TARGET'},
                yaxis={'title': 'INSTAL_PAYMENT_PERC_MAX'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                hovermode='closest'
            )
        }
    )
])


@app.callback(dash.dependencies.Output('textarea-example', 'value'),
              [dash.dependencies.Input('crossfilter-xaxis-column', 'value')])
def update_output(value):
    score = (df.loc[df["SK_ID_CURR"] == int(value), 'TARGET_adj']).values
    text = ""
    if score == 0:
        text = "Crédit accepté"
    elif score == 1:
        text = "Crédit refusé"
    return ('Score = {}\n{}'.format(score[0], text))


@app.callback(
    dash.dependencies.Output('graph_two_variables', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-var1-column', 'value'),
     dash.dependencies.Input('crossfilter-var2-column', 'value')])
def update_timeseries(xaxis_column_name, var1_column_name, var2_column_name):
    return {
            'data': [
                {
                    'x': df[df['TARGET_adj'] == 0][var1_column_name],
                    'y': df[df['TARGET_adj'] == 0][var2_column_name],
                    'name': 'Score = 0',
                    'mode': 'markers',
                    'marker': {'size': 12, 'color': 'blue', 'opacity': 0.5}
                },
                {
                    'x': df[df['TARGET_adj'] == 1][var1_column_name],
                    'y': df[df['TARGET_adj'] == 1][var2_column_name],
                    'name': 'Score = 1',
                    'mode': 'markers',
                    'marker': {'size': 12, 'color': 'orange', 'opacity': 0.5}
                },
                {
                    'x': df[df['SK_ID_CURR'] == xaxis_column_name][
                        var1_column_name],
                    'y': df[df['SK_ID_CURR'] == xaxis_column_name][
                        var2_column_name],
                    'name': 'ID Client',
                    'mode': 'markers',
                    'marker': {'size': 12, 'color': 'Chartreuse', 'opacity': 1}
                }
            ],
            'layout': go.Layout(
                xaxis={'title': var1_column_name},
                yaxis={'title': var2_column_name},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                hovermode='closest'
            )
        }


@app.callback(
    dash.dependencies.Output('graph_three_curves', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-var-column', 'value'),
     dash.dependencies.Input('feature_importance', 'clickData')])
def update_timeseries(xaxis_column_name, var_column_name, clickData):
    y_value = int(df[df['SK_ID_CURR'] == xaxis_column_name][var_column_name])
    y_target = int(df[df['SK_ID_CURR'] == xaxis_column_name]['TARGET_adj'])
    y_min = df['INSTAL_PAYMENT_PERC_MAX'].min()
    y_max = df['INSTAL_PAYMENT_PERC_MAX'].max()

    figure_curves = ff.create_distplot([df[df['TARGET_adj'] == 0][
        var_column_name],
                                      df[df['TARGET_adj'] == 1][
                                          var_column_name]],
                                      ['Score=0', 'Score=1'],
                                      show_hist=False,
                                      show_rug=False)
    figure_curves.add_trace(
        go.Scatter(
            x=[float(df[df['SK_ID_CURR'] == xaxis_column_name][
                var_column_name]),
               float(df[df['SK_ID_CURR'] == xaxis_column_name][
                   var_column_name])],
            y=[figure_curves['data'][y_target]['y'].min(),
               figure_curves['data'][y_target]['y'].max()],
            mode="lines",
            line=go.scatter.Line(color="gray"),
            name='Client',
            showlegend=True
        )
    )
    return figure_curves


def update_trace(xaxis_column_name, clickData):
    y_target = int(df[df['SK_ID_CURR'] == xaxis_column_name]['TARGET_adj'])
    return fig.update_traces(
        x=[float(df[df['SK_ID_CURR'] == xaxis_column_name][
            clickData['points'][0]['label']]),
           float(df[df['SK_ID_CURR'] == xaxis_column_name][
               clickData['points'][0]['label']])],
        y=[figure_curves['data'][y_target]['y'].min(),
           figure_curves['data'][y_target]['y'].max()],
        selector=dict(mode="lines"), overwrite=True)

if __name__ == '__main__':
    app.run_server()
