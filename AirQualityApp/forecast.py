import numpy
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas
import matplotlib
import matplotlib.pyplot as plotter
from sklearn.model_selection import train_test_split
import requests, math
import datetime, joblib
from .train import date_calculation, train


def predict(zip, ozones, start_date=None):
    try:        
        model = joblib.load('AirQualityApp/forecasting/model.joblib')
        print("Forecast model already set")
    except Exception as e:
        train()
        model = joblib.load('AirQualityApp/forecasting/model.joblib')
        print("New forecast model created and trained")

    if not start_date:
        start_date = datetime.date.today() + datetime.timedelta(days=1)
    
    forecast = []

    try:
        for day in range(len(ozones)):
            date = start_date + datetime.timedelta(days=day)
            value = date_calculation(date.isoformat())
            new_data = [[ozones[day]["ozone"], value, zip]]

            pm = model.predict(new_data)
            forecast.append({"stamp" : date, "pm": pm[0]})
        
        return forecast
            
    except Exception as e:
        print(str(e))

def retrain(pm, ozone, date, zip):
    x = [[ozone, date_calculation(date), zip]]
    y = [[pm]]

    print(x)
    print(y)
    model = joblib.load('model.joblib')
    model.fit(x,y)
    joblib.dump(model, 'model.joblib')










