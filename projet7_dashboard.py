#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
import pickle
import lightgbm
from sklearn.preprocessing import StandardScaler


# In[2]:


df = pd.read_csv('data_model_dashboard.csv', sep='\t')
print (df.columns)

list_clients=df['SK_ID_CURR']


# In[3]:


threshold=0.1

with open('model', 'rb') as file1:
    pickle_model = pickle.load(file1)
    
with open('standardscaler','rb') as file2:
    ss_mod=pickle.load(file2)


# In[4]:


fi = pd.read_csv('feature_importance.csv', sep='\t')
fi = fi.sort_values(by="importance", ascending=False)
print (fi)
available_indicators = fi["feature"]


# In[6]:


def adjusted_classes(y_scores, t):
    return [1 if y >= t else 0 for y in y_scores]

clients=df
clients=clients.drop(['TARGET', 'SK_ID_CURR', 'index','TARGET_adj'], axis=1)
clients_scaled = ss_mod.transform(clients)
score=pickle_model.predict_proba(clients_scaled)
score=score[:, 1]
df['TARGET_adj']=adjusted_classes(score,threshold)
print (df['TARGET_adj'])

print (df[df['TARGET_adj']==1][['SK_ID_CURR','TARGET_adj']])


# In[7]:


y_value = int(df[df['SK_ID_CURR'] == 115304]['INSTAL_PAYMENT_PERC_MAX'])
y_target = int(df[df['SK_ID_CURR'] == 115304]['TARGET_adj'])
y_min = df['YEARS_BUILD_MODE'].min()
y_max = df['YEARS_BUILD_MODE'].max()
figure_curves = ff.create_distplot([df[df['TARGET_adj'] == 0][
    'YEARS_BUILD_MODE'],
                                  df[df['TARGET_adj'] == 1][
                                      'YEARS_BUILD_MODE']],
                                  ['Score=0', 'Score=1'],
                                  show_hist=False,
                                  show_rug=False)
figure_curves.add_trace(
        go.Scatter(
            x=[float(df[df['SK_ID_CURR'] == 115304][
                'YEARS_BUILD_MODE']),
               float(df[df['SK_ID_CURR'] == 115304]['YEARS_BUILD_MODE'])
               ],
            y=[figure_curves['data'][y_target]['y'].min(),
               figure_curves['data'][y_target]['y'].max()],
            mode="lines",
            line=go.scatter.Line(color="gray"),
            name='Client',
            showlegend=True
        )
    )


# In[8]:


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Create server variable with Flask server object for use with gunicorn
server = app.server


app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in list_clients],
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
                value='YEARS_BUILD_MODE',
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
            )
         ], className="six columns"),
    ], className="row"),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='crossfilter-var1-column',
                options=[{'label': i, 'value': i}
                         for i in available_indicators],
                value='YEARS_BUILD_MODE'
            )
        ], className="six columns"),
        html.Div([
            dcc.Dropdown(
                id='crossfilter-var2-column',
                options=[{'label': i, 'value': i}
                         for i in available_indicators],
                value='YEARS_BUILD_MODE'
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
    score=df.loc[df['SK_ID_CURR'] == value, 'TARGET_adj'].values[0]
    text=""
    if score == 0 :
        text = "Crédit accepté"
    elif score ==1 :
        text = "Crédit refusé"
    
    return ('Score = {}\n{}'.format(score, text))
   
    


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


# In[ ]:


if __name__ == '__main__':
    app.run_server()


# In[ ]:




