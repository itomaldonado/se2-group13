import numpy as np
import os
import tulipy as ti

from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler


class LSTM:
    """ Represents our SVM prediction algorithm/models"""

    def __init__(self, models_dir=None):
        """ Create an instance of SVM
        Args:
            models_dir (String): directory where the SVM models (per symbol) exists,
                defaults to ./models/svm
        """
        self.models_ext = 'h5'
        if not models_dir:
            self.models = f'{os.path.dirname(os.path.realpath(__file__))}/models/lstm'
        else:
            self.models = os.path.abspath(models_dir)

        # model configuration
        self.data_needed = 130
        self.trained_data_input = 120
        self.trained_forecast_out = 30

    def predict(self, symbol, data, forecast_out):
        """ Predict stock "close" value `forecast_out` days in the future
        Args:
            symbol (String): symbol name used to load the model
            data (pandas Dataframe): contains input data for prediction, should be of size
                (self.data_needed) rows of data, with format:
                'day_open', 'day_high', 'day_low', 'day_close', 'day_volume'
            forecast_out (Integer): used to verify if the data provided is enough to forecast
        """
        model_file = f'{self.models}/{symbol.upper()}.{self.models_ext}'

        if not os.path.isfile(model_file):
            raise Exception(f'Model for {symbol} does not exist')

        if len(data) < self.data_needed:
            raise Exception(f'Data provided is not enough for prediction of {forecast_out} days')

        # calculate the performance indicators needed for this data, drop any NAs
        for i in range(1, int(self.trained_forecast_out/5) + 1):
            data = self.performance_indicators(data, i)
        data.dropna(inplace=True)

        # trim the frame to the exact number needed
        data = data[-self.trained_data_input:]

        # scale the data
        scl = MinMaxScaler()
        array = data.values.reshape(data.shape)
        array = scl.fit_transform(array)

        # load the model
        model = load_model(model_file)

        # predict with the test data
        data = np.array([array, ])
        predicted_values = model.predict(data)
        predicted_values = np.round(scl.inverse_transform(predicted_values)[0], 2)
        predicted_values = predicted_values.tolist()

        # slice the array for the data we need and return that
        return predicted_values[:forecast_out]

    def performance_indicators(self, df, period):
        # generate the performance indicators
        data = df.astype('float64')
        rsi = ti.rsi(data['day_close'].values, period)
        rsi = np.insert(rsi, 0, [np.nan for i in range(period)])

        wma = ti.wma(data['day_close'].values, period=period)
        wma = np.insert(wma, 0, [np.nan for i in range(period-1)])

        vwma = ti.vwma(
            close=data['day_close'].values,
            volume=data['day_volume'].values,
            period=period)
        vwma = np.insert(vwma, 0, [np.nan for i in range(period-1)])

        willr = ti.willr(
            high=data['day_high'].values,
            low=data['day_low'].values,
            close=data['day_close'].values,
            period=period)
        willr = np.insert(willr, 0, [np.nan for i in range(period-1)])

        stddev = ti.stddev(data['day_close'].values, period=period)
        stddev = np.insert(stddev, 0, [np.nan for i in range(period-1)])

        # set the performance indicator data
        df[f'{period}days_rsi'] = rsi
        df[f'{period}days_wma'] = wma
        df[f'{period}days_vwma'] = vwma
        df[f'{period}days_willr'] = willr
        df[f'{period}days_stddev'] = stddev
        return df
