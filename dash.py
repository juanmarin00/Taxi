from pred_funcs import get_coords
from prediction_pipeline import new_prediction_pipeline
import dash  # (version 1.11.0)
import pandas as pd
import plotly.express as px     # (version 4.6.0)
from dash.dependencies import Input, Output
import numpy as np
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.offline as py     #(version 4.4.1)
import plotly.graph_objs as go
import math
import os
from dotenv import load_dotenv


load_dotenv()
mapbox_access_token =os.getenv("mapbox")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def hovertext_string(name, stype, time):
    ret_str = stype + " : " + name + ", " + stype + " time:" + time
    return ret_str
hovertext_string("moma", "dropoff", "1pm")

def update_time(start, journey_time):
    curr_minutes = int(start[-2:])
    curr_hour = int(start[:2])
    minutes_travelled = journey_time//60
    final_minutes = curr_minutes + minutes_travelled
    if final_minutes>59:
        final_minutes = final_minutes%60
        curr_hour +=1
    final_time = str(curr_hour) + ":" + str(final_minutes)
    return final_time

input_types = ['pickup', 'dropoff', "Passengers", "date", "time"]

app.layout = html.Div([
    html.Div([
        dcc.Input(
            id='my_{}'.format(x),
            type=x,
            placeholder="insert {}".format(x),  # A hint to the user of what can be entered in the control
            debounce=True,                      # Changes to input are sent to Dash server only on enter or losing focus
            min=-75, max=41,         # Ranges of numeric value. Step refers to increments
            minLength=0, maxLength=50,          # Ranges for character length inside input box
            autoComplete='on',
            disabled=False,                     # Disable input box
            readOnly=False,                     # Make input box read only
            required=False,                     # Require user to insert something into input box
            size="20",                          # Number of characters that will be visible inside box
            # style={'':''}                     # Define styles for dropdown (Dropdown video: 13:05)
            # className='',                     # Define style from separate CSS document (Dropdown video: 13:05)
            # persistence='',                   # Stores user's dropdown changes in memory (Dropdown video: 16:20)
            # persistence_type='',              # Stores user's dropdown changes in memory (Dropdown video: 16:20)
        ) for x in input_types
    ]),

    html.Br(),

    html.Div(id='result'),
    
    html.Br(),

    dcc.Graph(id="mymap"),

])





@app.callback(
    Output(component_id='result', component_property='children'),
    [Input(component_id='my_{}'.format(x), component_property='value')
     for x in input_types
     ],
)

def update_result(pickup, dropoff, Passengers, date, time):
    date_string = date+ " " + time
    result = new_prediction_pipeline(date_string, Passengers, pickup, dropoff)
    price = result[0]
    new_mins = result[1]
    mins = new_mins//60
    seconds = math.floor(new_mins%60)
    drop_time = update_time(time, result[1])
    
    
    
    #eta = update_result(time, result[1])
    
    result_str = "The cab will cost " , price, " dollars. will take ", mins, " minutes and ", seconds, " seconds. Estimated time of arrival is: ", drop_time
    return result_str
    
    
    
    
@app.callback(
    Output(component_id='mymap', component_property='figure'),
    [Input(component_id='my_{}'.format(x), component_property='value')
     for x in input_types
     ],
)

def update_graph(pickup, dropoff, Passengers, date, time):
    
    
    date_string = date+ " " + time
    result = new_prediction_pipeline(date_string, Passengers, pickup, dropoff)[1]
    drop_time = update_time(time, result)
    
    
    p_lat = get_coords(pickup)[0]
    d_lat = get_coords(dropoff)[0]    
    p_lon = get_coords(pickup)[1]
    d_lon = get_coords(dropoff)[1]
    
    
    
    d = {'latitude': [p_lat, d_lat], 'longitude': [p_lon, d_lon], "type": ["pickup","dropoff"], "color": ["#ff00ff","#008000"], "hov_str" : [hovertext_string(pickup, "pickup", str(time)), hovertext_string(dropoff, "dropoff", str(drop_time))]}
    df_sub = pd.DataFrame(data=d)
    
    
    locations=[go.Scattermapbox(
                    lon = df_sub['longitude'],
                    lat = df_sub['latitude'],
                    mode = "markers+text",
                    marker={'color' : df_sub['color'], 'size': 20},
                    unselected={'marker' : {'opacity':1}},
                    selected={'marker' : {'opacity':0.5, 'size':25}},
                    hoverinfo='text',
                    hovertext= df_sub['hov_str'],
                    #customdata=df_sub['website']
    )]
    
    
    # Return figure
    return {
        'data': locations,
        'layout': go.Layout(
            uirevision= 'foo', #preserves state of figure/map after callback activated
            clickmode= 'event+select',
            hovermode='closest',
            width=2000,
            height=800,
            hoverdistance=2,
            title=dict(text="Taxi query",font=dict(size=70, color='green')),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=25,
                style='light',
                center=dict(
                    lat=40.60105,
                    lon=-73.945155
                    
                ),
                pitch=0,
                zoom=11.5
            ),
        )
    }
    

if __name__ == '__main__':
    app.run_server(debug=False, host = '127.0.0.1')