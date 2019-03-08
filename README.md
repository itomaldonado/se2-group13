# se2-group13
Software Engineering 2 - Group 13 Project

## Requirements:
* [Python 3.7](https://www.python.org/downloads/release/python-372/)
* [pip](https://pip.pypa.io/en/stable/installing/)
* (Optional) [Vritual Environment](https://virtualenv.pypa.io/en/latest/installation/)
* An account with [IEX Cloud](http://iexcloud.io/) and an API Token
* A running `MySQL` database or a path to a `SQLite` database.

## Installation & Configuration (Unix/Linux/MacOS):
* (Optional) Set-up a virtual environment:
	* Change into the directory: `cd /path/to/se2-group13/`
  * Create environment: `virtualenv ./venv`
  * Activate environment: `source ./venv/bin/activate`
* Install all project dependencies: `pip install -r requirements.txt`
* Export IEX Cloud token to your environment: `export IEX_TOKEN=<IEX_API_TOKEN_HERE>`

## Collectors
The collectors seen on this section will get data for 10 different stocks (hard-coded symbols). The symbols are:
```
[
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
```

Before running a collector, the assumption is that you have a database running (like `MySQL`)
or you are going to use `SQLite`.

### Historical Data Collector
* Display Help Menu
```
$ python get-historical-stock-data.py --help

Usage: get-historical-stock-data.py [OPTIONS] DATABASE_URL

Options:
  --debug
  --token TEXT                    IEX Cloud API Token
  -f, --from-date [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]
                                  From date to get data
  -t, --to-date [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]
                                  To date to get data
  --help                          Show this message and exit.
```

* Run the collector with defaults
```
$ python get-historical-stock-data.py <database connection string>
```

* Run the collector with specified date range
```
$ python get-historical-stock-data.py --from-date 2019-01-01 --to-date 2019-01-31 <database connection string>
```

* Run the collector with defaults and debug mode on
```
$ python get-historical-stock-data.py --debug <database connection string>
```

### Real-Time Data Collector
* Display Help Menu
```
$ python get-realtime-stock-data.py --help

Usage: get-realtime-stock-data.py [OPTIONS] DATABASE_URL

Options:
  --debug
  --token TEXT  IEX Cloud API Token
  --help        Show this message and exit.
```

* Run the collector
```
$ python get-realtime-stock-data.py <database connection string>
```

* Run the collector with debug mode on
```
$ python get-realtime-stock-data.py --debug <database connection string>
```


### Database Connection Strings:

We only support **two** database types: `MySQL` and `SQLite`. The format for the connection strings
for each can be seen below and is further explained [here](https://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls).

* `MySQL`: `mysql://<user>:<password>@<hostname>:<port>/<database>`
	* example: `mysql://scott:tiger@localhost:3306/foo`
* `SQLite`: `sqlite:///<path>`
	* example: `sqlite:///db.sqlite3`


## Real-Time Collection

To collect real-time information, we use the [real-time collector](#real-time-data-collector) and a [cron job](https://en.wikipedia.org/wiki/Cron) that runs every minute from 9:00 AM to 1:00 PM EST (30 mins before open to close of NYSE hours) Monday through Friday.

The cron expression for this is: `* 13-21 * * 1-5` and can be explained [here](https://crontab.guru/#*_13-21_*_*_1-5)

The full cron command would be:
```
# cd into script folder: /path/to/se2-group13
# use the virtual environment's python: /path/to/se2-group13/venv/bin/python
# call realtime script with IEX_TOKEN and database connection string

* 13-21 * * 1-5 cd /path/to/se2-group13 && /path/to/se2-group13/venv/bin/python /path/to/se2-group13/get-realtime-stock-data.py -t <IEX_TOKEN> <database connection string>
```