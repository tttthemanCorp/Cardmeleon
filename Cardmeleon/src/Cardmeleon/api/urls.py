'''
Created on Aug 10, 2011

@author: jlu
'''

from django.conf.urls.defaults import *
from piston.resource import Resource
from Cardmeleon.api.enduser.handlers import UserHandler

user_handler = Resource(UserHandler)

urlpatterns = patterns('',
   url(r'^users/(?P<user_name>\w+)', user_handler, {'emitter_format':'json'}),
   url(r'^users/', user_handler, {'emitter_format':'json'}),
)