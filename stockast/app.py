import falcon
import logging

from falcon_autocrud.middleware import Middleware
from sqlalchemy import create_engine

from stockast import config
from stockast.models import Base
from stockast.resources import user
from stockast.resources import company
from stockast.resources import stocks
from stockast.utils import parse_bool

logger = logging.getLogger(__name__)

# database initialization
engine = create_engine(config.DATABASE_URL, echo=parse_bool(config.DATABASE_DEBUG))
Base.metadata.create_all(engine)

# falcon.API instances are callable WSGI apps
application = falcon.API(middleware=[Middleware()])

# paths and resources
# application.add_route('/login', user.LoginResource())
application.add_route('/users', user.UserCollectionResource(engine))
application.add_route('/users/{id}', user.UserResource(engine))
application.add_route('/users/{id}/follows', user.UserFollowsCollectionResource(engine))
application.add_route('/users/{id}/follows/{symbol}', user.UserFollowsResource(engine))
application.add_route('/companies', company.CompanyCollectionResource(engine))
application.add_route('/companies/{symbol}', company.CompanyResource(engine))
application.add_route('/stocks/history', stocks.StockHistoryCollectionResource(engine))
application.add_route('/stocks/realtime', stocks.StockRealTimeCollectionResource(engine))
