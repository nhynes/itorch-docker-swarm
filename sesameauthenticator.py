import os

from jupyterhub.auth import LocalAuthenticator

class SesameAuthenticator(LocalAuthenticator):
    @gen.coroutine
    def authenticate(self, handler, data):
        if data['password'] == os.environ['OPEN_SESAME']:
            return data['username']
