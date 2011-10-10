'''
Created on Aug 10, 2011

@author: jlu
'''

from django.conf.urls.defaults import patterns, url
from piston.resource import Resource
from Cardmeleon.api.handlers import UserHandler, UserPrefHandler, ReferralActivityHandler, UserRewardHandler, TradeActivityHandler, RewardHandler
from Cardmeleon.api.handlers import PurchaseActivityHandler, RedeemActivityHandler, MerchantHandler, GiftActivityHandler, RewardProgramHandler, LoginHandler
from piston.authentication import HttpBasicAuthentication, NoAuthentication


basicAuth = HttpBasicAuthentication(realm="Secure Realm")
authChain = { 'authentication': basicAuth }
#authChain = None

user_handler = Resource(UserHandler, **authChain)
login_handler = Resource(LoginHandler, **authChain)
userpref_handler = Resource(UserPrefHandler, **authChain)
userreward_handler = Resource(UserRewardHandler, **authChain)
refer_activity_handler = Resource(ReferralActivityHandler, **authChain)
purchase_activity_handler = Resource(PurchaseActivityHandler, **authChain)
redeem_activity_handler = Resource(RedeemActivityHandler, **authChain)
trade_activity_handler = Resource(TradeActivityHandler, **authChain)
gift_activity_handler = Resource(GiftActivityHandler, **authChain)
merchant_handler = Resource(MerchantHandler, **authChain)
program_handler = Resource(RewardProgramHandler, **authChain)
reward_handler = Resource(RewardHandler, **authChain)

urlpatterns = patterns('',
   url(r'^users/reward(/(?P<sell_only>forsell))?$', userreward_handler, {'emitter_format':'json'}),
   url(r'^users/(?P<user_id>\d+)/reward$', userreward_handler, {'emitter_format':'json'}),
   url(r'^users/(?P<user_id>\d+)/redeem$', redeem_activity_handler, {'emitter_format':'json'}),
   url(r'^users/(?P<user_id>\d+)/buy$', trade_activity_handler, {'emitter_format':'json'}),
   url(r'^users/(?P<user_id>\d+)/gift$', gift_activity_handler, {'emitter_format':'json'}),
   url(r'^users/(?P<user_id>\d+)/purchase$', purchase_activity_handler, {'emitter_format':'json'}),
   url(r'^users/(?P<user_id>\d+)/refer$', refer_activity_handler, {'emitter_format':'json'}),
   url(r'^users/(?P<user_id>\d+)/pref$', userpref_handler, {'emitter_format':'json'}),
   url(r'^users/(?P<user_id>\d+)', user_handler, {'emitter_format':'json'}),
   url(r'^users$', user_handler, {'emitter_format':'json'}),
   url(r'^auth$', login_handler, {'emitter_format':'json'}),
   url(r'^stores/(?P<merchant_id>\d+)/reward(/(?P<reward_id>\d+))?$', reward_handler, {'emitter_format':'json'}),
   url(r'^stores/(?P<merchant_id>\d+)/program(/(?P<program_id>\d+))?$', program_handler, {'emitter_format':'json'}),
   url(r'^stores/(?P<merchant_id>\d+)$', merchant_handler, {'emitter_format':'json'}),
   url(r'^stores$', merchant_handler, {'emitter_format':'json'}),
   url(r'^stores/prox/((?P<longitude>\d*\.?\d+),(?P<latitude>\d*\.?\d+),(?P<distance>\d+))?$', merchant_handler, {'emitter_format':'json'}),  # GET only
)