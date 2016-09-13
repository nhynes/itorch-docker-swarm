import os

from jupyterhub.auth import LocalAuthenticator
import tornado.gen as gen

class SesameAuthenticator(LocalAuthenticator):
    @gen.coroutine
    def authenticate(self, handler, data):
        if data['password'] == os.environ['OPEN_SESAME']:
            return data['username']
