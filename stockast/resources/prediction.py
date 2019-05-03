import falcon
import logging
import pandas as pd

from falcon_autocrud.db_session import session_scope
from pandas.tseries.offsets import BDay

from stockast.authentication import StockastAuthentication
from stockast.learning import bayesian
from stockast.learning.lstm import LSTM
from stockast.learning.svm import SVM
from stockast.models import Company, StockHistory, StockRealTime
from stockast.utils import check_and_get_company, check_params, compare_price

logger = logging.getLogger(__name__)


class StockPredictionShort:
    """ Resource to run short-term predictions"""

    # only steps we allow in short-term prediction:
    #   T/MIN --> minute
    #   H --> hourly
    #   D -> daily
    # as per: http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    ALLOWED_STEPS = ['T', 'MIN', 'H', 'D']
    DEFAULT_STEP = 'T'
    DEFAULT_DAYS = 5

    # Bayesian defaults
    DEFAULT_ALPHA = 0.005
    DEFAULT_BETA = 11.100
    DEFAULT_MTH = 2

    def __init__(self, engine):
        self.db_engine = engine

    @falcon.before(StockastAuthentication())
    def on_get(self, req, resp, symbol):

        # get parameters
        days = int(req.params.get('days', self.DEFAULT_DAYS))
        step = req.params.get('step', self.DEFAULT_STEP).upper()
        symbol = symbol.upper()
        cost = req.params.get('cost')
        cost = float(cost) if cost else None

        # check params are proper and allowed
        if not check_params(step, self.ALLOWED_STEPS):
            raise falcon.HTTPInvalidParam(
                msg=f'Valid values are: {", ".join(self.ALLOWED_STEPS)}.', param_name='step')

        with session_scope(self.db_engine) as db_session:

            # check and get the company
            company = check_and_get_company(symbol, Company, db_session)
            if not company:
                raise falcon.HTTPNotFound(description=(f'Company not found.'))

            # get prediction results and return
            prediction_results = self._bayesian(
                company.symbol, db_session, cost=cost, step=step, days=days)

            # return the prediction results
            resp.status = falcon.HTTP_OK
            resp.media = {'data': prediction_results}

    def _bayesian(self, symbol, db_session, cost=None, step='T', days=1):
        """ Using bayesian curve fitting, predict the next value for the stocks provided
        Args:
            symbol (String): the company symbol to predict data for
            db_session (Database Session): session used to connect to the database
            cost (Float): the cost of the stock if/when it was bought (if the user owns it)
            step (String): The step used to group data and predict:
                e.g. if 'T', data will be grouped by mins and the prediction is for the next min.
                e.g. if 'H', data will be grouped by hour and the prediction is for the next hour.
            days (String): how many business-days worth of data should be used to feed
                into the Bayesian prediction algorithm
        """
        step = step.upper()
        try:
            # create query to filter by symbol and business days
            from_timestamp = pd.Timestamp(pd.Timestamp.utcnow().strftime('%Y-%m-%d')) - BDay(days)
            query = db_session.query(StockRealTime).filter(
                StockRealTime.symbol == symbol,
                StockRealTime.timestamp >= from_timestamp.to_pydatetime()
            )

            # read-in data into a pandas dataframe
            frame = pd.read_sql(query.statement, db_session.bind, index_col='timestamp')
        except Exception as e:
            logger.error(e)
            raise falcon.HTTPInternalServerError(description='Error loading data for prediction.')

        # there is no data to do anything, raise error
        if frame.empty:
            raise falcon.HTTPInternalServerError(
                description=f'{symbol} does not have enough data for prediction')

        # create a series and group the series by 'STEP', get the mean value and drop any NANs
        series = pd.Series(frame.price, index=frame.index)
        frame = series.groupby(pd.Grouper(freq=step)).mean().dropna().to_frame()

        # convert series back to dataframe and get the 'price' column as a list
        data = frame.price.tolist()

        try:
            # use bayesian prediction
            mean, variance, p_range = bayesian.predict(
                data, alpha=self.DEFAULT_ALPHA, beta=self.DEFAULT_BETA, mth=self.DEFAULT_MTH)
        except Exception as e:
            logger.error(e)
            raise falcon.HTTPInternalServerError(
                description='could not run Bayesian curve fitting prediction.')

        # get the prediction based on prices
        last_price = round(data[-1], 2)
        predicted_price = round(p_range[0], 2)
        bought_price = round(cost, 2) if cost else cost
        prediction = compare_price(last_price, predicted_price, bought_price=bought_price)
        prediction_range = None
        prediction_range = '1 minute' if step in ['T', 'MIN'] else prediction_range
        prediction_range = '1 hour' if step in ['H'] else prediction_range
        prediction_range = '1 day' if step in ['D'] else prediction_range

        # return the prediction results
        return {
            'engine': 'bayesian',
            'last_price': last_price,
            'predicted_price': round(mean, 2),
            'predicted_price_range': p_range,
            'prediction_range': prediction_range,
            'prediction': prediction,
            'predicted_variance': variance,
            'predicted_mean_price': round(mean, 2)
        }


class StockPredictionLong:
    """ Resource to run long-term predictions"""

    ALLOWED_ENGINES = ['svm', 'lstm']
    DEFAULT_ENGINE = 'svm'
    DEFAULT_DAYS = 10
    MAX_DAYS = 30

    def __init__(self, engine):
        self.db_engine = engine

    @falcon.before(StockastAuthentication())
    def on_get(self, req, resp, symbol):

        # get parameters
        days = int(req.params.get('days', self.DEFAULT_DAYS))
        engine = req.params.get('engine', self.DEFAULT_ENGINE).lower()
        symbol = symbol.upper()
        cost = req.params.get('cost')
        cost = float(cost) if cost else None

        # check params are proper and allowed
        if not check_params(days, range(1, self.MAX_DAYS+1)):
            raise falcon.HTTPInvalidParam(
                msg=f'Valid values are: {", ".join(range(1, self.MAX_DAYS+1))}.', param_name='days')
        if not check_params(engine, self.ALLOWED_ENGINES):
            raise falcon.HTTPInvalidParam(
                msg=f'Valid values are: {", ".join(self.ALLOWED_ENGINES)}.', param_name='engine')

        with session_scope(self.db_engine) as db_session:

            # check and get the company
            company = check_and_get_company(symbol, Company, db_session)
            if not company:
                raise falcon.HTTPNotFound(description=(f'Company not found.'))

            # get prediction results and return
            if engine == 'svm':
                prediction_results = self._svm(company.symbol, db_session, days=days, cost=cost)
            elif engine == 'lstm':
                prediction_results = self._lstm(company.symbol, db_session, days=days, cost=cost)
            else:
                raise falcon.HTTPInternalServerError(
                    msg=f'The engine selected does not exist')

            # return the prediction results
            resp.status = falcon.HTTP_OK
            resp.media = {'data': prediction_results}

    def _svm(self, symbol, db_session, days=10, cost=None):
        try:
            # create query to filter by symbol and business days
            svm = SVM()
            days_of_data = int(days)
            days_of_data += int(days_of_data * 0.25)
            logger.debug(f'Days of data to get: {days_of_data}')
            from_date = pd.Timestamp(
                pd.Timestamp.utcnow().strftime('%Y-%m-%d')) - BDay(days_of_data)
            logger.debug(f'From date: {from_date}')
            query = db_session.query(StockHistory).filter(
                StockHistory.symbol == symbol,
                StockHistory.date >= from_date.to_pydatetime()
            )

            # read-in data into a pandas dataframe
            frame = pd.read_sql(query.statement, db_session.bind, index_col='date')
            frame.sort_values('date', inplace=True)
        except Exception as e:
            logger.error(e)
            raise falcon.HTTPInternalServerError(description='Error loading data for prediction.')

        # there is no data to do anything, raise error
        if frame.empty:
            raise falcon.HTTPInternalServerError(
                description=f'{symbol} does not have enough data for prediction')

        # calculate the ratios and drop uneeded rows
        logger.debug(f'Length of frame before filtering: {len(frame)}')
        frame = frame.dropna()
        frame = frame.drop(['symbol'], axis=1)
        frame['High_Low_per'] = (frame['day_high'] - frame['day_close']) / frame['day_close']*100
        frame['Per_change'] = (frame['day_close'] - frame['day_open']) / frame['day_open']*100
        frame = frame[['day_close', 'High_Low_per', 'Per_change']]
        frame.fillna(value=-99999, inplace=True)
        logger.debug(f'Length of frame after filtering: {len(frame)}')

        try:
            # use svm prediction
            p_range = svm.predict(symbol, frame, days)
            p_range = p_range.tolist()
        except Exception as e:
            logger.error(e)
            raise falcon.HTTPInternalServerError(
                description='could not run SVM prediction.')

        if len(p_range) < days:
            raise falcon.HTTPInternalServerError(
                description=f'Not enough predicted points for requested days: {days}')

        logger.debug(f'Price Range: {p_range}')
        # get the prediction based on prices
        last_price = frame[["day_close"]].values[-1][0]
        last_price = round(last_price, 2)
        predicted_price = round(p_range[(days-1)], 2)
        bought_price = round(cost, 2) if cost else cost
        prediction = compare_price(last_price, predicted_price, bought_price=bought_price)

        # return the prediction results
        return {
            'engine': 'svm',
            'last_price': last_price,
            'predicted_price': predicted_price,
            'predicted_price_range': p_range,
            'prediction_range': f'{days} days',
            'prediction': prediction
        }

    def _lstm(self, symbol, db_session, days=10, cost=None):
        try:
            # create query to filter by symbol and business days
            lstm = LSTM()
            days_of_data = int(lstm.data_needed)
            days_of_data += int(days_of_data * 0.25)
            logger.debug(f'Days of data to get: {days_of_data}')
            from_date = pd.Timestamp(
                pd.Timestamp.utcnow().strftime('%Y-%m-%d')) - BDay(days_of_data)
            logger.debug(f'From date: {from_date}')
            query = db_session.query(StockHistory).filter(
                StockHistory.symbol == symbol,
                StockHistory.date >= from_date.to_pydatetime()
            )

            # read-in data into a pandas dataframe
            frame = pd.read_sql(query.statement, db_session.bind, index_col='date')
            frame.sort_values('date', inplace=True)
        except Exception as e:
            logger.error(e)
            raise falcon.HTTPInternalServerError(description='Error loading data for prediction.')

        # there is no data to do anything, raise error
        if frame.empty:
            raise falcon.HTTPInternalServerError(
                description=f'{symbol} does not have enough data for prediction')

        # calculate the ratios and drop uneeded rows
        frame = frame.dropna()
        frame = frame.drop(['symbol'], axis=1)
        logger.debug(f'Length of data frame: {len(frame)}')

        try:
            # use svm prediction
            p_range = lstm.predict(symbol, frame, days)
        except Exception as e:
            logger.error(e)
            raise falcon.HTTPInternalServerError(
                description='could not run SVM prediction.')

        if len(p_range) < days:
            raise falcon.HTTPInternalServerError(
                description=f'Not enough predicted points for requested days: {days}')

        logger.debug(f'Price Range: {p_range}')
        # get the prediction based on prices
        last_price = frame[["day_close"]].values[-1][0]
        last_price = round(last_price, 2)
        predicted_price = round(p_range[(days-1)], 2)
        bought_price = round(cost, 2) if cost else cost
        prediction = compare_price(last_price, predicted_price, bought_price=bought_price)

        # return the prediction results
        return {
            'engine': 'lstm',
            'last_price': last_price,
            'predicted_price': predicted_price,
            'predicted_price_range': p_range,
            'prediction_range': f'{days} days',
            'prediction': prediction
        }
