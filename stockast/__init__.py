import logging
import logging.config

from stockast import config

logging.config.dictConfig(config.LOGGING)
