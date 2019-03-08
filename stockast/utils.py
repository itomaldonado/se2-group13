from datetime import datetime

# SQL insert ignore options
ignore_stmt = {
    'sqlite': 'OR IGNORE',
    'mysql': 'IGNORE',
}


def parse_companies(companies):
    """Parses the IEXCollector response of companies into a list of dictionaries"""
    objects = []
    for symbol, info in companies.items():
        objects.append({
            'symbol': info['symbol'],
            'name': info['companyName'],
            'exchange': info['exchange'],
        })
    return objects


def parse_historical_data(history):
    """Parses the IEXCollector response of historical data into a list of dictionaries"""
    objects = []
    for symbol, history in history.items():
            for datestamp, prices in history.items():
                objects.append(
                    {
                        'symbol': symbol,
                        'date': datetime.strptime(datestamp, '%Y-%m-%d'),
                        'day_open': prices['open'],
                        'day_close': prices['close'],
                        'day_high': prices['high'],
                        'day_low': prices['low'],
                        'day_volume': prices['volume']
                    }
                )
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
