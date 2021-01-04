import numpy, requests, math, pandas
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib

def dates_calculation(dates):
    length = len(dates)
    result_array = []

    for index in range(length):
        date = dates[index].split('-')
        result = (365 + float(date[1])*30 + float(date[2])) / float(date[0])
        result_array.append(result)
    
    return result_array

def date_calculation(date):
    split_date = date.split('-')
    return (365 + float(split_date[1])*30 + float(split_date[2])) / float(split_date[0])

def train():
      pollution = pandas.read_csv('AirQualityApp/forecasting/pollution.csv')

      Y = pollution['pm']
      X = pollution[['ozone', 'stamp', 'zipcode']]

      print(X)

      dates = dates_calculation(X['stamp'])

      X['stamp'] = dates

      train_x, test_x, train_y, test_y = train_test_split(X, Y, test_size=.2, random_state=1234)

      model = RandomForestRegressor(n_estimators=300, random_state=1234)
      
      model.fit(train_x, train_y)

      prediction = model.predict(test_x)

      # The mean squared error
      print("Root mean squared error: %.2f"
            % math.sqrt(mean_squared_error(test_y, prediction)))
      # The absolute squared error
      print("Mean absolute error: %.2f"
            % mean_absolute_error(test_y, prediction))
      # Explained variance score: 1 is perfect prediction
      print('R-squared: %.2f' % r2_score(test_y, prediction))

      joblib.dump(model, 'AirQualityApp/forecasting/model.joblib')
