import falcon

from falcon_auth import FalconAuthMiddleware
from falcon_auth import BasicAuthBackend
from falcon_autocrud.middleware import Middleware
from sqlalchemy import create_engine

from stockast import config
from stockast.models import Base
from stockast.resources import user
from stockast.resources import company
from stockast.resources import stocks
from stockast.utils import parse_bool
from stockast.utils import user_loader

# database initialization
engine = create_engine(config.DATABASE_URL, echo=parse_bool(config.DATABASE_DEBUG))
Base.metadata.create_all(engine)

# authentication middleware
auth_middleware = FalconAuthMiddleware(BasicAuthBackend(user_loader), exempt_methods=['HEAD'])

# falcon.API instances are callable WSGI apps
# application = falcon.API(middleware=[auth_middleware, Middleware()])
application = falcon.API(middleware=[Middleware()])

# paths and resources
application.add_route('/users', user.UserCollectionResource(engine))
application.add_route('/users/{id}', user.UserResource(engine))
application.add_route('/companies', company.CompanyCollectionResource(engine))
application.add_route('/companies/{id}', company.CompanyResource(engine))
application.add_route('/stocks/history', stocks.StockHistoryCollectionResource(engine))
application.add_route('/stocks/realtime', stocks.StockRealTimeCollectionResource(engine))
