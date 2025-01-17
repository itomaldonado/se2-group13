import click
import logging
import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from stockast.collectors import IEXStockCollector
from stockast.models import Base
from stockast.models import Company
from stockast.models import StockHistory
from stockast.utils import insert_ignore_dups, parse_companies, parse_historical_data

logger = logging.getLogger(__name__)

# list of tickets to pull data for
default_symbols = [
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
@click.option('--debug', is_flag=True, help="Show queries")
@click.option('--show-data', '-s', is_flag=True, help="Show data downloaded")
@click.option('--token', default=os.getenv('STOCKAST_IEX_CLOUD_TOKEN'), help='IEX Cloud API Token')
@click.option(
    '--from-date', '-f', default='2018-01-01', type=click.DateTime(), help='From date to get data')
@click.option(
    '--to-date', '-t', default='2018-12-31', type=click.DateTime(), help='To date to get data')
@click.argument('database_url')
def download_historical_data(debug, show_data, token, from_date, to_date, database_url):
    # Normalize symbols to a list of uppercase symbols
    symbols = default_symbols
    if symbols and type(symbols) != list:
            symbols = [symbols]
    symbols = [x.upper() for x in symbols]

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

        # create or get company names
        data = collector.get_company_info(symbols)

        # parse data into list of Company objects
        objects = parse_companies(data, show=show_data)

        # save Companies objects in bulk and commit transaction ignore dups
        insert_ignore_dups(engine, session, Company, objects)

        # get the historical data
        data = collector.get_historical_data(symbols, from_date, to_date)

        # parse data into a list of StockHistory objects
        objects = parse_historical_data(data, show=show_data)

        # save StockHistory objects in bulk and commit transaction ignore dups
        logger.info(f'Inserting: {objects}')
        insert_ignore_dups(engine, session, StockHistory, objects)
    finally:
        # attempt to close db connection even if there are errors
        session.close()


if __name__ == '__main__':
    download_historical_data()
