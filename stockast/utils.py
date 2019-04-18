from distutils.util import strtobool
from stockast.models import User
from datetime import datetime
from falcon import HTTPUnauthorized

# SQL insert ignore options
ignore_stmt = {
    'sqlite': 'OR IGNORE',
    'mysql': 'IGNORE',
}


def parse_companies(companies, show=False):
    """Parses the IEXCollector response of companies into a list of dictionaries"""
    objects = []
    if show:
        print(f'symbol,name,exchange')
    for symbol, info in companies.items():
        item = {'symbol': info['symbol'], 'name': info['companyName'], 'exchange': info['exchange']}
        if show:
            print(f'{item["symbol"]},{item["name"]},{item["exchange"]}')
        objects.append(item)
    return objects


def parse_companies_dict(companies, show=False):
    objects = parse_companies(companies, show)
    return {item['symbol']: item for item in objects}


def parse_historical_data(history, show=False):
    """Parses the IEXCollector response of historical data into a list of dictionaries"""
    objects = []
    if show:
        print(f'symbol,date,open,high,low,close,volume')
    for symbol, history in history.items():
            for datestamp, prices in history.items():
                item = {
                    'symbol': symbol,
                    'date': datetime.strptime(datestamp, '%Y-%m-%d'),
                    'day_open': prices['open'],
                    'day_close': prices['close'],
                    'day_high': prices['high'],
                    'day_low': prices['low'],
                    'day_volume': prices['volume']
                }
                if show:
                    print(
                        f'{item["symbol"]},{item["date"]},{item["day_open"]},{item["day_high"]},'
                        f'{item["day_low"]},{item["day_close"]},{item["day_volume"]}')
                objects.append(item)
    return objects


def parse_realtime_data(timestamp, rt_data, show=False):
    """Parses the IEXCollector response of historical data into a list of dictionaries"""
    objects = []
    if show:
        print(f'symbol,timestamp,price')
    for symbol, price in rt_data.items():
        item = {'symbol': symbol, 'timestamp': timestamp, 'price': price}
        if show:
            print(
                f'{item["symbol"]},{item["timestamp"]},{item["price"]}')
        objects.append(item)
    return objects


def insert_ignore_dups(engine, session, model, values):
    """Inserts the values into the model's table in bulk, ignoring duplicates
    *Note*: Only works for MySQL and SQLite
    """
    try:
        engine.execute(
            model.__table__.insert().prefix_with(ignore_stmt[engine.dialect.name]), values)
        session.commit()
    except Exception as e:
        print(f'Could not save into {model.__table__}: {e}')
        session.rollback()


def parse_bool(v):
    """ Converts a string to boolean representation
    Args:
        v (String): value to convert
    Returns:
        Boolean: True values are y, yes, t, true, on and 1;
                 False: anything else.
    """
    try:
        return bool(strtobool(str(v)))
    except ValueError:
        return False


# user-loader function for authentication
def user_loader(username, password):
    """ Load a user from the database and compare its password"""

    # get user from DB
    user = User.query.filter_by(email=username).first()

    # if we found a user and the password matches, return user as dict
    if user and user.password == password:
        user = user._as_dict()
        user.pop('password')
        return user

    # for every other scenario, raise a 401 error
    raise HTTPUnauthorized(description='invalid user or password.')
