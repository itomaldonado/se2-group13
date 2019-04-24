import falcon
import logging

from falcon_autocrud.middleware import Middleware
from sqlalchemy import create_engine

from stockast import config
from stockast.models import Base
from stockast.resources import company
from stockast.resources import health
from stockast.resources import stocks
from stockast.resources import user

logger = logging.getLogger(__name__)

# database initialization
engine = create_engine(config.DATABASE_URL, echo=config.DATABASE_DEBUG)
Base.metadata.create_all(engine)

# falcon.API instances are callable WSGI apps
application = falcon.API(middleware=[Middleware()])

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
# TODO: models
# TODO: predict
