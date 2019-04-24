import falcon
import logging

logger = logging.getLogger(__name__)


class StatusResource:
    def on_get(self, req, resp):
        req.status = falcon.HTTP_OK
        resp.media = {'status': 'ok'}
