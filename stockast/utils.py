from datetime import datetime

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
