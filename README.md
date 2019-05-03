# se2-group13
Software Engineering 2 - Group 13 Project, broken down into two mayor components:
* `stockast`: the stockast api server written in python
* `stockast-ui`: the stockast web ui written in HTML/CSS/Javascript/Vuejs


## Stockast API Server

The stockast API server is written in python [falcon](https://falcon.readthedocs.io/en/stable/), and can run in `docker` or standalone with python and `gunicorn`.


Stockast's public API documentation can be found at: https://bit.ly/stockast-api-docs


### Requirements:
* An account with [IEX Cloud](http://iexcloud.io/) and an API Token
* A running `MySQL` database or a path to a `SQLite` database
* For running with python and `gunicorn`:
  * [Python 3.7](https://www.python.org/downloads/release/python-372/)
  * [pip](https://pip.pypa.io/en/stable/installing/)
  * (Optional) [Vritual Environment](https://virtualenv.pypa.io/en/latest/installation/)
* For running in docker:
  * [Docker](https://docs.docker.com/install/)
  * [docker-compose](https://docs.docker.com/compose/install/)


### Installation & Configuration

Stockast can be installed in one of two ways, using docker or using plain python. We show both ways here.

#### Installation, Configuration & Running (Unix/Linux/MacOS/Windows) - Docker:
* Export IEX Cloud token to your environment: `export STOCKAST_IEX_CLOUD_TOKEN=<IEX_API_TOKEN_HERE>`
* Change into the directory: `cd /path/to/se2-group13/`
* Run: `docker-compose up -d`
  * Note, this will start three services: a mysql database (on port `3306`), the stockast-api (on port `8000`) and the stockast-ui (on port `80`)
* Navigate to `http://localhost:80` to see the UI
* Navigate to `http://localhost:8000/status` to see the status of the stockast API

#### Installation, Configuration & Running (Unix/Linux/MacOS) - Python:
* (Optional) Set-up a virtual environment:
	* Change into the directory: `cd /path/to/se2-group13/`
  * Create environment: `virtualenv ./venv`
  * Activate environment: `source ./venv/bin/activate`
* Install all project dependencies: `pip install -r ./stockast/requirements.txt`
* Export IEX Cloud token to your environment: `export STOCKAST_IEX_CLOUD_TOKEN=<IEX_API_TOKEN_HERE>`
* Export the database url (use SQLite when running locally) `export STOCKAST_DATABASE_URL=sqlite:///$(pwd)/stockast.db`
* Run the stockast-api server: `gunicorn stockast.app`
* The stockast-ui is a simple static web site so you can open the file `./stockast-ui/www/index.html` in your browser
* Navigate to `http://localhost:8000/status` to see the status of the stockast API

#### API Configuration

The stockast API server is configured using environmental variables, here is the list of available configuration:

* `STOCKAST_IEX_CLOUD_TOKEN`: the IEX cloud token
* `STOCKAST_DATABASE_URL`: the database url used for stockast, supports only SQLite or MySQL
* `STOCKAST_LOG_LEVEL`: controls the log level: `DEBUG`, `INFO`, `WARN`, `ERROR`
* `STOCKAST_DATABASE_DEBUG`: show debug information of database interactions
* `STOCKAST_API_PREFIX`: if the paths served by the API server need a prefix (e.g. `/api/` or `/v1`) this controls that prefix
* `STOCKAST_ADMIN_USER_EMAIL`: the email address of the admin user, this user can do things on behalf of other users


## Stockast Web User Interface (UI)

The stockast API server is written in plain HTML, CSS and javascript with the help of [Vuejs](https://vuejs.org/).


### Installation & Configuration

UI is currently configured to connect to the public API: `https://stockast.itomaldonado.com`.

#### Installation, Configuration & Running (Unix/Linux/MacOS/Windows) - Docker:
* Export IEX Cloud token to your environment: `export STOCKAST_IEX_CLOUD_TOKEN=<IEX_API_TOKEN_HERE>`
* Change into the directory: `cd /path/to/se2-group13/`
* Run: `docker-compose up -d`
  * Note, this will start three services: a mysql database (on port `3306`), the stockast-api (on port `8000`) and the stockast-ui (on port `80`)
* Navigate to `http://localhost:80` to see the UI
* Navigate to `http://localhost:8000/status` to see the status of the stockast API

#### Installation, Configuration & Running (Unix/Linux/MacOS/Windows) - Locally:
* Simply open the following file with your preferred web browser: 
```
/path/to/se2-group13/stockast-ui/www/index.html
```


## Stockast Data Collectors
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
$ python python get-historical-stock-data.py --help

Usage: get-historical-stock-data.py [OPTIONS] DATABASE_URL

Options:
  --debug                         Show queries
  -s, --show-data                 Show data downloaded
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
  --debug          Show queries
  -s, --show-data  Show data downloaded
  --token TEXT     IEX Cloud API Token
  --help           Show this message and exit.
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


### Continuous Historical & Real-Time Data Collection

To conituously collect historical and real-time stock information, we use the both collectors ([real-time collector](#real-time-data-collector)) and a [cron job](https://en.wikipedia.org/wiki/Cron).

For historical data, it runs in the mornings at 5 minutes past 1:00 AM, Monday through Friday, which will collect the historical information of all tracked companies for the day before. An example is cron expression is seen below:

```
# historical -1 day collection
5 5 * * 1-5 docker run --rm itomaldonado/stockast-api:latest python get-historical-stock-data.py --token <IEX_TOKEN> --from-date=$(date -d "-5 days" +'%Y-%m-%d') --to-date=$(date +'%Y-%m-%d') <database connection string> >> /path/to/logs/historical.log 2>&1
```
The cron expression used for historical data is: `5 5 * * 1-5` and can be explained [here](https://crontab.guru/#5_5_*_*_1-5)

For real-time data, it runs every minute from 9:00 AM to 1:00 PM EST (30 mins before open to close of NYSE hours) Monday through Friday, which collects the strike-price of all tracked stocks. An example is seen below:

```
# real-time collection
* 13-21 * * 1-5 docker run --rm itomaldonado/stockast-api:latest python get-realtime-stock-data.py --token <IEX_TOKEN> <database connection string> >> /path/to/logs/real-time.log 2>&1
```

The cron expression used for real-time data is: `* 13-21 * * 1-5` and can be explained [here](https://crontab.guru/#*_13-21_*_*_1-5)


## Database Schema

Included is also the database schema for the project. It can be found at: `./database-schema/stockast.pdf`.


## Data Dumps

The folder: `./data-dumps` contains three files with the historical and real-time information collected.

* Dump of companies information table: `./data-dumps/companies.csv`
* Dump of historical stocks data: `./data-dumps/stocks_history.csv`
* Dump of real-time stocks data: `./data-dumps/stocks_real_time.csv`


## Stockast Modeling

The folder `/path/to/se2-group13/stockast-models` contains an assortment of one-of files used during the machine learning modeling process and may not be completely usable on their own.
