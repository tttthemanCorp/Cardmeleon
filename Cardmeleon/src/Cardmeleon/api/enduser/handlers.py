'''
Created on Aug 10, 2011

@author: jlu
'''

from piston.handler import BaseHandler
from piston.utils import rc, throttle

from django.contrib.auth.models import User


class UserHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = User

    def read(self, request, user_name=None):
        """
        Returns a single user if `user_name` is given,
        otherwise a list of all users.
        """
        base = User.objects

        if user_name:
            return base.get(username=user_name)
        else:
            return base.all() # Or base.filter(...)
   
    @throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, user_name):
        return rc.CREATED
   
    @throttle(10, 60) # allow 5 times in 1 minute
    def update(self, request, user_name):
        return rc.ALL_OK

    def delete(self, request, user_name):
        return rc.DELETED # returns HTTP 204

