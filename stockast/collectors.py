import datetime
import os
import requests_cache


from iexfinance import stocks


class IEXStockCollector(object):

    def __init__(self, token, output_format='json', cache_expire_days=7):
        # set-up IEX cloud API access
        os.environ['IEX_API_VERSION'] = 'iexcloud-beta'

        self.token = token
        self.output_format = output_format

        # session to cache data
        self.expiry = datetime.timedelta(days=cache_expire_days)
        self.session = requests_cache.CachedSession(
            cache_name='iexcache', backend='sqlite',
            expire_after=self.expiry, ignored_parameters='token')

    def get_company_info(self, symbols):
        if symbols and type(symbols) != list:
            symbols = [symbols]

        batch = stocks.Stock(
            symbols,
            token=self.token,
            output_format=self.output_format
        )
        info = batch.get_company()

        # if there was only one symbol
        # convert to proper dictionary response
        # else return what was downloaded as is
        return {symbols[0]: info} if len(symbols) == 1 else info

    def get_historical_data(self, symbols, from_date, to_date):
        """ Gets stocks historical data, which includes:
            date, open, high, low, close, volumes

        Args:
            symbols: list of strings, symbols to get data from
            from_date: datetime object to search from
            to_date: datetime object to search to

        Returns:
            historical data in the format:
            {
                'TICKER1': {
                    "2018-01-01": {
                        "open": 1000.00,
                        "high": 1000.00,
                        "low": 1000.00,
                        "close": 1000.00,
                        "volume": 1234567890
                    },
                    "2018-01-02": {
                        "open": 1000.00,
                        "high": 1000.00,
                        "low": 1000.00,
                        "close": 1000.00,
                        "volume": 1234567890
                    },
                },
                'TICKER2': {...},
                'TICKER3': {...},
            }
        """
        if symbols and type(symbols) != list:
            symbols = [symbols]

        history = stocks.get_historical_data(
            symbols,
            start=from_date,
            end=to_date,
            token=self.token,
            output_format=self.output_format,
            session=self.session
        )

        # if there was only one symbol
        # convert to proper dictionary response
        # else return what was downloaded as is
        return {symbols[0]: history} if len(symbols) == 1 else history

    def get_real_time_data(self, symbols):
        """ Gets real-time/current stock prices.
        Args:
            symbols: list of strings, symbols to get data from

        Returns:
            real-time data in the format:
            {
                'TICKER1': {},
                'TICKER2': {},
                'TICKER3': {},
            }
        """
        if symbols and type(symbols) != list:
            symbols = [symbols]

        batch = stocks.Stock(
            symbols,
            token=self.token,
            output_format=self.output_format
        )
        prices = batch.get_price()

        # if there was only one symbol
        # convert to proper dictionary response
        # else return what was downloaded as is
        return {symbols[0]: prices} if len(symbols) == 1 else prices
