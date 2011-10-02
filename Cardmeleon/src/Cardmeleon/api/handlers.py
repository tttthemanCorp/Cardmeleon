'''
Created on Aug 10, 2011

@author: jlu
'''

from piston.handler import BaseHandler
from piston.utils import rc, throttle
from datetime import datetime
from decimal import Decimal
from django.db.models import Q
from datetime import date

from Cardmeleon.server.models import User, UserPoint, UserReward, UserPref, ReferralActivity, PurchaseActivity, RewardActivity, Merchant, Reward, RewardProgram, UserProgress
from Cardmeleon.settings import REFERRAL_BONUS


class SharedHandler(BaseHandler):
    """
    common base handler for all cardmeleon rest handlers
    """
    
    def userExists(self, data):
        try:
            if data.get('username'):
                a = Q(username__iexact=data.get('username'))
            else:
                a = Q(username__isnull=True)
            if data.get('facebook'):
                b = Q(facebook__iexact=data.get('facebook'))
            else:
                b = Q(facebook__isnull=True)
            User.objects.get(a & b)
            return True
        except User.MultipleObjectsReturned:
            return True
        except User.DoesNotExist:
            return False
    
    def userById(self, userId):
        try:
            user = User.objects.get(id=userId)
            return user
        except User.DoesNotExist:
            return None
        
    def userByLogin(self, login):
        try:
            user = User.objects.get(Q(username__iexact=login) | Q(facebook__iexact=login))
            return user
        except User.DoesNotExist:
            return None
        
    def merchantById(self, merchantId):
        try:
            merchant = Merchant.objects.get(id=merchantId)
            return merchant
        except Merchant.DoesNotExist:
            return None
        
    def merchantByName(self, name):
        try:
            merchant = Merchant.objects.get(name__iexact=name)
            return merchant
        except Merchant.DoesNotExist:
            return None

    def rewardById(self, rewardId):
        try:
            reward = Reward.objects.get(id=rewardId)
            return reward
        except Reward.DoesNotExist:
            return None
        
    def rewardProgramById(self, rewardProgramId):
        try:
            rewardProg = RewardProgram.objects.get(id=rewardProgramId)
            return rewardProg
        except RewardProgram.DoesNotExist:
            return None
        
    def idsValidation(self, user_id, reward_id, merchant_id):
        user = None
        if user_id is not None:
            user = self.userById(user_id)
            if user is None:
                raise LookupError, 'No User with this id exists: '+user_id
                
        reward = None  
        if reward_id is not None:
            reward = self.rewardById(reward_id)
            if reward is None:
                raise LookupError, 'No Reward with this id exists: '+reward_id
        
        merchant = None
        if merchant_id is not None:
            merchant = self.merchantById(merchant_id)
            if merchant is None:
                raise LookupError, 'No Merchant with this id exists: '+merchant_id
            
        return (user, reward, merchant)


class UserHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = User
    fields = ('username','facebook','email','phone',('referer',('id',)))

    def read(self, request, user_id=None):
        """
        Returns a single user if `user_id` is given,
        otherwise a list of all users.
        """
        base = User.objects

        if user_id:
            user = base.get(id=user_id)
            
            try:
                userpoint = UserPoint.objects.get(user__id=user_id)
            except UserPoint.DoesNotExist:
                userpoint = None
            try:
                userprogress = UserProgress.objects.get(user__id=user_id)
            except UserProgress.DoesNotExist:
                userprogress = None
            userrewards = UserReward.objects.filter(user__id=user_id)
            self.fields = None
            return {"user":user, "userprogress":userprogress, "userpoint":userpoint, "userrewards":userrewards}
        else:
            return base.all() # Or base.filter(...)
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request):
        """
        Creates a new user.
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        if self.userExists(attrs):
            return rc.DUPLICATE_ENTRY
        
        #insert new user
        user = User()
        user.updateValues(**attrs)
        user.save()
        
        #update referral activity table
        refererDict = attrs.get('referer')
        if refererDict:
            refererName = refererDict.get('username')
            if not refererName:
                refererName = refererDict.get('facebook')
            if refererName:
                referer = self.userByLogin(refererName)
                if referer:
                    refereeName = user.username
                    if not refereeName:
                        refereeName = user.facebook
                    try:
                        #TODO - the following query may fail to get the referral activity record.  revisit it later for a better way
                        referActivity = ReferralActivity.objects.filter(referer__id=referer.id, referee_name__iexact=refereeName).latest('time')
                        referActivity.referee = user
                        referActivity.referee_join_time = datetime.now()
                        referActivity.save()
                    except ReferralActivity.DoesNotExist:
                        pass
                    #update UserPoint for referral bonus
                    userPoint = UserPoint.objects.get(user__id=referer.id)
                    userPoint.points += REFERRAL_BONUS
        
        return rc.CREATED
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def update(self, request, user_id):
        """
        Update a user's information
        """
        user = User.objects.get(id=user_id)

        attrs = self.flatten_dict(request.data)
        #print attrs
        
        #does not allow change of username/facebook/referer fields
        if "username" in attrs:
            del attrs["username"]
        if "facebook" in attrs:
            del attrs["facebook"]
        if "referer" in attrs:
            del attrs["referer"]
            
        user.updateValues(**attrs)
            
        user.save()

        return rc.ALL_OK

    def delete(self, request, user_id):
        """
        Delete a user
        """
        user = User.objects.get(id=user_id)

        user.delete()

        return rc.DELETED # returns HTTP 204

# UserPrefHandler
class UserPrefHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = UserPref
    fields = ('nearby_radius', )  #('nearby_radius', ('user',('username', 'facebook')))

    def insertOrUpdate(self, userId, radius):
        """
        Insert if userpref not exists before; otherwise update it
        """
        try:
            pref = UserPref.objects.get(user__id=userId)
            #update
            pref.nearby_radius = radius
            pref.save()
        except UserPref.DoesNotExist:
            user = self.userById(userId)
            if user is None:
                raise LookupError, 'No User with this user_id exists: '+userId
            else:
                #insert
                pref = UserPref()
                pref.nearby_radius = radius
                pref.user = user
                pref.save()
        except UserPref.MultipleObjectsReturned:
            raise LookupError, 'More than 1 UserPref records exist in DB for user_id='+userId

    def read(self, request, user_id):
        """
        Returns a single userPref
        """
        return UserPref.objects.get(user__id=user_id)
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, user_id):
        """
        Creates a new userPref.
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        self.insertOrUpdate(user_id, attrs['nearby_radius'])
        
        return rc.CREATED
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def update(self, request, user_id):
        """
        Update a userPref's values
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        self.insertOrUpdate(user_id, attrs['nearby_radius'])

        return rc.ALL_OK

    #@throttle(10, 60) # allow 5 times in 1 minute
    def delete(self, request, user_id):
        """
        Delete a userpref
        """
        try:
            pref = UserPref.objects.get(user__id=user_id)
            pref.delete()
            return rc.DELETED # returns HTTP 204
        except UserPref.DoesNotExist:
            return rc.DELETED
        except UserPref.MultipleObjectsReturned:
            raise LookupError, 'More than 1 UserPref records exist in DB for user_id='+user_id
        

#UserRewardHandler
class UserRewardHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = UserReward
    fields = (('user', ('id','username','facebook')), 'reward', 'expiration', 'forsale')

    def existsAndActive(self, user, reward):
        exists, userreward = self.exists(user, reward)
        if exists:
            today = date.today()
            if userreward.expiration >= today:
                return (True, userreward)
 
        return (False, None)

    def exists(self, user, reward):
        try:
            userreward = UserReward.objects.get(user__id=user.id, reward__id=reward.id)
            return (True, userreward)
        except UserReward.DoesNotExist:
            return (False, None)

    def read(self, request, user_id=None, sell_only='forsell'):
        """
        If user_id is available, then returns all rewards belong to this user_id;
        If user_id is None, then returns all rewards (if sell_only is Flase) or all for-sell rewards (if sell_only is True) in the market (non-expired)
        """
        base = UserReward.objects

        if user_id:
            return base.filter(user__id=user_id)
        else:
            today = date.today()
            if (sell_only == 'forsell'):
                return base.filter(expiration__gte=today, forsale=True)
            else:
                return base.filter(expiration__gte=today)
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, user_id):
        """
        When the points become eligible, user requests a reward
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        user, _, merchant = self.idsValidation(user_id, None, attrs['merchant_id'])
        rewardProgram = self.rewardProgramById(attrs['rewardprogram_id'])
        try:
            userProgress = UserProgress.objects.get(user__id=user_id, merchant__id=merchant.id)
        except UserProgress.DoesNotExist:
            return ("user is not eligible for reward", 500)
        
        #eligibility validation & honor request
        if rewardProgram.prog_type == 0:  #dollar amount
            if userProgress.cur_dollar_amt < rewardProgram.reward_trigger:
                return ("user hasn't made enough purchases to be eligible for a reward", 500)
            else:
                userProgress.cur_dollar_amt -= rewardProgram.reward_trigger
        else:  #purchase times
            if userProgress.cur_times < rewardProgram.reward_trigger:
                return ("user hasn't made enough purchases to be eligible for a reward", 500)
            else:
                userProgress.cur_times -= rewardProgram.reward_trigger
        
        #issue reward to user
        reward = rewardProgram.reward
        today = date.today()
        expiration = today.replace(year=today.year+reward.expire_in_years, month=today.month+reward.expire_in_months, day=today.day+reward.expire_in_days)
        userreward = UserReward()
        userreward.user = user
        userreward.reward = reward
        userreward.expiration = expiration
        userreward.forsale = False
        
        #commit to DB
        userProgress.save()
        userreward.save()
            
        return rc.CREATED
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def update(self, request, user_id):
        """
        Update a userreward's values: mark it as "for sale", or change the expiration date
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        rewardId = attrs['reward']['id']
        user, reward, _ = self.idsValidation(user_id, rewardId, None)
        
        exists, userreward = self.exists(user, reward)
        if not exists:
            return rc.NOT_FOUND
        
        if 'expiration' in attrs:
            userreward.expiration = attrs['expiration']
        if 'forsale' in attrs:
            userreward.forsale = attrs['forsale']

        userreward.save()

        return rc.ALL_OK

    #@throttle(10, 60) # allow 5 times in 1 minute
    def delete(self, request, user_id):
        """
        Delete all rewards belong to a user_id
        """
        userrewards = UserReward.objects.filter(user__id=user_id)
        if not userrewards:
            return rc.NOT_FOUND
        
        userrewards.delete()
        return rc.DELETED # returns HTTP 204

        
# ReferralActivityHandler
class ReferralActivityHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')
    model = ReferralActivity
    fields = ('time', 'referee_name', 'refer_method', 'referee_join_time')

    def read(self, request, user_id):
        """
        Returns all referral activities by this user
        """
        return ReferralActivity.objects.filter(referer__id=user_id)
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, user_id):
        """
        Creates a new referralActivity.
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        user, _, _ = self.idsValidation(user_id, None, None)
        
        #insert referral activity
        refer = ReferralActivity()
        refer.time = datetime.now()
        refer.referee_name = attrs['referee_name']
        refer.refer_method = attrs['refer_method']
        refer.referer = user
        refer.save()
        
        return rc.CREATED

    #@throttle(10, 60) # allow 5 times in 1 minute
    def delete(self, request, user_id):
        """
        Delete all referral activities by this user
        """
        try:
            refers = ReferralActivity.objects.filter(referer__id=user_id)
            refers.delete()
            return rc.DELETED # returns HTTP 204
        except RuntimeError:  #TODO error variable and message
            raise LookupError


# PurchaseActivityHandler
class PurchaseActivityHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')
    model = PurchaseActivity
    fields = ('time', ('merchant', ('name',)), 'dollar_amount', 'description')

    def read(self, request, user_id):
        """
        Returns all purchase activities by this user
        """
        return PurchaseActivity.objects.filter(user__id=user_id)
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, user_id):
        """
        Makes a purchase
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        if attrs.get('merchant'):
            mid = attrs.get('merchant').get('id')
        else:
            mid = None
        user, _, merchant = self.idsValidation(user_id, None, mid)
        
        #insert purchase activity
        purchase = PurchaseActivity()
        purchase.time = datetime.now()
        purchase.merchant = merchant
        purchase.dollar_amount = Decimal("%.2f" % attrs['dollar_amount'])
        purchase.description = attrs['description']
        purchase.user = user
        purchase.save()
        
        #update UserProgress
        try:
            userProgress = UserProgress.objects.get(user__id=user_id, merchant__id=merchant.id)
            userProgress.cur_dollar_amt += purchase.dollar_amount
            userProgress.cur_times += 1
        except UserProgress.DoesNotExist:
            userProgress = UserProgress()
            userProgress.user = user
            userProgress.merchant = merchant
            userProgress.cur_dollar_amt = purchase.dollar_amount
            userProgress.cur_times = 1

        userProgress.save()

        return rc.CREATED

    #@throttle(10, 60) # allow 5 times in 1 minute
    def delete(self, request, user_id):
        """
        Delete all purchase activities by this user
        """
        try:
            purchases = PurchaseActivity.objects.filter(user__id=user_id)
            purchases.delete()
            return rc.DELETED # returns HTTP 204
        except RuntimeError:  #TODO error variable and message
            raise LookupError


#RedeemActivityHandler
class RedeemActivityHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')
    model = RewardActivity

    def read(self, request, user_id):
        """
        Returns redeem-reward activities initiated by this user
        """
        return RewardActivity.objects.filter(from_user__id__exact=user_id, activity_type__exact=1)
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, user_id):
        """
        Redeem a reward
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        user, reward, _ = self.idsValidation(user_id, attrs['reward']['id'], None)
        
        urHandler = UserRewardHandler()
        exists, userreward = urHandler.existsAndActive(user, reward)
        if not exists:
            raise ValueError, "reward doesn't belong to user, or reward is invalid/expired"
            
        #insert reward activity
        rewardActivity = RewardActivity()
        rewardActivity.time = datetime.now()
        rewardActivity.reward = reward
        rewardActivity.activity_type = 1
        rewardActivity.description = attrs.get('description')
        rewardActivity.points_value = reward.equiv_points
        rewardActivity.from_user = user
        rewardActivity.to_user = None
            
        #commit to DB
        rewardActivity.save()
        userreward.delete()

        return rc.CREATED

    #@throttle(10, 60) # allow 5 times in 1 minute
    def delete(self, request, user_id):
        """
        Delete redeem-reward activities initiated by this user
        """
        try:
            rewardActivities = RewardActivity.objects.filter(from_user__id__exact=user_id, activity_type__exact=1)
            rewardActivities.delete()
            return rc.DELETED # returns HTTP 204
        except RuntimeError:  #TODO error variable and message
            raise LookupError


#TradeActivityHandler
class TradeActivityHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')
    model = RewardActivity

    def read(self, request, user_id):
        """
        Returns trade-reward activities initiated by this user: buying activities by this user
        """
        return RewardActivity.objects.filter(to_user__id__exact=user_id, activity_type__exact=2)
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, user_id):
        """
        Buy a reward
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        user, reward, _ = self.idsValidation(user_id, attrs['reward']['id'], None)
        
        sellerId = attrs['from_user']['id']
        seller = self.userById(sellerId)
        if seller is None:
            raise LookupError, 'No Seller with this id exists: '+sellerId
        
        urHandler = UserRewardHandler()
        exists, userreward = urHandler.existsAndActive(seller, reward)
        if not exists:
            raise ValueError, "reward doesn't belong to user, or reward is invalid/expired"
        
        try:
            buyerPoint = UserPoint.objects.get(user__id=user_id)
            if buyerPoint.points < reward.equiv_points:
                return ('Buyer does not have enough points', 500)
        except UserPoint.DoesNotExist:
            return ('Buyer does not have enough points', 500)
            
        #insert reward activity
        rewardActivity = RewardActivity()
        rewardActivity.time = datetime.now()
        rewardActivity.reward = reward
        rewardActivity.activity_type = 2
        rewardActivity.description = attrs.get('description')
        rewardActivity.points_value = reward.equiv_points
        rewardActivity.from_user = seller
        rewardActivity.to_user = user
            
        #update UserReward record
        userreward.user = user
        userreward.forsale = False
        
        #update UserPoint records
        buyerPoint.points -= reward.equiv_points
        try:
            sellerPoint = UserPoint.objects.get(user__id=sellerId)
            sellerPoint.points += reward.equiv_points
        except UserPoint.DoesNotExist:
            sellerPoint = UserPoint()
            sellerPoint.user = seller
            sellerPoint.points = reward.equiv_points
        
        #commit to DB
        rewardActivity.save()
        userreward.save()
        sellerPoint.save()
        buyerPoint.save()

        return rc.CREATED

    #@throttle(10, 60) # allow 5 times in 1 minute
    def delete(self, request, user_id):
        """
        Delete trade-reward activities initiated by this user: buying activities by this user
        """
        try:
            rewardActivities = RewardActivity.objects.filter(to_user__id__exact=user_id, activity_type__exact=2)
            rewardActivities.delete()
            return rc.DELETED # returns HTTP 204
        except RuntimeError:  #TODO error variable and message
            raise LookupError


#GiftActivityHandler
class GiftActivityHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')
    model = RewardActivity

    def read(self, request, user_id):
        """
        Returns gift-reward activities initiated by this user
        """
        return RewardActivity.objects.filter(from_user__id__exact=user_id, activity_type__exact=3)
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, user_id):
        """
        Gift out a reward
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        user, reward, _ = self.idsValidation(user_id, attrs['reward']['id'], None)
        
        user2Id = attrs['to_user']['id']
        user2 = self.userById(user2Id)
        if user2 is None:
            raise LookupError, 'No User with this to_user_id exists: '+user2Id
        
        urHandler = UserRewardHandler()
        exists, userreward = urHandler.existsAndActive(user, reward)
        if not exists:
            raise ValueError, "reward doesn't belong to user, or reward is invalid/expired"
            
        #insert reward activity
        rewardActivity = RewardActivity()
        rewardActivity.time = datetime.now()
        rewardActivity.reward = reward
        rewardActivity.activity_type = 3
        rewardActivity.description = attrs['description']
        rewardActivity.points_value = reward.equiv_points
        rewardActivity.from_user = user
        rewardActivity.to_user = user2
            
        #update UserReward record
        userreward.user = user2
        userreward.forsale = False
        
        #commit to DB
        rewardActivity.save()
        userreward.save()

        return rc.CREATED

    #@throttle(10, 60) # allow 5 times in 1 minute
    def delete(self, request, user_id):
        """
        Delete reward activities initiated by this user and a particular activity_type
        """
        try:
            rewardactivities = RewardActivity.objects.filter(from_user__id__exact=user_id, activity_type__exact=3)
            rewardactivities.delete()
            return rc.DELETED # returns HTTP 204
        except RuntimeError:  #TODO error variable and message
            raise LookupError
        
        
#MerchantHandler
class MerchantHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Merchant

    def read(self, request, merchant_id=None, longitude=None, latitude=None, distance=None):
        """
        Returns a single merchant if `merchant_id` is given,
        otherwise a list of all merchants.
        """
        base = Merchant.objects

        if merchant_id:
            return base.get(id=merchant_id)
        else:
            query = "SELECT (acos(sin(latitude * 0.017453292) * sin(%s * 0.017453292) + cos(latitude * 0.017453292) * cos(%s * 0.017453292) * cos((longitude - %s) * 0.017453292)) * 3958.565474745) AS distance, * FROM server_merchant WHERE distance <= %s ORDER BY distance ASC" % (latitude, latitude, longitude, distance)
            #return base.raw(query, [latitude, latitude, longitude, distance])
            #print query
            r = base.raw(query)
            #for i in r:
            #    print "%s miles for %s." % (i.distance, i.name)
            return r
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request):
        """
        Creates a new merchant.
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        try:
            if self.exists(**attrs):
                return rc.DUPLICATE_ENTRY
            else:
                merchant = Merchant()
                merchant.updateValues(**attrs)
                merchant.save()
                return rc.CREATED
        except Exception as inst:
            print inst
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def update(self, request, merchant_id):
        """
        Update a merchant's information
        """
        merchant = Merchant.objects.get(id=merchant_id)

        attrs = self.flatten_dict(request.data)
        #print attrs
        
        merchant.updateValues(**attrs)
            
        merchant.save()

        return rc.ALL_OK

    def delete(self, request, merchant_id):
        """
        Delete a merchant
        """
        merchant = Merchant.objects.get(id=merchant_id)

        merchant.delete()

        return rc.DELETED # returns HTTP 204


#UserPointHandler
class UserPointHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = UserPoint
    fields = ('points',)
    

#UserProgressHandler
class UserProgressHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = UserProgress
    fields = (('merchant', ('id', 'name')), 'cur_dollar_amt', 'cur_times')
    

#RewardHandler
class RewardHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Reward
    fields = ('id', 'name', 'description', 'equiv_dollar', 'equiv_points', 'expire_in_days', 'expire_in_months', 'expire_in_years', 'status', ('merchant', ('id', 'name')))

    def read(self, request, merchant_id, reward_id=None):
        """
        Returns all Rewards from a merchant_id
        or returns a single Reward from a merchant if reward_id is given
        """
        if reward_id:
            return Reward.objects.get(id=reward_id)
        else:
            return Reward.objects.filter(merchant__id=merchant_id)
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, merchant_id, reward_id=None):
        """
        Creates a new Reward.
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        _, _, merchant = self.idsValidation(None, None, merchant_id)
        
        name = attrs['name']
        try:
            Reward.objects.get(name__iexact=name, merchant__id=merchant.id)
            return rc.DUPLICATE_ENTRY
        except Reward.MultipleObjectsReturned:
            return rc.DUPLICATE_ENTRY
        except Reward.DoesNotExist:
            pass
        
        reward = Reward()
        reward.name = name
        reward.description = attrs['description']
        reward.merchant = merchant
        reward.equiv_dollar = Decimal("%.2f" % attrs['equiv_dollar'])
        reward.equiv_points = int(attrs['equiv_points'])
        reward.expire_in_days = int(attrs['expire_in_days'])
        reward.expire_in_months = int(attrs['expire_in_months'])
        reward.expire_in_years = int(attrs['expire_in_years'])
        reward.status = int(attrs['status'])
        
        reward.save()
        
        return rc.CREATED
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def update(self, request, merchant_id, reward_id):
        """
        Update a Reward's information
        """
        attrs = self.flatten_dict(request.data)
        #print attrs

        try:
            reward = Reward.objects.get(id=reward_id)
            reward.updateValues(**attrs)
            reward.save()
            
            return rc.ALL_OK
        except RewardProgram.DoesNotExist:
            return rc.BAD_REQUEST

    def delete(self, request, merchant_id, reward_id=None):
        """
        Delete all rewards from a merchant_id
        or delete a single reward from a merchant if reward_id is given
        """
        if reward_id:
            reward = Reward.objects.get(id=reward_id)
            reward.delete()
        else:
            rewards = Reward.objects.filter(merchant__id=merchant_id)
            rewards.delete()

        return rc.DELETED # returns HTTP 204    

    
#RewardProgramHandler
class RewardProgramHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = RewardProgram
    fields = ('name', ('merchant', ('name',)), ('reward', ('name', 'equiv_points')), 'prog_type', 'reward_trigger', 'start_time', 'end_time', 'status')
    
    def read(self, request, merchant_id, program_id=None):
        """
        Returns all RewardPrograms from a merchant_id
        or returns a single RewardProgram from a merchant if program_id is given
        """
        if program_id:
            return RewardProgram.objects.get(id=program_id)
        else:
            return RewardProgram.objects.filter(merchant__id=merchant_id)
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, merchant_id, program_id=None):
        """
        Creates a new RewardProgram.
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        if attrs.get('reward'):
            rewardId = attrs['reward'].get('id')
        else:
            rewardId = None
        _, reward, merchant = self.idsValidation(None, rewardId, merchant_id)
        
        name = attrs['name']
        progType = int(attrs['prog_type'])
        try:
            RewardProgram.objects.get(name__iexact=name, merchant__id=merchant.id, prog_type__exact=progType, reward__id=rewardId)
            return rc.DUPLICATE_ENTRY
        except RewardProgram.MultipleObjectsReturned:
            return rc.DUPLICATE_ENTRY
        except RewardProgram.DoesNotExist:
            pass
        
        if attrs.get('start_time'):
            start = datetime.strptime(attrs['start_time'], '%Y-%m-%d')
        else:
            start = None
        if attrs.get('end_time'):
            end = datetime.strptime(attrs['end_time'], '%Y-%m-%d')
        else:
            end = None
        program = RewardProgram()
        program.name = name
        program.merchant = merchant
        program.reward = reward
        program.prog_type = progType
        program.reward_trigger = float(attrs['reward_trigger'])
        program.start_time =start
        program.end_time = end
        program.status = int(attrs['status'])
        
        program.save()
        
        return rc.CREATED
   
    #@throttle(10, 60) # allow 5 times in 1 minute
    def update(self, request, merchant_id, program_id):
        """
        Update a RewardProgram's information
        """
        attrs = self.flatten_dict(request.data)
        #print attrs

        try:
            program = RewardProgram.objects.get(id=program_id)
            if attrs.get('reward'):
                rewardId = attrs['reward'].get('id')
            else:
                rewardId = None
            if rewardId:
                if program.reward.id != int(rewardId):
                    reward = self.rewardById(rewardId)
                    attrs['reward'] = reward
                    
            program.updateValues(**attrs)
            program.save()
            
            return rc.ALL_OK
        except RewardProgram.DoesNotExist:
            return rc.BAD_REQUEST

    def delete(self, request, merchant_id, program_id=None):
        """
        Delete all rewardPrograms from a merchant_id
        or delete a single rewardProgram from a merchant if program_id is given
        """
        if program_id:
            program = RewardProgram.objects.get(id=program_id)
            program.delete()
        else:
            programs = RewardProgram.objects.filter(merchant__id=merchant_id)
            programs.delete()

        return rc.DELETED # returns HTTP 204    
