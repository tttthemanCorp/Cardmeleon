'''
Created on Sep 20, 2011

@author: jlu
'''
from django.test import TestCase
from django.test.client import Client
from datetime import datetime
import json


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
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
        c = Client()
        response = c.get("/api/users/1/pref")
        #print response

    def test_purchase(self):
        """
        Tests purchase handler
        """
        time = str(datetime.now())
        jsonstr = json.dumps({"time":time, "merchant":{"name":"Safeway"}, "dollar_amount":20.50, "description":"test purchase", "points_earned":0})
        c = Client()
        response = c.post('/api/users/1/purchase', jsonstr, 'application/json')
        #print "post: "
        #print response
        response = c.get('/api/users/1/purchase')
        #print "get: "
        #print response
        response = c.delete('/api/users/1/purchase')
        #print "delete: "
        #print response
        
    def test_merchant(self):
        """
        Tests merchant handler
        """
        c = Client()
        response = c.get('/api/stores/1')
        #print response
        response = c.get('/api/stores/')
        #print response
        
    def test_rewardprogram(self):
        """
        Tests rewardprogram handler
        {
        "status": 1, 
        "name": "safeway loyalty program 2", 
        "prog_type": 1, 
        "reward_trigger": 300.0, 
        "end_time": null, 
        "reward_id": 2, 
        "start_time": null
        }
        """
        pass
    