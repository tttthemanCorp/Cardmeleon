'''
Created on Aug 10, 2011

@author: jlu
'''

from piston.handler import BaseHandler
from piston.utils import rc, throttle

from django.contrib.auth.models import User

class UserHandler(BaseHandler):
   allowed_methods = ('GET',)
   model = User   

   def read(self, request, user_name):
       user = User.objects.get(username=user_name)
       return user
   
   @throttle(5, 10*60) # allow 5 times in 10 minutes
   def create(self, request, user_name):
       return rc.CREATED
   
   @throttle(5, 10*60) # allow 5 times in 10 minutes
   def update(self, request, user_name):
       return rc.ALL_OK

   def delete(self, request, user_name):
       return rc.DELETED # returns HTTP 204
