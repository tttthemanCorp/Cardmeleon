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
        
    def test_userpref(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
        c = Client()
        response = c.get("/api/users/1/pref")
        print response

    def test_purchase(self):
        """
        Tests purchase handler
        """
        time = str(datetime.now())
        jsonstr = json.dumps({"time":time, "merchant":{"name":"Safeway"}, "dollar_amount":20.50, "description":"test purchase", "points_earned":0})
        c = Client()
        response = c.post('/api/users/1/purchase', jsonstr, 'application/json')
        print "post: "
        print response
        response = c.get('/api/users/1/purchase')
        print "get: "
        print response
        response = c.delete('/api/users/1/purchase')
        print "delete: "
        print response
        
    def test_merchant(self):
        """
        Tests merchant handler
        """
        c = Client()
        response = c.get('/api/stores/1')
        print response
        response = c.get('/api/stores/')
        print response
        
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
    