import logging

from base64 import b64decode
from falcon import HTTPUnauthorized, HTTPForbidden
from six.moves.urllib.parse import unquote
from sqlalchemy.orm import sessionmaker

from stockast.models import User

logger = logging.getLogger(__name__)


class DecodeError(Exception):
    pass


class StockastAuthentication(object):
    """ Handles user login and loading the user to the request context"""

    def identify(self, req, resp, resource, params):
        # check auth header
        auth_header = req.get_header('Authorization')
        if not auth_header:
            raise HTTPUnauthorized('Authentication Required', 'Missing Authorization header')

        # get username and password from auth header
        try:
            username, password = self.decode(auth_header)
        except DecodeError:
            raise HTTPUnauthorized('Authentication Required', 'No credentials supplied')

        # get user from DB
        user = self.user_loader(resource.db_engine, username.lower(), password)

        # if we found a user and the password matches, return user as dict
        if user and user.password == password:
            req.context['user'] = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            }
        else:
            # for every other scenario, raise a 401 error
            raise HTTPUnauthorized(description='invalid user or password.')

    def user_loader(self, engine, username, password):
        """ Load a user from the database and compare its password"""

        # create a new session
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()

        try:
            # get user from DB
            return session.query(User).filter_by(email=username).first()
        finally:
            # attempt to close db connection even if there are errors
            session.close()

    def decode(self, encoded_str):
        """ Decodes an encrypted HTTP basic authentication string.
        Returns:
            username, password: tuple

        Raises:
            a DecodeError exception if nothing could be decoded.
        """
        split = encoded_str.strip().split(' ')

        # If there are only two elements, check the first and ensure it says 'basic'
        # so that we know we're about to decode the right thing. If not, bail out.
        if len(split) == 2:
            if split[0].strip().lower() == 'basic':
                try:
                    username, password = b64decode(split[1]).decode().split(':', 1)
                except Exception:
                    raise DecodeError
            else:
                raise DecodeError
        # If there are more than 2 elements, we don't know what the header is...
        else:
            raise DecodeError

        return unquote(username), unquote(password)


class StockastUserUpdateAuthorization(object):
    """ Handles checks of user information updates"""

    def authorize(self, req, resp, resource, params):
        # get the ID of the user
        user_id = params.get('id')

        # if the user does not exist in context, no access
        if 'user' not in req.context:
            raise HTTPForbidden('Permission Denied', 'User does not have access to this resource')

        # if the user tries to access a user resource who's ID is not the same as it, break access
        if str(req.context['user']['id']) != str(user_id):
            raise HTTPForbidden('Permission Denied', 'User does not have access to this resource')


class StockastFollowUpdateAuthorization(object):
    """ Handles checks of user information updates"""

    def authorize(self, req, resp, resource, params):
        # get the ID of the user
        user_id = params.get("id")

        logger.info(f'Follow - user_id: {user_id}')

        # if the user does not exist in context, no access
        if 'user' not in req.context:
            logger.warn(f'User not loaded in context.')
            raise HTTPForbidden('Permission Denied', 'User does not have access to this resource')

        # if the user tries to access a user resource who's ID is not the same as it, break access
        if str(req.context['user']['id']) != str(user_id):
            logger.warn(f'Context user id is not the same as requested user id')
            raise HTTPForbidden('Permission Denied', 'User does not have access to this resource')
