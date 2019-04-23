import os

# General configuration
LOG_LEVEL = os.getenv('STOCKAST_LOG_LEVEL', 'INFO').upper()


# Collector configuration
IEX_CLOUD_TOKEN = os.getenv('STOCKAST_IEX_CLOUD_TOKEN')


# Database configuration
DATABASE_DEBUG = os.getenv('STOCKAST_DATABASE_DEBUG', 'false')
DATABASE_URL = os.getenv('STOCKAST_DATABASE_URL')
# re-write the 'mysql' engine to 'mysql+pymysql'
if DATABASE_URL.lower().startswith('mysql'):
    DATABASE_URL = ":".join(DATABASE_URL.split(":")[1:])
    DATABASE_URL = f'mysql+pymysql:{DATABASE_URL}'


# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '[{asctime}] [{levelname}] [{pathname:s} {lineno}]: {message}',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
        }
    }
}
