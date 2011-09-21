'''
Created on Aug 10, 2011

@author: jlu
'''

from piston.handler import BaseHandler
from piston.utils import rc, throttle

from Cardmeleon.server.models import User, UserPoint, UserReward, UserPref


class SharedHandler(BaseHandler):
    """
    common base handler for all cardmeleon rest handlers
    """
    
    def userById(self, userId):
        try:
            user = User.objects.get(id=userId)
            return user
        except User.DoesNotExist:
            return None
        
    def userByLogin(self, login, cardmeleon):
        try:
            if cardmeleon:
                user = User.objects.get(username__iexact=login)
            else:
                user = User.objects.get(facebook_id__iexact=login)
            return user
        except User.DoesNotExist:
            return None


class UserHandler(SharedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = User

    def read(self, request, user_name=None):
        """
        Returns a single user if `user_name` is given,
        otherwise a list of all users.
        """
        base = User.objects

        if user_name:
            #u = User.objects.get(username=user_name)
            #p = UserPoint.objects.get(user=u)
            return base.get(username=user_name)
        else:
            return base.all() # Or base.filter(...)
   
    @throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request):
        """
        Creates a new user.
        """
        attrs = self.flatten_dict(request.data)
        #print attrs
        
        try:
            if self.exists(**attrs):
                return rc.DUPLICATE_ENTRY
            else:
                user = User()
                user.updateValues(**attrs)
                user.save()
                return rc.CREATED
        except Exception as inst:
            print inst
   
    @throttle(10, 60) # allow 5 times in 1 minute
    def update(self, request, user_name):
        """
        Update a user's information
        """
        user = User.objects.get(username=user_name)

        attrs = self.flatten_dict(request.data)
        #print attrs
        
        user.updateValues(**attrs)
            
        user.save()

        return rc.ALL_OK

    def delete(self, request, user_name):
        """
        Delete a user
        """
        user = User.objects.get(username=user_name)

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
   
    @throttle(10, 60) # allow 5 times in 1 minute
    def create(self, request, user_id):
        """
        Creates a new userPref.
        """
        attrs = self.flatten_dict(request.data)
        print attrs
        
        self.insertOrUpdate(user_id, attrs['nearby_radius'])
        
        return rc.CREATED
   
    @throttle(10, 60) # allow 5 times in 1 minute
    def update(self, request, user_id):
        """
        Update a userPref's values
        """
        attrs = self.flatten_dict(request.data)
        print attrs
        
        self.insertOrUpdate(user_id, attrs['nearby_radius'])

        return rc.ALL_OK

    @throttle(10, 60) # allow 5 times in 1 minute
    def delete(self, request, user_id):
        """
        Delete a userpref
        """
        try:
            pref = UserPref.objects.get(user__id=user_id)
            pref.delete()
            return rc.DELETED # returns HTTP 204
        except UserPref.DoesNotExist:
            return rc.BAD_REQUEST
        except UserPref.MultipleObjectsReturned:
            raise LookupError, 'More than 1 UserPref records exist in DB for user_id='+user_id
