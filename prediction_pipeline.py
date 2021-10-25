import numpy as np
import pandas as pd
import pickle
import warnings
warnings.filterwarnings('ignore')
import pred_funcs as pred
import json
import requests


def new_prediction_pipeline(timestamp, n_passengers, pickup, dropoff):
    pickup_coords =  pred.get_coords(pickup)
    dropoff_coords = pred.get_coords(dropoff)
    
    pickup_latitude = pickup_coords[0]
    dropoff_longitude = dropoff_coords[1]
    dropoff_latitude = dropoff_coords[0]
    pickup_longitude = pickup_coords[1]
    
    fare = pred.get_price_pipeline(timestamp, n_passengers, pickup_latitude, dropoff_longitude, dropoff_latitude, pickup_longitude)
    time = pred.get_time_pipeline(timestamp, n_passengers, pickup_latitude, dropoff_longitude, dropoff_latitude, pickup_longitude)
    
    #print("A cab here will cost you" , fare, "dollars, and will take", time, "to get to your destination")
    return(fare, time)