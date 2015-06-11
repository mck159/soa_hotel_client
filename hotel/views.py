from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .forms import LoginForm, RegisterForm
from requests import Request
import requests
from django.conf import settings
from .utils import tokenRequiredDecorator
from . import objects
import json
# Create your views here.

@tokenRequiredDecorator.tokenRequired
def index(request):
    #return HttpResponse(request.session.__str__())
    return HttpResponse("Hello")

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']
            url = '%slogin/in/%s/%s' % (settings.WEBSERVICE_URL, username, password)
            r = requests.post(url)
            if username == 'maciek' and password == 'test':
                response = HttpResponse('logged in')
                response.set_cookie("token", "OKI")
                return response
            else:
                return HttpResponse('unauthorized', status=401)
        return HttpResponse("not ok")



        return HttpResponse(settings.WEBSERVICE_URL)
    else:
        if 'redirect' in request.GET and request.GET['redirect'] == 'true':
            redir = True
        loginForm = {"form" : LoginForm(), "url" : settings.WEBSERVICE_URL, "method" : "POST"}
    return render(request, 'hotel/login.html', {'loginForm' : loginForm, 'redir' : True})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']
            try:
                if password != password2:
                    raise ValueError('Passwords not match')
                url = '%sregistration/account' % (settings.WEBSERVICE_URL)
                # deserialize
                account = {}
                account['password'] = password
                account['firstName'] = form.cleaned_data['firstName']
                account['lastName'] = form.cleaned_data['lastName']
                account['birthDate'] = form.cleaned_data['birthDate'].strftime('%Y-%m-%d')
                account['accountType'] = 'C'
                account['accountStatus'] = 'A'
                account['contact'] = {}
                account['contact']['mail'] = form.cleaned_data['email']
                account['address'] = {}
                account['address']['street'] = form.cleaned_data['street']
                account['address']['houseNumber']    = form.cleaned_data['houseNumber']
                account['address']['city'] = form.cleaned_data['city']
                account['address']['postalCode'] = form.cleaned_data['postalCode']
                account['address']['country'] = form.cleaned_data['country']
                account['regulaminAccepted'] = True

                data = json.dumps(account)

                r = requests.post(url, data=data ,headers={"Content-Type" : "application/json"})
                return HttpResponse('Dobrze wypelnione')
            except ValueError as e:
                return HttpResponse(e)
        return HttpResponse("Wypełnij wszystkie pola")
    else:
        registerForm = {"form" : RegisterForm(), "url" : settings.WEBSERVICE_URL, "method" : "POST"}
        return render(request, 'hotel/register.html', {'registerForm' : registerForm})
