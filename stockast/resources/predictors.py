import falcon
import logging
import pandas as pd
import tulipy as ti

from falcon_autocrud.db_session import session_scope
from pandas.tseries.offsets import BDay

from stockast.authentication import StockastAuthentication
from stockast.models import Company, StockHistory
from stockast.utils import check_and_get_company

logger = logging.getLogger(__name__)


class StockPredictors:
    """ Resource to run short-term predictions"""

    DEFAULT_DAYS = 5

    def __init__(self, engine):
        self.db_engine = engine

    @falcon.before(StockastAuthentication())
    def on_get(self, req, resp, symbol):

        # get parameters
        days = int(req.params.get('days', self.DEFAULT_DAYS))
        symbol = symbol.upper()

        # return dictionary
        predictiors = {}

        with session_scope(self.db_engine) as db_session:

            # check and get the company
            company = check_and_get_company(symbol, Company, db_session)
            if not company:
                raise falcon.HTTPNotFound(description=(f'Company not found.'))

            try:
                # get prediction results and return
                today = pd.Timestamp.utcnow().strftime('%Y-%m-%d')
                from_date = pd.Timestamp(today) - BDay(days + 10)
                query = db_session.query(StockHistory).filter(
                    StockHistory.symbol == symbol,
                    StockHistory.date >= from_date.to_pydatetime()
                )
                # read-in data into a pandas data-frame
                frame = pd.read_sql(query.statement, db_session.bind, index_col='date')
            except Exception as e:
                logger.error(e)
                raise falcon.HTTPInternalServerError(
                    description='Error loading data for predictors.')

                # there is no data to do anything, raise error
            if frame.empty:
                raise falcon.HTTPInternalServerError(
                    description=f'{symbol} does not have enough data to calculate the predictors')

            # calculate predictors and add the data to the return dictionary
            predictiors.update({'stddev': self._calculate_stddev(frame, days)})
            predictiors.update({'rsi': self._calculate_rsi(frame, days)})
            predictiors.update({'willr': self._calculate_willr(frame, days)})
            predictiors.update({'wma': self._calculate_wma(frame, days)})
            predictiors.update({'vwma': self._calculate_vwma(frame, days)})

            # return the prediction results
            resp.status = falcon.HTTP_OK
            resp.media = {'data': predictiors}

    def _calculate_stddev(self, df, period):
        """ Calculates the Standard Deviation for the period given"""

        # Tail the data-frame to the needed data
        data = df.tail(period)[['day_close', 'day_volume']].astype('float64')
        return ti.stddev(data['day_close'].values, period=float(period))[0]

    def calculate_stddev(self, df, period):
        """ Calculates the Standard Deviation for the period given"""

        # Tail the data-frame to the needed data
        data = df.tail(period)[['day_close', 'day_volume']].astype('float64')
        return ti.stddev(data['day_close'].values, period=float(period))[0]

    def _calculate_rsi(self, df, period):
        """ Calculates the RSI for the period given"""

        # Tail the data-frame to the needed data
        data = df.tail(period+1)
        return ti.rsi(data['day_close'].values, period)[0]

    def _calculate_willr(self, df, period):
        """ Calculates the Williams %R for the period given"""

        # Tail the data-frame to the needed data
        data = df.tail(period)
        return ti.willr(
            high=data['day_high'].values,
            low=data['day_low'].values,
            close=data['day_close'].values,
            period=period
        )[0]

    def _calculate_wma(self, df, period):
        """ Calculates the Weighted Moving Average for the period given"""

        # Tail the data-frame to the needed data
        data = df.tail(period)[['day_close', 'day_volume']].astype('float64')
        return ti.wma(data['day_close'].values, period=float(period))[0]

    def _calculate_vwma(self, df, period):
        """ Calculates the Volume Weighted Moving Average for the period given"""

        # Tail the data-frame to the needed data
        data = df.tail(period)[['day_close', 'day_volume']].astype('float64')
        return ti.vwma(
            close=data['day_close'].values,
            volume=data['day_volume'].values,
            period=float(period)
        )[0]
