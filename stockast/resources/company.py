import falcon
import logging

from falcon_autocrud.auth import identify
from falcon_autocrud.resource import CollectionResource, SingleResource

from stockast import config
from stockast.authentication import StockastAuthentication
from stockast.collectors import IEXStockCollector
from stockast.models import Company
from stockast.utils import parse_companies_dict

logger = logging.getLogger(__name__)


@identify(StockastAuthentication)
class CompanyCollectionResource(CollectionResource):
    """ Makse CRUD-like resource for company collections"""
    model = Company
    methods = ['GET', 'POST']
    default_sort = ['symbol']

    def before_post(self, req, resp, db_session, resource, *args, **kwargs):
        """ Check that the company exists (by the symbol) and
        replace information with the one from IEX Cloud.
        """
        collector = IEXStockCollector(config.IEX_CLOUD_TOKEN)
        resource.symbol = resource.symbol.upper()
        try:
            info = collector.get_company_info(resource.symbol)
            info = parse_companies_dict(info)
            info = info[resource.symbol]
            resource.name = info['name']
            resource.symbol = info['symbol']
            resource.exchange = info['exchange']
        except Exception as e:
            logger.error(e)
            raise falcon.HTTPBadRequest(
                description='could not validate the company symbol provided')


@identify(StockastAuthentication)
class CompanyResource(SingleResource):
    """ Makse CRUD-like resource for a single company"""
    model = Company
    lookup_attr_map = {
        'symbol': lambda req, resp, query, *args, **kwargs:
            query.filter(Company.symbol == kwargs['symbol'].upper())
    }
