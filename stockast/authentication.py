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

    def __call__(self, req, resp, resource, params):
        self.identify(req, resp, resource, params)

    def identify(self, req, resp, resource, params):
        # check auth header
        auth_header = req.get_header('Authorization')
        if not auth_header:
            raise HTTPUnauthorized('Authentication Required', 'Missing Authorization header')

        # get username and password from auth header
        try:
            username, password = self.decode(auth_header)
            logger.debug(f'Trying to authenticate: {username}.')
        except DecodeError:
            raise HTTPUnauthorized('Authentication Required', 'No credentials supplied')

        # get user from DB
        user = self.user_loader(resource.db_engine, username.lower(), password)
        logger.debug(f'User query returned: {user}.')

        # if we found a user and the password matches, return user as dict
        if user and user.password == password:
            logger.debug(f'Authentication successful for: {username}.')
            req.context['user'] = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            }
        else:
            logger.debug(f'Authentication failure for: {username}.')
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
        logger.debug(f'Trying to authorize user with id: {user_id}.')

        # if the user does not exist in context, no access
        if 'user' not in req.context:
            logger.debug(f'User not set in context, permission denied.')
            raise HTTPForbidden('Permission Denied', 'User does not have access to this resource')

        # if the user tries to access a user resource who's ID is not the same as it, break access
        context_user_id = req.context["user"]["id"]
        if str(context_user_id) != str(user_id):
            logger.debug(
                f'User id: {str(user_id)} does not match '
                f'the context user: {str(context_user_id)}')
            raise HTTPForbidden('Permission Denied', 'User does not have access to this resource')
