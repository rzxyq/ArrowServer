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

TWILIO_NUMBER = "+16072755281"
AUTH_CODE_MIN = 100000
AUTH_CODE_MAX = 999999
 
@twilio_view
def sms(request):
    name = request.POST.get('Body', '') #default value is empty string
    msg = 'Hey %s, how are you today' % (name)
    r = twiml.Response()
    r.message(msg)



    return r
    # twiml = '<Response><Message>Hello from Arrow!</Message></Response>'
    # return HttpResponse(twiml, content_type='text/xml')

def home(request):
    context = {    
        'request' : request,   
    }
    return render(request, 'home.html', context)

# check the phone number is a valid phone
# return true if the number is valid, false otherwise
def phone_number_valid(phone_number):
    matchObj = re.match( r'^\+[0-9]{11}$', phone_number, )
    if matchObj is None:
        print(phone_number, "is not valid")
        return False
    else:
        return True

@csrf_exempt
def phoneAuth(request):
    '''
    request format:
    url = 'localhost:8000'
    data = json.dumps({
        'num': +16072629422
    })
    '''
    if request.method == 'POST':
        import ipdb; ipdb.set_trace()
        try:
            data = json.loads(request.body.decode('utf-8'))
            num=data['num']
        except:
            return JsonResponse({
                'error': 'Incorrect formet for phoneAuth. Must have "num" attribute'
                })
        if not phone_number_valid(num):
            return JsonResponse({
                'error': 'Invalid phone number'
                })
        authCode = random.randrange(AUTH_CODE_MIN, AUTH_CODE_MAX)
        body = "Hello from Arow! Your authentication code is: "+str(authCode)

        # account_sid = os.environ['TWILIO_ACCOUNT_SID']
        # auth_token = os.environ['TWILIO_AUTH_TOKEN']
        account_sid = 'ACfb15e6282b3e9c65b4c9fb5be5b5e179'
        auth_token = 'e39388e8ef81d00a4e81466d4f76b69a'

        client = TwilioRestClient(account_sid, auth_token)
        # body = "Hello there! Here's your authentication code: %s" % (authCode)
        message = client.messages.create(body=body, to=str(num), from_=TWILIO_NUMBER)
        
        return JsonResponse({
            'authCode': authCode,
            'senderNum': num
            })
    return render(request, 'home.html')

    # return HttpResponse(twiml, content_type='text/xml')

