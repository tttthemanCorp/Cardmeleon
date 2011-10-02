'''
Created on Sep 20, 2011

@author: jlu
'''
from django.test import TestCase
from django.test.client import Client
from django.db import connection
from datetime import datetime, date
import json
from Cardmeleon.api import setup_func
from Cardmeleon.server.models import UserPoint, UserReward


class ServerTest(TestCase):
    fixtures = ['testdata.json',]

    def setUp(self):
        pass
        
    def test_user(self):
        """
        Tests UserHandler
        """
        c = Client()
        
        '''
        [
            {
                "username": "ttttheman", 
                "referer": {
                    "id": 2
                }
                "phone": "4082323232", 
                "facebook": null, 
                "email": "ttttheman@test.com"
            }, 
            {
                "username": "ttttheman2", 
                "phone": "4084545455", 
                "facebook": null, 
                "email": "ttttheman2@test.com"
            }
        ]
        '''
        response = c.get("/api/users")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), 'number of users is not 2')
        self.assertEqual('ttttheman', r[0]['username'], '')
        self.assertEqual(2, r[0]['referer']['id'], '')
        self.assertEqual('ttttheman2', r[1]['username'], '')
        self.assertEqual(None, r[1].get('referer', None), '')
        
        '''
        {
            "userprogress": {
                "merchant": {
                    "name": "Safeway", 
                    "id": 1
                }, 
                "cur_times": 2, 
                "cur_dollar_amt": "50.25"
            }, 
            "userpoint": {
                "points": 200
            },  
            "userrewards": [
                {
                    "reward": {
                        "status": 1, 
                        "merchant": {
                            "name": "Safeway", 
                            "id": 1
                        }, 
                        "equiv_points": 20, 
                        "name": "free bread", 
                        "expire_in_days": 0, 
                        "id": 1, 
                        "expire_in_years": 3, 
                        "equiv_dollar": "20", 
                        "expire_in_months": 0, 
                        "description": "free whole-wheet bread"
                    }, 
                    "expiration": "2012-03-12", 
                    "forsale": false
                }, 
                {
                    "reward": {
                        "status": 1, 
                        "merchant": {
                            "name": "StarBucks", 
                            "id": 2
                        }, 
                        "equiv_points": 10, 
                        "name": "free starbucks", 
                        "expire_in_days": 0, 
                        "id": 2, 
                        "expire_in_years": 3, 
                        "equiv_dollar": "10", 
                        "expire_in_months": 0, 
                        "description": "free one cup of starbucks coffee"
                    }, 
                    "expiration": "2012-08-20", 
                    "forsale": true
                }
            ], 
            "user": {
                "username": "ttttheman", 
                "referredby": null, 
                "phone": "4082323232", 
                "facebook": null, 
                "referredby_username": "ttttheman", 
                "email": "ttttheman@test.com"
            }
        }
        '''
        response = c.get("/api/users/1")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(4, len(r), '')
        self.assertEqual('4082323232', r['user']['phone'], '')
        self.assertEqual(2, r['userprogress']['cur_times'], '')
        self.assertEqual('Safeway', r['userprogress']['merchant']['name'], '')
        self.assertEqual(200, r['userpoint']['points'], '')
        self.assertEqual(2, len(r['userrewards']), '')
        self.assertEqual('free bread', r['userrewards'][0]['reward']['name'], '')
        self.assertEqual(10, r['userrewards'][1]['reward']['equiv_points'], '')
        self.assertEqual(True, r['userrewards'][1]['forsale'], '')
        #self.assertEqual('', r[][], '')
        
        jsonstr = json.dumps({"username":"xin","email":"xin@test.com","phone":"4082538985","referer":{"username":"ttttheman"}})
        response = c.post("/api/users", jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')

        response = c.get("/api/users/3")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(4, len(r), '')
        self.assertEqual('xin', r['user']['username'], '')
        self.assertEqual('4082538985', r['user']['phone'], '')
        self.assertEqual('xin@test.com', r['user']['email'], '')
        
        jsonstr = json.dumps({"username":"xin2","email":"xin2@test.com","phone":"6502538985"})
        response = c.put("/api/users/3", jsonstr, 'application/json')
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        response = c.get("/api/users/3")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(4, len(r), '')
        self.assertEqual('xin', r['user']['username'], '')
        self.assertEqual('6502538985', r['user']['phone'], '')
        self.assertEqual('xin2@test.com', r['user']['email'], '')
        
        response = c.delete("/api/users/3")
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/users")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), 'number of users is not 2')

        
    def test_userpref(self):
        """
        Tests UserPrefHandler
        """
        c = Client()
        
        '''
        {
            "nearby_radius": 40.0
        }
        '''
        response = c.get("/api/users/1/pref")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual(40.0, r['nearby_radius'], '')
        
        response = c.delete("/api/users/1/pref")
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/users/1/pref")
        #print response
        self.assertContains(response, "DoesNotExist: UserPref matching query does not exist.", status_code=500)
        
        jsonstr = json.dumps({"nearby_radius":25.5})
        response = c.post("/api/users/1/pref", jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')
        
        response = c.get("/api/users/1/pref")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual(25.5, r['nearby_radius'], '')
        
        jsonstr = json.dumps({"nearby_radius":45.0})
        response = c.put("/api/users/1/pref", jsonstr, 'application/json')
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        response = c.get("/api/users/1/pref")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual(45.0, r['nearby_radius'], '')        


    def test_merchant(self):
        """
        Tests merchant handler
        """
        c = Client()
        setup_func(connection)
        
        '''
        [
            {
                "name": "Safeway", 
                "longitude": 201.32300000000001, 
                "phone": "6502334332", 
                "address": "434 abc ave, san jose, ca", 
                "latitude": 102.45399999999999, 
                "logo": "/path/to/logo.png", 
                "email": "safeway@safeway.com"
            }
        ]
        '''
        response = c.get("/api/stores/prox/201.32,102.45,5")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), 'number of merchants is not 1')
        self.assertEqual('Safeway', r[0]['name'], '')
        self.assertEqual('6502334332', r[0]['phone'], '')
        self.assertEqual('/path/to/logo.png', r[0]['logo'], '')
        
        '''
        {
            "name": "Safeway", 
            "longitude": 201.32300000000001, 
            "phone": "6502334332", 
            "address": "434 abc ave, san jose, ca", 
            "latitude": 102.45399999999999, 
            "logo": "/path/to/logo.png", 
            "email": "safeway@safeway.com"
        }
        '''
        response = c.get("/api/stores/1")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(7, len(r), 'number of merchants is not 7')
        self.assertEqual('Safeway', r['name'], '')
        self.assertEqual('6502334332', r['phone'], '')
        self.assertEqual('/path/to/logo.png', r['logo'], '')
        
        jsonstr = json.dumps({"name":"BostonMarket","email":"xin@test.com","phone":"4082538985","address":"973 1st st, san jose, ca","logo":"/logo/bm.png","longitude":"150.20","latitude":"90.09"})
        response = c.post("/api/stores", jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')

        response = c.get("/api/stores/3")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(7, len(r), '')
        self.assertEqual('BostonMarket', r['name'], '')
        self.assertEqual('4082538985', r['phone'], '')
        self.assertEqual('/logo/bm.png', r['logo'], '')
        self.assertEqual('973 1st st, san jose, ca', r['address'], '')
        
        jsonstr = json.dumps({"email":"bm@test.com","phone":"6509234325"})
        response = c.put("/api/stores/3", jsonstr, 'application/json')
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        response = c.get("/api/stores/3")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(7, len(r), '')
        self.assertEqual('BostonMarket', r['name'], '')
        self.assertEqual('6509234325', r['phone'], '')
        self.assertEqual('bm@test.com', r['email'], '')
        
        response = c.delete("/api/stores/3")
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/stores/3")
        #print response.content
        self.assertContains(response, "DoesNotExist: Merchant matching query does not exist.", status_code=500)
 

    def test_purchase(self):
        """
        Tests purchase handler
        """
        c = Client()
        time = str(datetime.now())
        jsonstr = json.dumps({"time":time, "merchant":{"id":1}, "dollar_amount":20.50, "description":"test purchase"})
        response = c.post('/api/users/1/purchase', jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')
        
        '''
        [
            {
                "dollar_amount": "20.5", 
                "merchant": {
                    "name": "Safeway"
                }, 
                "description": "test purchase", 
                "time": "2011-09-30 23:49:03"
            }
        ]
        '''
        response = c.get('/api/users/1/purchase')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual('test purchase', r[0]['description'], '')
        self.assertEqual('Safeway', r[0]['merchant']['name'], '')
        
        response = c.delete('/api/users/1/purchase')
        #print response.content
        self.assertEqual(0, len(response.content), '')


    def test_rewardprogram(self):
        """
        Tests rewardprogram handler
        """
        c = Client()
        setup_func(connection)
        
        '''
        {
            "status": 1, 
            "merchant": {
                "name": "Safeway"
            }, 
            "name": "safeway loyalty program", 
            "prog_type": 1, 
            "reward_trigger": 200.0, 
            "end_time": null, 
            "reward": {
                "equiv_points": 20, 
                "name": "free bread"
            }, 
            "start_time": null
        }
        '''
        response = c.get("/api/stores/1/program/1")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(8, len(r), '')
        self.assertEqual('safeway loyalty program', r['name'], '')
        self.assertEqual(1, r['prog_type'], '')
        self.assertEqual(None, r['end_time'], '')
        self.assertEqual(200.0, r['reward_trigger'], '')

        '''
        [
            {
                "status": 1, 
                "merchant": {
                    "name": "Safeway"
                }, 
                "name": "safeway loyalty program", 
                "prog_type": 1, 
                "reward_trigger": 200.0, 
                "end_time": null, 
                "reward": {
                    "equiv_points": 20, 
                    "name": "free bread"
                }, 
                "start_time": null
            }, 
            {
                "status": 1, 
                "merchant": {
                    "name": "Safeway"
                }, 
                "name": "safeway loyalty program 2", 
                "prog_type": 1, 
                "reward_trigger": 400.0, 
                "end_time": null, 
                "reward": {
                    "equiv_points": 10, 
                    "name": "free starbucks"
                }, 
                "start_time": null
            }
        ]
        '''
        response = c.get("/api/stores/1/program")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), 'number of merchant reward programs is not 2')
        self.assertEqual('safeway loyalty program', r[0]['name'], '')
        self.assertEqual(1, r[0]['prog_type'], '')
        self.assertEqual(None, r[0]['end_time'], '')
        self.assertEqual(200.0, r[0]['reward_trigger'], '')
        self.assertEqual('safeway loyalty program 2', r[1]['name'], '')
        self.assertEqual(1, r[1]['prog_type'], '')
        self.assertEqual(None, r[1]['end_time'], '')
        self.assertEqual(400.0, r[1]['reward_trigger'], '')
        
        jsonstr = json.dumps({"name":"BostonMarket loyalty program","status":1,"prog_type":1,"reward_trigger":150.0,"end_time":"2012-05-26","reward":{"id":1}})
        response = c.post("/api/stores/1/program/1", jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')

        response = c.get("/api/stores/1/program/4")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(8, len(r), '')
        self.assertEqual('BostonMarket loyalty program', r['name'], '')
        self.assertEqual(1, r['prog_type'], '')
        self.assertEqual("2012-05-26", r['end_time'], '')
        self.assertEqual(150.0, r['reward_trigger'], '')
        self.assertEqual("free bread", r['reward']['name'], '')
        
        jsonstr = json.dumps({"prog_type":2,"reward_trigger":10,"reward":{"id":2}})
        response = c.put("/api/stores/1/program/4", jsonstr, 'application/json')
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        response = c.get("/api/stores/1/program/4")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(8, len(r), '')
        self.assertEqual('BostonMarket loyalty program', r['name'], '')
        self.assertEqual(2, r['prog_type'], '')
        self.assertEqual("2012-05-26", r['end_time'], '')
        self.assertEqual(10, r['reward_trigger'], '')
        self.assertEqual("free starbucks", r['reward']['name'], '')
        
        response = c.delete("/api/stores/1/program/4")
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/stores/1/program")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), 'number of merchant reward programs is not 2')
        
        response = c.delete("/api/stores/1/program")
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/stores/1/program")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), 'number of merchant reward programs is not 0')
 
    
    def test_reward(self):
        '''
        Test RewardHandler
        '''
        c = Client()
        setup_func(connection)
        
        '''
         {
            "status": 1, 
            "merchant": {
                "name": "Safeway", 
                "id": 1
            }, 
            "equiv_points": 20, 
            "name": "free bread", 
            "expire_in_days": 0, 
            "id": 1, 
            "expire_in_years": 3, 
            "equiv_dollar": "20", 
            "expire_in_months": 0, 
            "description": "free whole-wheet bread"
        }
        '''
        response = c.get("/api/stores/1/reward/1")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(10, len(r), '')
        self.assertEqual('free bread', r['name'], '')
        self.assertEqual(20, r['equiv_points'], '')
        self.assertEqual(3, r['expire_in_years'], '')
        self.assertEqual('Safeway', r['merchant']['name'], '')

        '''
        [
            {
                "status": 1, 
                "merchant": {
                    "name": "Safeway", 
                    "id": 1
                }, 
                "equiv_points": 20, 
                "name": "free bread", 
                "expire_in_days": 0, 
                "id": 1, 
                "expire_in_years": 3, 
                "equiv_dollar": "20", 
                "expire_in_months": 0, 
                "description": "free whole-wheet bread"
            }
        ]
        '''
        response = c.get("/api/stores/1/reward")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), 'number of merchant rewards is not 1')
        self.assertEqual('free bread', r[0]['name'], '')
        self.assertEqual(20, r[0]['equiv_points'], '')
        self.assertEqual(3, r[0]['expire_in_years'], '')
        self.assertEqual('Safeway', r[0]['merchant']['name'], '')
        
        jsonstr = json.dumps({"name":"free meal","status":1,"equiv_dollar":30,"equiv_points":30,"expire_in_days":"100","expire_in_years":"1","expire_in_months":"0","description":"free meal only"})
        response = c.post("/api/stores/1/reward", jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')

        response = c.get("/api/stores/1/reward/3")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(10, len(r), '')
        self.assertEqual('free meal', r['name'], '')
        self.assertEqual(30, r['equiv_points'], '')
        self.assertEqual(1, r['expire_in_years'], '')
        self.assertEqual('Safeway', r['merchant']['name'], '')
        
        jsonstr = json.dumps({"equiv_points":50,"expire_in_months":5})
        response = c.put("/api/stores/1/reward/3", jsonstr, 'application/json')
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        response = c.get("/api/stores/1/reward/3")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(10, len(r), '')
        self.assertEqual('free meal', r['name'], '')
        self.assertEqual(50, r['equiv_points'], '')
        self.assertEqual(5, r['expire_in_months'], '')
        self.assertEqual('Safeway', r['merchant']['name'], '')
        
        response = c.delete("/api/stores/1/reward/3")
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/stores/1/reward")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), 'number of merchant reward rewards is not 1')
        
        response = c.delete("/api/stores/1/reward")
        #print response.content
        self.assertEqual(0, len(response.content), '')
        
        response = c.get("/api/stores/1/reward")
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), 'number of merchant reward rewards is not 0')
        
        
    def test_userreward(self):
        '''
        Test UserRewardHandler
        '''
        c = Client()
        
        response = c.get('/api/users/reward')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(4, len(r), '')
        
        '''
        [
            {
                "user": {
                    "username": "ttttheman", 
                    "facebook": null, 
                    "id": 1
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "StarBucks", 
                        "id": 2
                    }, 
                    "equiv_points": 10, 
                    "name": "free starbucks", 
                    "expire_in_days": 0, 
                    "id": 2, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "10", 
                    "expire_in_months": 0, 
                    "description": "free one cup of starbucks coffee"
                }, 
                "expiration": "2012-08-20", 
                "forsale": true
            }, 
            {
                "user": {
                    "username": "ttttheman2", 
                    "facebook": null, 
                    "id": 2
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "expiration": "2012-08-15", 
                "forsale": true
            }
        ]      
        '''
        response = c.get('/api/users/reward/forsell')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), '')
        self.assertEqual('free one cup of starbucks coffee', r[0]['reward']['description'], '')
        self.assertEqual('ttttheman', r[0]['user']['username'], '')
        self.assertEqual(10, r[0]['reward']['equiv_points'], '')
        self.assertEqual(True, r[0]['forsale'], '')
        self.assertEqual('2012-08-20', r[0]['expiration'], '')
        self.assertEqual('free whole-wheet bread', r[1]['reward']['description'], '')
        self.assertEqual('ttttheman2', r[1]['user']['username'], '')
        self.assertEqual(20, r[1]['reward']['equiv_points'], '')
        self.assertEqual(True, r[1]['forsale'], '')
        self.assertEqual('2012-08-15', r[1]['expiration'], '')
        
        jsonstr = json.dumps({"merchant_id":1, "rewardprogram_id":1})
        response = c.post('/api/users/1/reward', jsonstr, 'application/json')
        #print response.content
        self.assertContains(response, "user hasn't made enough purchases to be eligible for a reward")
        
        jsonstr = json.dumps({"merchant_id":2, "rewardprogram_id":2})
        response = c.post('/api/users/2/reward', jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')
        
        jsonstr = json.dumps({"forsale":True, "reward":{'id':1}})
        response = c.put('/api/users/1/reward', jsonstr, 'application/json')
        #print response.content
        self.assertEqual('OK', response.content, '')
        
        '''
        [
            {
                "user": {
                    "username": "ttttheman", 
                    "facebook": null, 
                    "id": 1
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "expiration": "2012-03-12", 
                "forsale": true
            }, 
            {
                "user": {
                    "username": "ttttheman", 
                    "facebook": null, 
                    "id": 1
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "StarBucks", 
                        "id": 2
                    }, 
                    "equiv_points": 10, 
                    "name": "free starbucks", 
                    "expire_in_days": 0, 
                    "id": 2, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "10", 
                    "expire_in_months": 0, 
                    "description": "free one cup of starbucks coffee"
                }, 
                "expiration": "2012-08-20", 
                "forsale": true
            }
        ]
        '''
        response = c.get('/api/users/1/reward')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(2, len(r), '')
        self.assertEqual('free one cup of starbucks coffee', r[1]['reward']['description'], '')
        self.assertEqual('ttttheman', r[1]['user']['username'], '')
        self.assertEqual(10, r[1]['reward']['equiv_points'], '')
        self.assertEqual(True, r[1]['forsale'], '')
        self.assertEqual('2012-08-20', r[1]['expiration'], '')
        self.assertEqual('free whole-wheet bread', r[0]['reward']['description'], '')
        self.assertEqual('ttttheman', r[0]['user']['username'], '')
        self.assertEqual(20, r[0]['reward']['equiv_points'], '')
        self.assertEqual(True, r[0]['forsale'], '')
        self.assertEqual('2012-03-12', r[0]['expiration'], '')
        
        response = c.delete('/api/users/1/reward')
        #print response.content
        self.assertEqual(0, len(response.content), '')   
        
        response = c.get('/api/users/1/reward')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        
        
    def test_trade(self):
        """
        Tests trade activity handler
        """
        c = Client()
        jsonstr = json.dumps({"reward":{"id":1}, "from_user":{'id':2}, "description":"test buy"})
        response = c.post('/api/users/1/buy', jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')
        
        '''
        [
            {
                "description": "test buy", 
                "points_value": 20, 
                "time": "2011-10-02 00:23:12", 
                "to_user": {
                    "username": "ttttheman", 
                    "phone": "4082323232", 
                    "facebook": null, 
                    "email": "ttttheman@test.com", 
                    "referer": {
                        "id": 2
                    }
                }, 
                "from_user": {
                    "username": "ttttheman2", 
                    "phone": "4084545455", 
                    "facebook": null, 
                    "email": "ttttheman2@test.com"
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "activity_type": 2
            }
        ]
        '''
        response = c.get('/api/users/1/buy')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual('test buy', r[0]['description'], '')
        self.assertEqual(20, r[0]['points_value'], '')
        self.assertEqual('ttttheman2', r[0]['from_user']['username'], '')
        self.assertEqual('ttttheman', r[0]['to_user']['username'], '')
        self.assertEqual(20, r[0]['reward']['equiv_points'], '')
        self.assertEqual('free bread', r[0]['reward']['name'], '')
        self.assertEqual(2, r[0]['activity_type'], '')
        
        buyerPoint = UserPoint.objects.get(user__id=1)
        sellerPoint = UserPoint.objects.get(user__id=2)
        userrewards = UserReward.objects.filter(user__id=1, reward__id=1)
        self.assertEqual(180, buyerPoint.points, '')
        self.assertEqual(170, sellerPoint.points, '')
        self.assertEqual(2, len(userrewards), '')
        self.assertEqual(False, userrewards[0].forsale, '')
        self.assertEqual(False, userrewards[1].forsale, '')
        
        response = c.delete('/api/users/1/buy')
        #print response.content
        self.assertEqual(0, len(response.content), '')

        response = c.get('/api/users/1/buy')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        

    def test_gift(self):
        """
        Tests gift activity handler
        """
        c = Client()
        jsonstr = json.dumps({"reward":{"id":1}, "to_user":{'id':2}, "description":"test gifting"})
        response = c.post('/api/users/1/gift', jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')
        
        '''
        [
            {
                "description": "test gifting", 
                "points_value": 20, 
                "time": "2011-10-02 01:04:39", 
                "to_user": {
                    "username": "ttttheman2", 
                    "phone": "4084545455", 
                    "facebook": null, 
                    "email": "ttttheman2@test.com"
                }, 
                "from_user": {
                    "username": "ttttheman", 
                    "phone": "4082323232", 
                    "facebook": null, 
                    "email": "ttttheman@test.com", 
                    "referer": {
                        "id": 2
                    }
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "activity_type": 3
            }
        ]
        '''
        response = c.get('/api/users/1/gift')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual('test gifting', r[0]['description'], '')
        self.assertEqual(20, r[0]['points_value'], '')
        self.assertEqual('ttttheman', r[0]['from_user']['username'], '')
        self.assertEqual('ttttheman2', r[0]['to_user']['username'], '')
        self.assertEqual(20, r[0]['reward']['equiv_points'], '')
        self.assertEqual('free bread', r[0]['reward']['name'], '')
        self.assertEqual(3, r[0]['activity_type'], '')
        
        buyerPoint = UserPoint.objects.get(user__id=1)
        sellerPoint = UserPoint.objects.get(user__id=2)
        gifterrewards = UserReward.objects.filter(user__id=1, reward__id=1)
        gifteerewards = UserReward.objects.filter(user__id=2, reward__id=1)
        self.assertEqual(200, buyerPoint.points, '')
        self.assertEqual(150, sellerPoint.points, '')
        self.assertEqual(0, len(gifterrewards), '')
        self.assertEqual(2, len(gifteerewards), '')
        self.assertEqual(False, gifteerewards[0].forsale, '')
        self.assertEqual(True, gifteerewards[1].forsale, '')
        
        response = c.delete('/api/users/1/gift')
        #print response.content
        self.assertEqual(0, len(response.content), '')

        response = c.get('/api/users/1/gift')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        

    def test_redeem(self):
        """
        Tests redeem activity handler
        """
        c = Client()
        jsonstr = json.dumps({"reward":{"id":1}, "description":"test redeem"})
        response = c.post('/api/users/1/redeem', jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')
        
        '''
        [
            {
                "description": "test redeem", 
                "points_value": 20, 
                "time": "2011-10-02 02:08:27", 
                "to_user": null, 
                "from_user": {
                    "username": "ttttheman", 
                    "phone": "4082323232", 
                    "facebook": null, 
                    "email": "ttttheman@test.com", 
                    "referer": {
                        "id": 2
                    }
                }, 
                "reward": {
                    "status": 1, 
                    "merchant": {
                        "name": "Safeway", 
                        "id": 1
                    }, 
                    "equiv_points": 20, 
                    "name": "free bread", 
                    "expire_in_days": 0, 
                    "id": 1, 
                    "expire_in_years": 3, 
                    "equiv_dollar": "20", 
                    "expire_in_months": 0, 
                    "description": "free whole-wheet bread"
                }, 
                "activity_type": 1
            }
        ]
        '''
        response = c.get('/api/users/1/redeem')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual('test redeem', r[0]['description'], '')
        self.assertEqual(20, r[0]['points_value'], '')
        self.assertEqual('ttttheman', r[0]['from_user']['username'], '')
        self.assertEqual(None, r[0]['to_user'], '')
        self.assertEqual(20, r[0]['reward']['equiv_points'], '')
        self.assertEqual('free bread', r[0]['reward']['name'], '')
        self.assertEqual(1, r[0]['activity_type'], '')
        
        userrewards = UserReward.objects.filter(user__id=1, reward__id=1)
        self.assertEqual(0, len(userrewards), '')
        
        response = c.delete('/api/users/1/redeem')
        #print response.content
        self.assertEqual(0, len(response.content), '')

        response = c.get('/api/users/1/redeem')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        

    def test_refer(self):
        """
        Tests referral activity handler
        """
        c = Client()
        jsonstr = json.dumps({"referee_name":"xin", "refer_method":1})
        response = c.post('/api/users/1/refer', jsonstr, 'application/json')
        #print response.content
        self.assertEqual('Created', response.content, '')
        
        '''
        [
            {
                "referee_name": "xin", 
                "referee_join_time": null, 
                "refer_method": 1, 
                "time": "2011-10-02 02:46:45"
            }
        ]
        '''
        response = c.get('/api/users/1/refer')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(1, len(r), '')
        self.assertEqual('xin', r[0]['referee_name'], '')
        self.assertEqual(None, r[0]['referee_join_time'], '')
        self.assertEqual(1, r[0]['refer_method'], '')
        
        response = c.delete('/api/users/1/refer')
        #print response.content
        self.assertEqual(0, len(response.content), '')

        response = c.get('/api/users/1/refer')
        #print response.content
        r = json.loads(response.content)
        self.assertEqual(0, len(r), '')
        
