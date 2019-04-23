import logging

logger = logging.getLogger(__name__)


class SQLAlchemySessionManager:
    """Create a scoped session for every request and close it when the request ends.
    """

    def __init__(self, session):
        self.session = session

    def process_resource(self, req, resp, resource, params):
        resource.session = self.session()

    def process_response(self, req, resp, resource, req_succeeded):
        if hasattr(resource, 'session'):
            if not req_succeeded:
                resource.session.rollback()
            self.session.remove()
