'''
Created on Aug 10, 2011

@author: jlu
'''

from django.conf.urls.defaults import *
from piston.resource import Resource
from Cardmeleon.api.enduser.handlers import UserHandler, UserPrefHandler

user_handler = Resource(UserHandler)
userpref_handler = Resource(UserPrefHandler)

urlpatterns = patterns('',
   
   url(r'^users/(?P<user_id>\w+)/pref$', userpref_handler, {'emitter_format':'json'}),
   url(r'^users/(?P<user_id>\w+)', user_handler, {'emitter_format':'json'}),
   url(r'^users/', user_handler, {'emitter_format':'json'}),
)