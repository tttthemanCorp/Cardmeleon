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
#authChain = { 'authentication': None }

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
   # Get: get all rewards or all forsell rewards for all users ;
   url(r'^users/reward(/(?P<sell_only>forsell))?$', userreward_handler, {'emitter_format':'json'}),
   # Get: get all rewards belong to 1 user ;  
   # Post: issue a reward to 1 user for enough purchases ;  
   # Put: change 1 user's reward values, such as mark it forsale, or change the expiration date ;  
   # Delete: delete all rewards belong to 1 user ;
   url(r'^users/(?P<user_id>\d+)/reward$', userreward_handler, {'emitter_format':'json'}),
   # Get: get all reward-redemption activities by 1 user ;  
   # Post:  redeem a reward by 1 user ;  
   # Delete: delete all reward-redemption activities by 1 user ;
   url(r'^users/(?P<user_id>\d+)/redeem$', redeem_activity_handler, {'emitter_format':'json'}),
   # Get: get all reward-buying activities by 1 user ;  
   # Post:  buy a reward by 1 user ;  
   # Delete: delete all reward-buying activities by 1 user ;
   url(r'^users/(?P<user_id>\d+)/buy$', trade_activity_handler, {'emitter_format':'json'}),
   # Get: get all reward-giving (gifting out) activities by 1 user ;  
   # Post: gift out a reward by 1 user  ;   
   # Delete: delete all reward-giving (gifting out) activities by 1 user ;
   url(r'^users/(?P<user_id>\d+)/gift$', gift_activity_handler, {'emitter_format':'json'}),
   # Get: get all purchasing activities by 1 user ;  
   # Post:  record a purchase by 1 user ;  
   # Delete: delete all purchasing activities by 1 user ;
   url(r'^users/(?P<user_id>\d+)/purchase$', purchase_activity_handler, {'emitter_format':'json'}),
   # Get: get all referring activities by 1 user ;  
   # Post:  refer a friend by 1 user ;  
   # Delete: delete all referring activities by 1 user ;
   url(r'^users/(?P<user_id>\d+)/refer$', refer_activity_handler, {'emitter_format':'json'}),
   # Get: get 1 user's pref ;  
   # Post:  create a new user pref ;  
   # Put: update values in 1 user's pref ;  
   # Delete: delete all pres belong to 1 user ;
   url(r'^users/(?P<user_id>\d+)/pref$', userpref_handler, {'emitter_format':'json'}),
   # Get: get full user info of 1 user ;  
   # Put: update info of 1 user ;  
   # Delete: delete 1 user ;
   url(r'^users/(?P<user_id>\d+)', user_handler, {'emitter_format':'json'}),
   # Get: get total number of users ;  
   # Post: sign up a new user  ;  
   url(r'^users$', user_handler, {'emitter_format':'json'}),
   # Get: authenticate 1 user based on credentials, and return user id ;  
   url(r'^auth$', login_handler, {'emitter_format':'json'}),
   # Get: get all reward offerings of 1 merchant, or, get 1 reward offering of 1 merchant ;  
   # Post:  create a new reward offering by 1 merchant ;  
   # Put: update info on 1 reward offering of 1 merchant ;  
   # Delete: delete all reward offerings of 1 merchant, or, delete 1 reward offering of 1 merchant ; 
   url(r'^stores/(?P<merchant_id>\d+)/reward(/(?P<reward_id>\d+))?$', reward_handler, {'emitter_format':'json'}),
   # Get: get all reward programs of 1 merchant, or, get 1 reward program of 1 merchant ; ;  
   # Post:  create a new reward program by 1 merchant ;  
   # Put: update info on 1 reward program of 1 merchant ;  
   # Delete: delete all reward programs of 1 merchant, or, delete 1 reward program of 1 merchant ; 
   url(r'^stores/(?P<merchant_id>\d+)/program(/(?P<program_id>\d+))?$', program_handler, {'emitter_format':'json'}),
   # Get: get 1 merchant ;  
   # Put: update info of 1 merchant ;  
   # Delete: delete 1 merchant ;
   url(r'^stores/(?P<merchant_id>\d+)$', merchant_handler, {'emitter_format':'json'}),
   # Post: create a new merchant ;
   url(r'^stores$', merchant_handler, {'emitter_format':'json'}),
   # Get: get all nearby merchants ;
   url(r'^stores/prox/((?P<longitude>\d*\.?\d+),(?P<latitude>\d*\.?\d+),(?P<distance>\d+))?$', merchant_handler, {'emitter_format':'json'}),
)