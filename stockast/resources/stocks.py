import logging

from falcon_autocrud.resource import CollectionResource
from stockast.models import StockHistory, StockRealTime

logger = logging.getLogger(__name__)


class StockHistoryCollectionResource(CollectionResource):
    """ Makse CRUD-like resource for stock history collections"""
    model = StockHistory
    methods = ['GET']
    default_sort = ['symbol', 'date']


class StockRealTimeCollectionResource(CollectionResource):
    """ Makse CRUD-like resource for real-time stock collections"""
    model = StockRealTime
    methods = ['GET']
    default_sort = ['symbol', 'timestamp']
