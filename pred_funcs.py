import numpy as np
import pandas as pd
import pickle
import json
import requests
import os
from dotenv import load_dotenv



import warnings
warnings.filterwarnings('ignore')

price_model = pickle.load(open("notebooks/prize_model.sav", 'rb'))
time_model = pickle.load(open("notebooks/length_model.sav", 'rb'))

#Price model
#All functions used for price pred
def prepare_time_features(df):
    df['pickup_datetime'] = df['pickup_datetime'].str.slice(0, 16)
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], utc=True, format='%Y-%m-%d %H:%M')
    df['hour_of_day'] = df.pickup_datetime.dt.hour
    df['month'] = df.pickup_datetime.dt.month
    df["year"] = df.pickup_datetime.dt.year
    df["weekday"] = df.pickup_datetime.dt.weekday
    return df

def transform(data):
    # Distances to nearby airports, 
    jfk = (-73.7781, 40.6413)
    ewr = (-74.1745, 40.6895)
    lgr = (-73.8740, 40.7769)

    data['distance_to_jfk'] = distance(jfk[1], jfk[0],
                                         data['pickup_latitude'], data['pickup_longitude'])
    data['distance_to_ewr'] = distance(ewr[1], ewr[0], 
                                          data['pickup_latitude'], data['pickup_longitude'])
    data['distance_to_lgr'] = distance(lgr[1], lgr[0],
                                          data['pickup_latitude'], data['pickup_longitude'])
    
    return data

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295 # Pi/180
    a = 0.5 - np.cos((lat2 - lat1) * p)/2 + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    return 0.6213712 * 12742 * np.arcsin(np.sqrt(a))


def get_price_pipeline(timestamp, n_passengers, pickup_latitude, dropoff_longitude, dropoff_latitude, pickup_longitude):
    d = {'pickup_datetime': [timestamp], 'passenger_count': [n_passengers],  'pickup_latitude' : [pickup_latitude], 'dropoff_longitude' : [dropoff_longitude], 'dropoff_latitude' : [dropoff_latitude],'pickup_longitude' : [pickup_longitude]}
    manual_df = pd.DataFrame(data=d)
    col_order = ['pickup_longitude', 'pickup_latitude', 'dropoff_longitude',
       'dropoff_latitude', 'passenger_count', 'hour_of_day', 'month', 'year',
       'weekday', 'distance_miles', 'distance_to_jfk', 'distance_to_ewr',
       'distance_to_lgr']
    
    prepare_time_features(manual_df)
    transform(manual_df)
    manual_df['distance_miles'] = distance(manual_df.pickup_latitude, manual_df.pickup_longitude, \
                                      manual_df.dropoff_latitude, manual_df.dropoff_longitude)
    manual_df.drop(columns= ['pickup_datetime'], axis= 1, inplace=True)

    manual_df = manual_df[col_order]
    
    manual_predictions = price_model.predict(manual_df)
    
    return manual_predictions[0]
    



#Time pipeline
def get_time_pipeline(timestamp, n_passengers, pickup_latitude, dropoff_longitude, dropoff_latitude, pickup_longitude):
    d = {'pickup_datetime': [timestamp], 'passenger_count': [n_passengers],  'pickup_latitude' : [pickup_latitude], 'dropoff_longitude' : [dropoff_longitude], 'dropoff_latitude' : [dropoff_latitude],'pickup_longitude' : [pickup_longitude]}
    manual_df = pd.DataFrame(data=d)
    manual_df['pickup_datetime'] = pd.to_datetime(manual_df.pickup_datetime)
    manual_df['month'] = manual_df.pickup_datetime.dt.month
    manual_df['week'] = manual_df.pickup_datetime.dt.week
    manual_df['weekday'] = manual_df.pickup_datetime.dt.weekday
    manual_df['hour'] = manual_df.pickup_datetime.dt.hour
    manual_df['minute'] = manual_df.pickup_datetime.dt.minute
    manual_df['minute_oftheday'] = manual_df['hour'] * 60 + manual_df['minute']
    manual_df.drop(['minute'], axis=1, inplace=True)
    
    col_order = ['passenger_count', 'pickup_longitude', 'pickup_latitude',
       'dropoff_longitude', 'dropoff_latitude', 'month', 'week', 'weekday',
       'hour', 'minute_oftheday']
    
    predictions = np.exp(time_model.predict(manual_df[col_order]))
    
    return predictions[0]


def get_coords(place):
    load_dotenv()
    key = os.getenv("google")
    #address = "Madison Square Garden"
    params = {
    "key": key,
    "address": place
    }

    url = "https://maps.googleapis.com/maps/api/geocode/json?"

    response = requests.get(url, params = params).json()
    if response["status"] == "OK":
        lat = response["results"][0]["geometry"]["location"]["lat"]
        long = response["results"][0]["geometry"]["location"]["lng"]
        return (lat,long)
