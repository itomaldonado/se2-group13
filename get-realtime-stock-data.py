import click
import os

from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from stockast.collectors import IEXStockCollector
from stockast.models import Base
from stockast.models import StockRealTime

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
@click.argument('database_url')
def download_realtime_data(debug, token, database_url):
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
        data = collector.get_real_time_data(symbols)

        # parse data into a list of StockRealTime objects
        objects = []
        now = datetime.utcnow()
        for symbol, price in data.items():
            objects.append(StockRealTime(symbol=symbol, timestamp=now, price=price))

        # save StockRealTime objects in bulk and commit transaction
        session.bulk_save_objects(objects)
        session.commit()
    finally:
        # attempt to close db connection even if there are errors
        session.close()


if __name__ == '__main__':
    download_realtime_data()
