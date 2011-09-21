'''
Created on Sep 20, 2011

@author: jlu
'''
from django.test import TestCase
from django.test.client import Client


class ServerTest(TestCase):
    fixtures = ['testdata.json',]

    def setUp(self):
        pass
        
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
        c = Client()
        response = c.get("/api/users/1/pref")
        print response
