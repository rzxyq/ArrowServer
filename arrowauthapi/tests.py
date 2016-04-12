from django.test import TestCase
from django.template.loader import render_to_string
from django.core.urlresolvers import resolve
from django.http import HttpRequest

from .models import User
from .views import *
from django.utils import timezone
import datetime
import base64

import json

# Create your tests here.
class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/arrowauthapi/')
        self.assertEqual(found.func, apihome)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = apihome(request)
        expected_html = render_to_string('apihome.html')
        self.assertEqual(response.content.decode(), expected_html)



class UserModelsTest(TestCase):
    # python manage.py shell
    # from data_.models import Trial, Data
    #from django.utils import timezone
    # t1 = Trial(1, 'first trial', datetime.date.today()) #1 at beginning is pk
    # d1 = Data(1, 9,0.18,0.78,0.75,3.95,32.6,0.167, 0.267,0.167,2, data_text='9,0.18,0.78,0.75,3.95,32.6,0.167', date_time=timezone.now(), trial=t1)
    # t1 = Trial.objects.filter(pk=1)[0]
    # t1.data_set.all()
    def test_saving_and_retrieving_items(self):
        u = User(num='16072629422', username='ruoyan', password='abc123')
        u.save()

        saved_data = User.objects.first()
        self.assertEqual(saved_data, u)
        self.assertNotEqual(u.date.hour, None) #test auto_add_now
        saved_t1_filter = User.objects.filter(num='16072629422')[0]
        self.assertEqual(saved_t1_filter, u)

        u2 = User(num='16072629422', username='ruoyan', password='abc123')
        u2.save()
        self.assertEqual(User.objects.count(), 2)

class PhoneAuthViewTest(TestCase):
    def test_create_user(self):
        #test user not exists before but create now
        value = create_user('16072629433', 'a11fsdf111')
        self.assertNotEqual(value, None)
        self.assertEqual(User.objects.count(), 1)


        u = User(num='16072629422', username='ruoyan', password='abc123')
        u.save()

        #test password incorrect
        value = create_user('16072629422', 'a11111')
        self.assertEqual(value, None)

        #test password correct and user exists
        value = create_user('16072629422', 'abc123')
        uid = '16072629422'+'abc123'
        uid = base64.b64encode(uid.encode())
        uid = uid.decode() #byte back to string
        auth_payload = {"uid": uid}
        token = create_token(FIREBASE_SECRET, auth_payload)
        self.assertEqual(value, token)

    def test_get(self):
        #dummy test
        response = self.client.get('/arrowauthapi/phoneAuth/')
        self.assertContains(response, 'To user our api please send a post request')
        self.assertNotContains(response, 'debug')
    def test_post(self):
        data = json.dumps({
        'num': '16072629422',
        'password': 'abc123'
        })
        self.client.post(
            '/arrowauthapi/phoneAuth/',
            content_type='application/json',
            data = data
        )
        self.assertEqual(User.objects.count(), 1)
        new_data = User.objects.first()
        self.assertEqual(new_data.num, '16072629422')
