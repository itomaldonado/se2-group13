import logging

from falcon_autocrud.resource import CollectionResource, SingleResource
from stockast.models import User

logger = logging.getLogger(__name__)


class SignUpResource(CollectionResource):
    """ Makse CRUD-like resource for user collections"""
    auth = {'auth_disabled': True}
    model = User
    methods = ['POST']
    response_fields = ['id', 'name', 'email']


class UserCollectionResource(CollectionResource):
    """ Makse CRUD-like resource for user collections"""
    model = User
    methods = ['GET']
    default_sort = ['email']
    response_fields = ['id', 'name', 'email']


class UserResource(SingleResource):
    """ Makse CRUD-like resource for single users"""
    model = User
    response_fields = ['id', 'name', 'email']
