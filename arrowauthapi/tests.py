from django.test import TestCase
from django.template.loader import render_to_string
from django.core.urlresolvers import resolve
from django.http import HttpRequest

from .models import User
from .views import *
from django.utils import timezone
import datetime

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

class EdaViewTest(TestCase):
    def test_display_all_items(self):
        #dummy test
        response = self.client.get('/data/results/')
        self.assertContains(response, 'successful')
        self.assertNotContains(response, 'debug')

        #test eda value view
        response = self.client.get('/data/eda_view/')
        self.assertContains(response, 'EDA')
        self.assertNotContains(response, 'debug')

        #test frequency value view
        response = self.client.get('/data/frequency_view/')
        self.assertContains(response, 'Frequency')
        self.assertNotContains(response, 'debug')

        #test sums value view
        response = self.client.get('/data/sums_view/')
        self.assertContains(response, 'Sum')
        self.assertNotContains(response, 'debug')

                #test average value view
        response = self.client.get('/data/mean_view/')
        self.assertContains(response, 'Mean')
        self.assertNotContains(response, 'debug')


    # def test_uses_list_template(self):
    #     list_ = List.objects.create()
    #     response = self.client.get('/lists/%d/' % (list_.id))
    #     self.assertTemplateUsed(response, 'list.html')


# class PostDataTest(TestCase):
#     def test_can_save_POST_request(self):
#         from django.utils import timezone

#         #test trial auto create
#         l='C,0.24,0.87,0.64,3.95,32.6,0.167'
#         data_array = l.split(",")
#         if (data_array[0] == 'C' or data_array[0] == 'c'): 
#             data_array[0] = 10 # Modify for 10's 
#         data = json.dumps({
#             'data': l, # Text-based data
#             'seconds': data_array[0],
#             'x_coord': data_array[1],
#             'y_coord': data_array[2],
#             'z_coord': data_array[3],
#             'unknown': data_array[4],
#             'temp': data_array[5],
#             'eda': data_array[6],
#             'trial': 299
#         })
#         self.client.post(
#             '/data/post_data/',
#             content_type='application/json',
#             data = data
#         )

#         self.assertEqual(Data.objects.count(), 1)
#         new_data = Data.objects.first()
#         self.assertEqual(new_data.eda, 0.167)
#         self.assertEqual(Trial.objects.count(), 1)
#         self.assertEqual(Trial.objects.first().num, '299')

#         #test applying to same trial
#         data = json.dumps({
#             'data': '0,0.24,0.87,0.64,3.95,40,0.100', # Text-based data
#             'seconds': data_array[0],
#             'x_coord': data_array[1],
#             'y_coord': data_array[2],
#             'z_coord': data_array[3],
#             'unknown': data_array[4],
#             'temp': 40,
#             'eda': 0.100,
#             'trial': 299
#         })
#         self.client.post(
#             '/data/post_data/',
#             content_type='application/json',
#             data = data
#         )
#         self.assertEqual(Trial.objects.count(), 1)
#         self.assertEqual(Trial.objects.first().num, '299')
#         t = Trial.objects.filter(num=299)[0]
#         filtered_d = t.data_set.filter(eda=0.100)[0]
#         self.assertEqual(filtered_d.temp, 40)
#         self.assertEqual(t.data_set.count(), 2)






    # def test_redirects_after_POST(self):
    #     response = self.client.post(
    #         '/lists/new',
    #         data={'item_text': 'A new list item'}
    #     )
    #     new_list = List.objects.first()
    #     self.assertRedirects(response, '/lists/%d/' % (new_list.id))

