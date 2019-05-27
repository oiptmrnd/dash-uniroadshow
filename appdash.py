# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests
import base64
import json
import datetime
import time
import pandas as pd
import plotly.graph_objs as go
requests.packages.urllib3.disable_warnings()

__author__ = "Chun-Yeow Yeoh"
__copyright__ = "Copyright 2019, Telekom R&D Sdn. Bhd."
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Chun-Yeow Yeoh"
__email__ = "yeow@tmrnd.com.my"

import conf

def auth(username, password):
    try:
       headers = {'charset':'utf-8','Content-Type':'application/json', 'Accept':'application/json', 'Authorization':'Bearer ' + conf.gw_token }
       url = conf.url + "/api/auth/login"
       data = "{\"username\":\"" + username + "\",\"password\":\"" + password + "\"}"
       post_resp = requests.post(url, data, headers=headers, verify=True)
       if post_resp.status_code == 200:
          return post_resp
       else:
          return
    except requests.exceptions.ConnectionError:
       return

def get_timeseries_data(device_id, key, startTs, endTs, interval, agg, limit, token):
    try:
       headers = {'charset':'utf-8','Content-Type':'application/json', 'Accept':'application/json', 'X-Authorization': 'Bearer ' + token, 'Authorization':'Bearer ' + conf.gw_token }
       url = conf.url + "/api/plugins/telemetry/DEVICE/" + device_id + \
             "/values/timeseries?keys=" + key + "&startTs=" + startTs + "&endTs=" + endTs + "&interval=" + interval + "&limit=" + limit + "&agg=" + agg
       get_resp = requests.get(url, headers=headers, verify=False)
       if get_resp.status_code == 200:
          return get_resp
       else:
          return
    except requests.exceptions.ConnectionError:
       return

def get_currentmillis(year, month, day, start):
    if (start == True):
       v = datetime.datetime(int(year), int(month), int(day), 0, 0, 0, 360700)
    else:
       v = datetime.datetime(int(year), int(month), int(day), 23, 59, 59, 360700)
    d = time.mktime(v.timetuple()) * 1000
    return "{0:13.0f}".format(d)

def serve_layout():
    res = auth(conf.username, conf.password)
    if res != None:
       token = res.json()['token']
       print token
    date = conf.date
    year,month,day = date.split('-')
    start = str(get_currentmillis(year, month, day, True))
    stop = str(get_currentmillis(year, month, day, False))
    interval = str(86400000)
    agg = "NONE"
    limit = str(60000)

    value = []
    ts = []
    res = get_timeseries_data(conf.device_id, conf.key, start, stop, interval, agg, limit, token)
    data = res.json()
    if res != None and data.has_key(conf.key):
       params = data[conf.key]
       for j in range(len(params)):
          value.append(float(params[j]['value']))
          tsproc = datetime.datetime.fromtimestamp(int(params[j]['ts'])/1000).strftime('%Y-%m-%d %H:%M:%S')
          ts.append(tsproc)
    print ts
    print value
    trace = go.Scatter(x = ts, y = value,
                       name = 'Data Points',
                       line = dict(width = 2, color = 'rgb(229, 151, 50)'))
    layout = go.Layout(title = 'Time Series Plot for Sending Value', hovermode = 'closest')
    fig = go.Figure(data = [trace], layout = layout)

    return html.Div(
                    [html.Div([
                               html.Div([html.H3('Example Demo for University Roadshow'), dcc.Graph(id='plot', figure=fig)]),
                              ], className="row")
                    ]
                   )


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = serve_layout

if __name__ == '__main__':
   app.run_server(debug=True)
