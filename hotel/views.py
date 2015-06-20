from datetime import date
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from .forms import LoginForm, RegisterForm, ReservationForm
from requests import Request
import requests
from django.conf import settings
from hotel.utils import utils
from .utils import tokenRequiredDecorator
from . import objects
import json
from django.views.decorators.http import require_http_methods
# Create your views here.

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["GET"])
def index(request):
    return render(request, 'hotel/index.html', {'info' : request.GET['info'] if 'info' in request.GET else None,
                                                'warnings' : request.GET['warnings'] if 'warnings' in request.GET else None})

@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']
            url = '%slogin/in/%s/%s' % (settings.WEBSERVICE_URL, username, password)
            r = requests.post(url)
            if r.status_code == 200:
                response = HttpResponse('logged in')
                response = redirect('index')
                response['Location'] += '?info=logged_in'
                response.set_cookie("token", r.json()['token'])
                response.set_cookie("account", r.json()['account']['id'])
                return response
            elif r.status_code in (400, 401):
                loginForm = {"form" : LoginForm(initial=request.POST), "url" : settings.WEBSERVICE_URL, "method" : "POST"}
                return render(request, 'hotel/login.html', {'loginForm' : loginForm, 'warnings' : 'Wrong username/password provided'})
            else:
                loginForm = {"form" : LoginForm(initial=request.POST), "url" : settings.WEBSERVICE_URL, "method" : "POST"}
                return render(request, 'hotel/login.html', {'loginForm' : loginForm, 'warnings' : 'Something went wrong'})
        loginForm = {"form" : LoginForm(initial=request.POST), "url" : settings.WEBSERVICE_URL, "method" : "POST"}
        return render(request, 'hotel/login.html', {'loginForm' : loginForm, 'warnings' : 'Something went wrong'})
    else:
        warnings = None
        info = None
        if 'warnings' in request.GET:
            warnings = request.GET['warnings'] if 'warnings' in request.GET else None
        if 'info' in request.GET:
            info = request.GET['info'] if 'info' in request.GET else None
        loginForm = {"form" : LoginForm(), "url" : settings.WEBSERVICE_URL, "method" : "POST"}
        return render(request, 'hotel/login.html', {'loginForm' : loginForm, 'warnings' : warnings, 'info' : info})

@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']
            try:
                if password != password2:
                    registerForm = {"form" : RegisterForm(initial=request.POST), "url" : settings.WEBSERVICE_URL, "method" : "POST"}
                    return render(request, 'hotel/register.html', {'registerForm' : registerForm, 'warnings' : "Passwords not match"})
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
                account['address']['postalCode'] = form.cleaned_data['postalCode'].replace('-', '')
                account['address']['country'] = form.cleaned_data['country']
                account['regulaminAccepted'] = True

                data = json.dumps(account)

                r = requests.post(url, data=data ,headers={"Content-Type" : "application/json"})
                response = redirect('login')
                response['Location'] += '?info=registered'
                return response
            except ValueError as e:
                return HttpResponse(e)
        registerForm = {"form" : RegisterForm(initial=request.POST), "method" : "POST"}
        return render(request, 'hotel/register.html', {'registerForm' : registerForm, 'warnings' : "Something went wrong"})
    else:
        registerForm = {"form" : RegisterForm(), "url" : request.get_full_path(), "method" : "POST"}
        return render(request, 'hotel/register.html', {'registerForm' : registerForm})

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["GET"])
def hotels(request):
    token = request.COOKIES.get('token')
    url = '%shotel/hotels' % (settings.WEBSERVICE_URL)
    r = requests.get(url, headers={'Token-Auth' : token})
    if(r.status_code == 200):
        data = json.loads(r.text    )
        return render(request, 'hotel/hotels/list.html', {'hotels' : data, 'info' : 'test'})
    response = redirect('login')
    response['Location'] += '?warnings=login_required'
    return response

@require_http_methods(["GET"])
def rooms(request, hotel_id):
    token = request.COOKIES.get('token')
    url = '%shotel/roomTypes/%s' % (settings.WEBSERVICE_URL, hotel_id)
    r = requests.get(url, headers={'Token-Auth' : token})
    if(r.status_code == 200):
        data = json.loads(r.text)
        return render(request, 'hotel/hotels/rooms/list.html', {'hotel_id' : hotel_id, 'rooms': data})

@require_http_methods(["GET", "POST"])
def roomAvailability(request, hotel_id, room_id):
    token = request.COOKIES.get('token')
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservationArray  = form.cleaned_data['reservationDates'].split(' - ')
            reservation = {}
            reservation['startDate'] = reservationArray[0]
            reservation['endDate'] = reservationArray[1]
            reservation['roomId'] = room_id
            reservation['discountId'] = None
            reservation['accountId'] = request.COOKIES.get('account')
            token = request.COOKIES.get('token')
            url = '%sreservation/reservation' % (settings.WEBSERVICE_URL)
            jsonReservation = json.dumps(reservation)
            r = requests.post(url, data=json.dumps(reservation) ,headers={'Token-Auth' : token, 'Content-Type' : 'application/json'})
            if r.status_code == 200:
                response = redirect('roomAvailabilty')
                return response
        else:
            reservationForm = {"form" : ReservationForm(), "url" : settings.WEBSERVICE_URL, "method" : "POST"}
            return render(request, 'hotel/hotels/rooms/availability.html', {'hotel_id' : hotel_id, 'availabilities': data, "reservationForm" : reservationForm, "warnings" : "Something went wrong"})
    else:
        url = '%sreservation/hotel/%s/roomType/%s/termins?year=%d' % (settings.WEBSERVICE_URL, hotel_id, room_id, date.today().year)
        r = requests.get(url, headers={'Token-Auth' : token})
        if(r.status_code == 200):
            data = json.loads(r.text)
            availabilities = utils.datesFromRanges(data)
        else:
            return HttpResponse('test')
        reservationForm = {"form" : ReservationForm(), "url" : settings.WEBSERVICE_URL, "method" : "POST"}
        return render(request, 'hotel/hotels/rooms/availability.html', {'hotel_id' : hotel_id, 'availabilities': availabilities, "reservationForm" : reservationForm})
