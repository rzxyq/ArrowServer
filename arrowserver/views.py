from django.http import HttpResponse
from django.shortcuts import render, redirect

from twilio import twiml
from django_twilio.decorators import twilio_view
 
@twilio_view
def sms(request):
    name = request.POST.get('Body', '')
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


