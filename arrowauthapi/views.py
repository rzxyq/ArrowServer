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



def dataAuth(request):
    '''
    request format:
    url = 'localhost:8000'
    data = json.dumps({
        'num': 16072729999, 
        'password': 1kfsd.2349f
    })
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            num=data['num']
            num = str(num)
            password=data['password']
        except:
            return JsonResponse({
                'error': 'Incorrect formet for phoneAuth. Must have "num" and "password" attribute'
                })

        token = create_user(num,password)
        if token==False:
            return JsonResponse({
            'error': 'Password incorrect'
            })
        return JsonResponse({
                    'token': token
                })


def phoneAuth(request):
    '''
    request format:
    url = 'localhost:8000'
    data = json.dumps({
        'num': 16072629432,
        'password': 'abc123'
    })
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            num=data['num']
            num = str(num)
            password=data['password']
        except:
            return JsonResponse({
                'error': 'Incorrect formet for phoneAuth. Must have "num" and "password" attribute'
                })

        #twilio
        if not phone_number_valid(num):
            return JsonResponse({
                'error': 'Invalid phone number'
                })
        authCode = random.randrange(AUTH_CODE_MIN, AUTH_CODE_MAX)
        body = "Hello from Arow! Your authentication code is: "+str(authCode)

        # ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
        # AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']

        client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
        # body = "Hello there! Here's your authentication code: %s" % (authCode)
        message = client.messages.create(body=body, to=str(num), from_=TWILIO_NUMBER)
        

        #generate firebase token
        user=None
        try:
            user = User.objects.get(num=num)
        except: #if doesn't exist(thows query doesnt exist error)
            token = create_user(num, password)
            return JsonResponse({
                'authCode': authCode,
                'senderNum': num,
                'token': token
            })
        #if no error then user exists
        return JsonResponse({
            'error': 'User already exists'
            })
       
    return render(request, 'home.html')

    # return HttpResponse(twiml, content_type='text/xml')

def create_user(num, password):
    '''create user in heroku database
    if user already exists(and password correct) return token without saving
    if password incorrect return false
    else save and return firebase token'''
    uid = num+password
    # auth_payload = {"uid": uid, "auth_data": "foo", "other_auth_data": "bar"}
    auth_payload = {"uid": uid}
    token = create_token(FIREBASE_SECRET, auth_payload)

    user = None
    try:
        user = User.objects.get(num=num)
    except:
        user = User(num=num, password=password)
        user.save()
        return token
    if user.password != password:
        return False
    return token
