import numpy
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas
import matplotlib
import matplotlib.pyplot as plotter
from sklearn.model_selection import train_test_split
import requests, math
from sklearn.externals import joblib
import datetime
from .train import date_calculation, train


def predict(zip, ozones):
    try:        
        model = joblib.load('model.joblib')
    except Exception as e:
        train()
        model = joblib.load('model.joblib')

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    forecast = []

    try:
        for day in range(len(ozones)):
            date = tomorrow + datetime.timedelta(days=day)
            value = date_calculation(date.isoformat())
            new_data = [[ozones[day]["ozone"], value, zip]]

            pm = model.predict(new_data)
            forecast.append({"stamp" : date.isoformat(), "pm": pm[0]})
        
        return forecast
            
    except Exception as e:
        print(str(e))

def retrain(pm, ozone, date, zip):
    x = [[ozone, date_calculation(date), zip]]
    y = [[pm]]

    model = joblib.load('model.joblib')
    model.fit(x,y)
    joblib.dump(model, 'model.joblib')










