import os
import pickle

from sklearn import preprocessing


class SVM:
    """ Represents our SVM prediction algorithm/models"""

    def __init__(self, models_dir=None):
        """ Create an instance of SVM
        Args:
            models_dir (String): directory where the SVM models (per symbol) exists,
                defaults to ./models/svm
        """
        if not models_dir:
            self.models = f'{os.path.dirname(os.path.realpath(__file__))}/models/svm'
        else:
            self.models = os.path.abspath(models_dir)

    def predict(self, symbol, data, forecast_out):
        """ Predict stock "close" value `forecast_out` days in the future
        Args:
            symbol (String): symbol name used to load the model
            data (pandas Dataframe): contains input data for prediction, should be of size
                (forecast_out / 0.01) rows of data, with format:
                'day_close','High_Low_per','Per_change'
            forecast_out (Integer): used to verify if the data provided is enough to forecast
        """
        model = f'{self.models}/{symbol.upper()}'

        if not os.path.isfile(model):
            raise Exception(f'Model for {symbol} does not exist')

        forecast_out = int(forecast_out)
        if len(data) < forecast_out:
            raise Exception(f'Data provided is not enough for prediction of {forecast_out} days')

        # trim the frame to the exact number needed
        data = data[-forecast_out:]

        with open(model, 'rb') as mf:
            clf = pickle.load(mf)
            data = preprocessing.scale(data)
            return preprocessing.scale(clf.predict(data))
