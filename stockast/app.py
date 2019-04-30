import falcon
import logging

from falcon_autocrud.middleware import Middleware
from falcon_cors import CORS
from sqlalchemy import create_engine

from stockast import config
from stockast.models import Base
from stockast.resources import company
from stockast.resources import health
from stockast.resources import stocks
from stockast.resources import user
from stockast.resources import prediction

logger = logging.getLogger(__name__)

# CORS
cors = CORS(
    allow_all_origins=True,
    allow_all_headers=True,
    allow_all_methods=True,
    allow_credentials_all_origins=True)

# database initialization
engine = create_engine(config.DATABASE_URL, echo=config.DATABASE_DEBUG)
Base.metadata.create_all(engine)

# falcon.API instances are callable WSGI apps
application = falcon.API(middleware=[Middleware(), cors.middleware])

# paths and resources
application.add_route(
    config.API_PREFIX + 'status', health.StatusResource())
application.add_route(
    config.API_PREFIX + 'login', user.LoginResource(engine))
application.add_route(
    config.API_PREFIX + 'users', user.UserCollectionResource(engine))
application.add_route(
    config.API_PREFIX + 'users/{id}', user.UserResource(engine))
application.add_route(
    config.API_PREFIX + 'users/{id}/follows', user.UserFollowsCollectionResource(engine))
application.add_route(
    config.API_PREFIX + 'users/{id}/follows/{symbol}', user.UserFollowsResource(engine))
application.add_route(
    config.API_PREFIX + 'companies', company.CompanyCollectionResource(engine))
application.add_route(
    config.API_PREFIX + 'companies/{symbol}', company.CompanyResource(engine))
application.add_route(
    config.API_PREFIX + 'stocks/history', stocks.StockHistoryCollectionResource(engine))
application.add_route(
    config.API_PREFIX + 'stocks/realtime', stocks.StockRealTimeCollectionResource(engine))
application.add_route(
    config.API_PREFIX + 'predict/short/{symbol}', prediction.StockPredictionShort(engine))
application.add_route(
    config.API_PREFIX + 'stocks/long/{symbol}', prediction.StockPredictionLong(engine))
# TODO: models
# TODO: predict
