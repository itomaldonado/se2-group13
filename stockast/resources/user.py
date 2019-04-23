import logging

from falcon_autocrud.auth import authorize, identify
from falcon_autocrud.resource import CollectionResource, SingleResource

from stockast.authentication import StockastAuthentication
from stockast.authentication import StockastFollowUpdateAuthorization
from stockast.authentication import StockastUserUpdateAuthorization
from stockast.models import Follows
from stockast.models import User

logger = logging.getLogger(__name__)


@identify(StockastAuthentication, methods=['GET'])
class UserCollectionResource(CollectionResource):
    """ Makse CRUD-like resource for user collections"""
    model = User
    methods = ['GET', 'POST']
    default_sort = ['email']
    response_fields = ['id', 'name', 'email']

    def before_post(self, req, resp, db_session, resource, *args, **kwargs):
        """ convert email to lowercase"""
        logger.info(f'Resource: {resource}')
        resource.email = resource.email.lower()


@authorize(StockastUserUpdateAuthorization, methods=['PUT', 'PATCH', 'DELETE'])
@identify(StockastAuthentication)
class UserResource(SingleResource):
    """ Makse CRUD-like resource for single users"""
    model = User
    response_fields = ['id', 'name', 'email']


@authorize(StockastFollowUpdateAuthorization, methods=['POST'])
@identify(StockastAuthentication)
class UserFollowsCollectionResource(CollectionResource):
    """ Makse CRUD-like resource for list of follows a single user has collections"""
    model = Follows
    methods = ['GET', 'POST']
    default_sort = ['symbol']
    lookup_attr_map = {
        'id': 'user_id'
    }
    inbound_attr_map = {
        'id': 'user_id'
    }


@authorize(StockastFollowUpdateAuthorization, methods=['DELETE'])
@identify(StockastAuthentication)
class UserFollowsResource(SingleResource):
    """ Makse CRUD-like resource for follow entity users"""
    model = Follows
    methods = ['GET', 'DELETE']
    lookup_attr_map = {
        'id': 'user_id'
    }
    inbound_attr_map = {
        'id': 'user_id'
    }
