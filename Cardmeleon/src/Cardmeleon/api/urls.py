'''
Created on Aug 10, 2011

@author: jlu
'''

from django.conf.urls.defaults import *
from piston.resource import Resource
from Cardmeleon.api.handlers import UserHandler

user_handler = Resource(UserHandler)

urlpatterns = patterns('',
   url(r'^users/(?P<user_name>\w+)\.(?P<emitter_format>.+)', user_handler),
   url(r'^users/', user_handler),
)