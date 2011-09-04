from django.db import models

# Create your models here.
    
class User(models.Model):
    username = models.CharField(max_length=30,null=True)
    facebook_id = models.EmailField(max_length=75,null=True)
    email = models.EmailField(max_length=75,null=True)
    phone = models.CharField(max_length=20,null=True)
    referredby = models.ForeignKey('self',null=True)
    referredby_username = models.CharField(max_length=30,null=True)
    
    def __unicode__(self):
        return "username:{0}, facebook:{1}, email:{2}, phone:{3}, referredBy:{4}".format(
                self.username, self.facebook_id, self.email, self.phone, self.referredby_username)
    
class UserPoint(models.Model):
    user = models.OneToOneField(User)
    points = models.IntegerField()
    
class UserReward(models.Model):
    user = models.ForeignKey(User)
    reward = models.ForeignKey('Reward')
    expiration = models.DateField(null=True)
    
class UserPref(models.Model):
    user = models.OneToOneField(User)
    nearby_radius = models.FloatField()
    
class Merchant(models.Model):
    name = models.CharField(max_length=30)
    #logo = models.ImageField();
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=75,null=True)
    address = models.CharField(max_length=100)
    longitude = models.FloatField();
    latitude = models.FloatField();

class RewardProgram(models.Model):
    merchant = models.ForeignKey(Merchant)
    prog_type = models.SmallIntegerField()  # DollarAmount|PurchaseTimes|Points
    reward_trigger = models.FloatField(null=True)  # accumulated number to trigger rewards
    reward = models.ForeignKey('Reward')
    points_per_activity = models.IntegerField(null=True)  # points earned per purchase activity
    start_time = models.DateField(null=True)  # program start time
    end_time = models.DateField(null=True)  # program end time
    status = models.SmallIntegerField()  # active|inactive|paused
    
class Reward(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100,null=True)
    merchant = models.ForeignKey(Merchant)
    equiv_dollar = models.DecimalField(max_digits=10,decimal_places=2,null=True)
    equiv_points = models.IntegerField(null=True)
    expire_days = models.IntegerField(null=True)
    expire_months = models.IntegerField(null=True)
    expire_years = models.IntegerField(null=True)
    status = models.SmallIntegerField()  # active|cancelled
    
class PurchaseActivity(models.Model):
    user = models.ForeignKey(User)
    time = models.DateTimeField(auto_now_add=True)
    merchant = models.ForeignKey(Merchant)
    dollar_amount = models.DecimalField(max_digits=10,decimal_places=2)
    description = models.CharField(max_length=200,null=True)
    points_earned = models.IntegerField(null=True)

class RewardActivity(models.Model):
    reward = models.ForeignKey(Reward)
    time = models.DateTimeField(auto_now_add=True)
    activity_type = models.SmallIntegerField()  # reward|trade|gift
    from_user = models.ForeignKey(User,related_name='User.initiating_rewardactivity_set',null=True)
    to_user = models.ForeignKey(User,related_name='User.receiving_rewardactivity_set')
    description = models.CharField(max_length=200,null=True)
    points_traded = models.IntegerField(null=True)
    
class ReferralActivity(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    referer = models.ForeignKey(User,related_name='User.referer_activity_set')
    referee = models.ForeignKey(User,related_name='User.referee_activity_set',null=True)
    refer_method = models.SmallIntegerField()  # email|text|phone|web|other
    referee_join_time = models.DateTimeField(null=True)
    
    