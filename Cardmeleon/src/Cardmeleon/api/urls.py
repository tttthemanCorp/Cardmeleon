'''
Created on Aug 10, 2011

@author: jlu
'''

from django.conf.urls.defaults import patterns, url
from piston.resource import Resource
from Cardmeleon.api.handlers import UserHandler, UserPrefHandler, ReferralActivityHandler, UserRewardHandler, TradeActivityHandler, RewardHandler
from Cardmeleon.api.handlers import PurchaseActivityHandler, RedeemActivityHandler, MerchantHandler, GiftActivityHandler, RewardProgramHandler

user_handler = Resource(UserHandler)
userpref_handler = Resource(UserPrefHandler)
userreward_handler = Resource(UserRewardHandler)
refer_activity_handler = Resource(ReferralActivityHandler)
purchase_activity_handler = Resource(PurchaseActivityHandler)
redeem_activity_handler = Resource(RedeemActivityHandler)
trade_activity_handler = Resource(TradeActivityHandler)
gift_activity_handler = Resource(GiftActivityHandler)
merchant_handler = Resource(MerchantHandler)
program_handler = Resource(RewardProgramHandler)
reward_handler = Resource(RewardHandler)

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
   url(r'^stores/(?P<merchant_id>\d+)/reward(/(?P<reward_id>\d+))?$', reward_handler, {'emitter_format':'json'}),
   url(r'^stores/(?P<merchant_id>\d+)/program(/(?P<program_id>\d+))?$', program_handler, {'emitter_format':'json'}),
   url(r'^stores/(?P<merchant_id>\d+)$', merchant_handler, {'emitter_format':'json'}),
   url(r'^stores$', merchant_handler, {'emitter_format':'json'}),
   url(r'^stores/prox/((?P<longitude>\d*\.?\d+),(?P<latitude>\d*\.?\d+),(?P<distance>\d+))?$', merchant_handler, {'emitter_format':'json'}),  # GET only
)