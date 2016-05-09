from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import json
from twilio import twiml
from twilio.rest import TwilioRestClient
from django_twilio.decorators import twilio_view
import random
import os
import re
from firebase_token_generator import create_token
from .models import User
from .secrets import *
import base64
from push_notifications.models import APNSDevice, GCMDevice

def apihome(request):
    context = {    
        'request' : request,   
    }
    return render(request, 'apihome.html', context)


# check the phone number is a valid phone
# return true if the number is valid, false otherwise
def phone_number_valid(phone_number):
    phone_number = str(phone_number)
    matchObj = re.match( r'^[0-9]{11}$', phone_number, )
    if matchObj is None:
        matchObj = re.match( r'^[0-9]{11}$', phone_number, )
        print(phone_number, "is not valid")
        return False
    else:
        return True



def login(request):
    '''
    request format:
    url = 'localhost:8000'
    data = json.dumps({
        'num': 16072729999,
        'username': emily123, 
        'password': 1kfsd.2349f
        'loginMethod': phone
    })
    loginMethod has two values: phone or username
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            num=str(data['num'])
            password=data['password']
            username=data['username']
            login = data['loginMethod']
        except:
            return JsonResponse({
                'error': 'Incorrect formet for dataAuth. Must have "num" "password" and "username" and "loginMethod" attribute'
                })

        if login=='phone':
            #generate firebase token
            user=None
            try:
                user = User.objects.get(num=num)
            except: #if doesn't exist(thows query doesnt exist error)
                return JsonResponse({
                'error': 'User doesnt exist yet'
                })
            token = create_user(num, '', password)
            if token==None:
                return JsonResponse({
                'error': 'Password incorrect'
                })
            return JsonResponse({
                'token': token
            })
        if login=='username':
            #generate firebase token
            user=None
            try:
                user = User.objects.get(username=username)
            except: #if doesn't exist(thows query doesnt exist error)
                return JsonResponse({
                'error': 'User doesnt exist yet'
                })
            token = create_user(user.num, '', password)
            if token==None:
                return JsonResponse({
                'error': 'Password incorrect'
                })
            return JsonResponse({
                'token': token
            })
    return JsonResponse({
        'error': 'To user our api please send a post request'
        })


def phoneAuth(request):
    '''
    request format:
    url = 'localhost:8000'
    data = json.dumps({
        'num': 16072629432,
    })
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            num=data['num']
            num = str(num)
        except:
            return JsonResponse({
                'error': 'Incorrect formet for phoneAuth. Must have "num" attribute'
                })

        #check if user already exists
        try:
            user = User.objects.get(num=num)
        except: #if doesn't exist
            #twilio
            if not phone_number_valid(num):
                return JsonResponse({
                    'error': 'Invalid phone number'
                    })
            authCode = random.randrange(AUTH_CODE_MIN, AUTH_CODE_MAX)
            body = "Hello from Arrow! Your authentication code is: "+str(authCode)

            # ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
            # AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']

            client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
            # body = "Hello there! Here's your authentication code: %s" % (authCode)
            message = client.messages.create(body=body, to=str(num), from_=TWILIO_NUMBER)
            return JsonResponse({
                    'authCode': authCode,
                    'senderNum': num,
                })
        # if no error then user already exists
        return JsonResponse({
        'error': 'User already exists'
        })

    # return HttpResponse(twiml, content_type='text/xml')

    return JsonResponse({
        'error': 'To user our api please send a post request'
        })

def createUser(request):
    '''
    public api for creating a user
    request format:
    url = 'localhost:8000'
    data = json.dumps({
        'num': 16072729999,
        'username': emily123, 
        'password': 1kfsd.2349f
    })
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            num=data['num']
            num = str(num)
            password=data['password']
            username = data['username']
        except:
            return JsonResponse({
                'error': 'Incorrect formet. Must have "num" "username""password"attribute'
                })
        token = create_user(num, username, password)
        return JsonResponse({
            'token': token
        })
    return JsonResponse({
    'error': 'To user our api please send a post request'
    })


def create_user(num, username, password):
    '''create user in heroku database
    if user already exists(and password correct) return token without saving
    if password incorrect return None
    else save and return firebase token'''
    uid = num+password
    uid = base64.b64encode(uid.encode())
    uid = uid.decode() #byte back to string
    # auth_payload = {"uid": uid, "auth_data": "foo", "other_auth_data": "bar"}
    auth_payload = {"uid": uid}
    token = create_token(FIREBASE_SECRET, auth_payload)

    user = None
    try:
        user = User.objects.get(num=num)
    except:
        user = User(num=num, password=password, username=username)
        user.save()
        return token
    if user.password != password:
        return None
    return token

def username_exists(username):
    try:
        user = User.objects.get(username=username)
    except:
        return False
    return True

def num_exists(num):
    try:
        user = User.objects.get(num=num)
    except:
        return False
    return True

def usernameExists(request):
    '''takes 'username' and see if it exists
    return:
    exists: True or False
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data['username']
        except:
            return JsonResponse({
                'error': 'Incorrect formet.'
                })
        return JsonResponse({
            'exists': username_exists(username)
        })
    return JsonResponse({
    'error': 'To user our api please send a post request'
    })

def numExists(request):
    '''takes 'num' and see if it exists
    return:
    exists: True or False
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data['num']
        except:
            return JsonResponse({
                'error': 'Incorrect formet.'
                })
        return JsonResponse({
            'exists': num_exists(num)
        })
    return JsonResponse({
    'error': 'To user our api please send a post request'
    })

def pushNot(request):
    '''Takes <device_token>, <message>.
    Effect: if success, return status and send message to device.
    For details check https://github.com/jleclanche/django-push-notifications
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            device_token = data['device_token']
            message = data['message']
        except:
            return JsonResponse({
                'error': 'Incorrect formet. Check documentation for usage.'
                })
        device = APNSDevice.objects.get(registration_id=device_token)
        device.send_message(message, badge=1) # Alert message may only be sent as text.
        # device.send_message(None, badge=1, extra={"foo": "bar"}) # Silent message with badge and added custom data.
        return JsonResponse({
            'status': success
        })
    return JsonResponse({
    'error': 'To user our api please send a post request'
    })
