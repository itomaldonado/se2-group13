from falcon import HTTPUnauthorized, HTTPForbidden
from falcon_auth import BasicAuthBackend
from sqlalchemy.orm import sessionmaker

from stockast.models import User


class StocastAuthentication(object):
    def identify(self, req, resp, resource, params):
        # check auth header
        auth_header = req.get_header('Authorization')
        if not auth_header:
            raise HTTPUnauthorized('Authentication Required', 'Missing Authorization header')

        # create a new session
        Session = sessionmaker()
        Session.configure(bind=resource.db_engine)
        session = Session()

        # get user from DB
        user = session.query(User).filter_by(email=username).first()

        # if we found a user and the password matches, return user as dict
        if user and user.password == password:
            return {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            }

            # for every other scenario, raise a 401 error
            raise HTTPUnauthorized(description='invalid user or password.')

        # req.context['user']

    def authorize(self, req, resp, resource, params):
        if 'user' not in req.context or req.context['user'] != 'Jim':
            raise HTTPForbidden('Permission Denied', 'User does not have access to this resource')


class StocastAuthentication(BasicAuthBackend):

    def __init__(self, engine):
        self.engine = engine
        super().__init__(self.user_loader)


    def user_loader(self, username, password):
        """ Load a user from the database and compare its password"""

        # create a new session
        Session = sessionmaker()
        Session.configure(bind=self.engine)
        session = Session()

        try:
            # get user from DB
            user = session.query(User).filter_by(email=username).first()

            # if we found a user and the password matches, return user as dict
            if user and user.password == password:
                return {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                }

            # for every other scenario, raise a 401 error
            raise HTTPUnauthorized(description='invalid user or password.')
        finally:
            # attempt to close db connection even if there are errors
            session.close()
