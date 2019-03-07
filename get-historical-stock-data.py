import click
import os

from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from stockast.collectors import IEXStockCollector
from stockast.models import Base
from stockast.models import StockHistory

# list of tickets to pull data for
symbols = [
    'AABA',
    'AAPL',
    'ADBE',
    'AMZN',
    'FB',
    'GOOG',
    'JPM',
    'MSFT',
    'NVDA',
    'TSLA',
]


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--token', default=os.getenv('IEX_TOKEN'), help='IEX Cloud API Token')
@click.option(
    '--from-date', '-f', default='2018-01-01', type=click.DateTime(), help='From date to get data')
@click.option(
    '--to-date', '-t', default='2018-12-31', type=click.DateTime(), help='To date to get data')
@click.argument('database_url')
def download_historical_data(debug, token, from_date, to_date, database_url):
    # databse Engine
    # example: 'sqlite:////Users/mmaldonadofigueroa/Desktop/test.db'
    engine = create_engine(database_url, echo=debug)

    # create all tables if needed
    Base.metadata.create_all(engine)

    # create session
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    try:
        # create the collector
        collector = IEXStockCollector(token)

        # get the historical data
        data = collector.get_historical_data(symbols, from_date, to_date)

        # parse data into a list of StockHistory objects
        objects = []
        for symbol, history in data.items():
            for datestamp, prices in history.items():
                objects.append(
                    StockHistory(
                        symbol=symbol,
                        date=datetime.strptime(datestamp, '%Y-%m-%d'),
                        day_open=prices['open'],
                        day_close=prices['close'],
                        day_high=prices['high'],
                        day_low=prices['low'],
                        day_volume=prices['volume']
                    )
                )
        # save StockHistory objects in bulk and commit transaction
        session.bulk_save_objects(objects)
        session.commit()
    finally:
        # attempt to close db connection even if there are errors
        session.close()


if __name__ == '__main__':
    download_historical_data()
