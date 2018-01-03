from uvtor.conf import settings
from uvtor.core import handlers
import functools


class BaseHandler(handlers.BaseHandler):

    def check_xsrf_cookie(self):

        return True
