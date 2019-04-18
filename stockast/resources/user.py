import logging

from falcon_autocrud.resource import CollectionResource, SingleResource
from stockast.models import User

logger = logging.getLogger(__name__)


class UserCollectionResource(CollectionResource):
    """ Makse CRUD-like resource for user collections"""
    model = User
    methods = ['GET', 'POST']
    default_sort = ['email']


class UserResource(SingleResource):
    """ Makse CRUD-like resource for single users"""
    model = User
