from datetime import date, datetime
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
import requests
from django.conf import settings
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, RegisterForm, ReservationForm, PaymentForm
from hotel.utils import utils
from .utils import tokenRequiredDecorator






# Create your views here.

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
        warnings = request.GET['warnings'] if 'warnings' in request.GET else None
        info = request.GET['info'] if 'info' in request.GET else None
        loginForm = {"form" : LoginForm(), "url" : settings.WEBSERVICE_URL, "method" : "POST"}
        return render(request, 'hotel/login.html', {'loginForm' : loginForm, 'warnings' : warnings, 'info' : info})

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["GET"])
def logout(request):
    response = redirect('index')
    response.delete_cookie('token')
    response.delete_cookie('account')
    return response

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
                    return render(request, 'hotel/register.html', {'registerForm' : registerForm, 'warnings' : "Passwords don't match"})
                url = '%sregistration/account' % (settings.WEBSERVICE_URL)
                # deserialize
                account = {}
                account['password'] = password
                account['firstName'] = form.cleaned_data['firstName']
                account['lastName'] = form.cleaned_data['lastName']
                account['birthDate'] = form.cleaned_data['birthDate']
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
                response['Location'] += '?info=Account registered'
                return response
            except ValueError as e:
                return HttpResponse(e)
        errorFields = form.errors.keys()
        registerForm = {"form" : RegisterForm(initial=request.POST), "method" : "POST"}
        return render(request, 'hotel/register.html', {'registerForm' : registerForm, 'warnings' : "Invalid fields: %s" % (', '.join(errorFields))})
    else:
        registerForm = {"form" : RegisterForm(), "url" : request.get_full_path(), "method" : "POST"}
        return render(request, 'hotel/register.html', {'registerForm' : registerForm})

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["GET"])
def hotels(request):
    warnings = request.GET['warnings'] if 'warnings' in request.GET else None
    info = request.GET['info'] if 'info' in request.GET else None
    token = request.COOKIES.get('token')
    url = '%shotel/hotels' % (settings.WEBSERVICE_URL)
    r = requests.get(url, headers={'Token-Auth' : token})
    if(r.status_code == 200):
        data = json.loads(r.text)
        return render(request, 'hotel/hotels/list.html', {'hotels' : data, 'info' : info, 'warnings' : warnings})
    return HttpResponse(status=r.status_code)

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["GET"])
def rooms(request, hotel_id):
    warnings = request.GET['warnings'] if 'warnings' in request.GET else None
    info = request.GET['info'] if 'info' in request.GET else None
    token = request.COOKIES.get('token')
    url = '%shotel/roomTypes/%s' % (settings.WEBSERVICE_URL, hotel_id)
    r = requests.get(url, headers={'Token-Auth' : token})
    if(r.status_code == 200):
        data = json.loads(r.text)
        return render(request, 'hotel/hotels/rooms/list.html', {'hotel_id' : hotel_id, 'rooms': data, 'reservationForm' : ReservationForm(), 'info' : info, 'warnings' : warnings})

@require_http_methods(["GET", "POST"])
def roomAvailability(request, hotel_id, room_id):
    token = request.COOKIES.get('token')
    if request.method == 'POST':
        reservationArray  = request.POST['reservationDates'].split(' - ');
        reservation = {}
        reservation['startDate'] = reservationArray[0]
        reservation['endDate'] = reservationArray[1]
        reservation['hotelId'] = hotel_id
        reservation['roomTypeId'] = room_id
        reservation['discountId'] = None
        reservation['accountId'] = request.COOKIES.get('account')
        token = request.COOKIES.get('token')
        url = '%sreservation/reservation' % (settings.WEBSERVICE_URL)
        r = requests.post(url, data=json.dumps(reservation) ,headers={'Token-Auth' : token, 'Content-Type' : 'application/json'})
        return HttpResponse(status=r.status_code)
    else:
        url = '%sreservation/hotel/%s/roomType/%s/termins?year=%d' % (settings.WEBSERVICE_URL, hotel_id, room_id, date.today().year)
        r = requests.get(url, headers={'Token-Auth' : token})
        if(r.status_code == 200):
            data = json.loads(r.text)
            availabilities = utils.datesFromRanges(data)
            return HttpResponse(json.dumps(availabilities))
        else:
            return HttpResponse('test')

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["GET"])
def reservations(request):
    token = request.COOKIES.get('token')
    url = '%sreservation/client/%s/reservations' % (settings.WEBSERVICE_URL, request.COOKIES.get('account'))
    r = requests.get(url, headers={'Token-Auth' : token, 'Content-Type' : 'application/json; utf-8'})
    warnings = request.GET['warnings'] if 'warnings' in request.GET else None
    info = request.GET['info'] if 'info' in request.GET else None
    if(r.status_code == 200):
        data = json.loads(r.text)
        reservations = []
        complaints = {}
        for d in data:
            reservation = {}
            reservation['id'] = d['id']
            reservation['from'] = datetime.fromtimestamp(d['startDate'] / 1000).strftime('%Y-%m-%d')
            reservation['to'] = datetime.fromtimestamp(d['endDate'] / 1000).strftime('%Y-%m-%d')
            reservation['hotel'] = d['room']['hotel']['name']
            reservation['roomType'] = d['room']['roomType']['name']
            complaint = checkCompaint(request, d['id'])
            if complaint:
                complaints[complaint['reservation_id']] = {'id' : complaint['id'], 'desc' : complaint['description']}
            reservations.append(reservation)
        return render(request, 'hotel/reservations/list.html', {'reservations' : reservations, 'complaints' : complaints, 'info' : info, 'warnings' :warnings})
    return HttpResponse(status=r.status_code)

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["GET", "POST"])
def complaint(request, reservation_id):
    token = request.COOKIES.get('token')
    if request.method == "POST":
        url = '%scomplaint/complaint/reservation/%s' % (settings.WEBSERVICE_URL, reservation_id)
        data = json.dumps({'description' : request.POST['complaint']})
        r = requests.post(url, data=data, headers={'Token-Auth' : token, 'Content-Type' : 'application/json; utf-8'})
        return HttpResponse(status=r.status_code)
    else:
        complaint = checkCompaint(request, reservation_id)
        if not complaint:
            return HttpResponseNotFound();
        return HttpResponse(json.dumps(complaint), status = 200)

def checkCompaint(request, reservation_id):
    token = request.COOKIES.get('token')
    url = '%scomplaint/complaint/reservation/%s' % (settings.WEBSERVICE_URL, reservation_id)
    r = requests.get(url, headers={'Token-Auth' : token, 'Content-Type' : 'application/json; utf-8'})
    if r.status_code != 200:
        return None
    complaintObj = json.loads(r.text)
    return {'id' : complaintObj['id'], 'description' : complaintObj['description'], 'reservation_id' : complaintObj['reservation']['id']}

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["GET"])
def invoices(request):
    token = request.COOKIES.get('token')
    account = request.COOKIES.get('account')
    url = '%sinvoices/user/%s' % (settings.WEBSERVICE_URL, account)
    r = requests.get(url, headers={'Token-Auth' : token, 'Content-Type' : 'application/json; utf-8'})
    invoices = json.loads(r.text)
    invoicesList = [{'id' : invoice['id'], 'name' : invoice['invoiceName']} for invoice in invoices]
    return render(request, 'hotel/invoices/list.html', {'invoices' : invoicesList, 'info' : None, 'warnings' : None})

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["GET"])
def invoice(request, invoice_id):
    token = request.COOKIES.get('token')
    url = '%sinvoices/%s' % (settings.WEBSERVICE_URL, invoice_id)
    r = requests.get(url, headers={'Token-Auth' : token, 'Content-Type' : 'application/pdf'})
    f = open('/tmp/output', 'wb')
    f.write(r._content)
    f.close()
    return HttpResponse(r._content, content_type='application/pdf')

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["GET"])
def payments(request):
    warnings = request.GET['warnings'] if 'warnings' in request.GET else None
    info = request.GET['info'] if 'info' in request.GET else None
    token = request.COOKIES.get('token')
    account = request.COOKIES.get('account')
    url = '%spayment/%s' % (settings.WEBSERVICE_URL, account)
    r = requests.get(url, headers={'Token-Auth' : token, 'Content-Type' : 'application/json; utf-8'})
    if r.status_code == 200:
        payments = json.loads(r.text)
        paymentsList = []
        for payment in payments:
            paym = {}
            paym['id'] = payment['id']
            paym['room'] = payment['reservation']['room']['roomType']['name']
            paym['hotel'] = payment['reservation']['room']['hotel']['name']
            paym['from'] = datetime.fromtimestamp(payment['reservation']['startDate'] / 1000).strftime('%Y-%m-%d')
            paym['to'] = datetime.fromtimestamp(payment['reservation']['endDate'] / 1000).strftime('%Y-%m-%d')
            paym['status'] = payment['status']
            paym['dueDate'] =datetime.fromtimestamp(payment['dueDate'] / 1000).strftime('%Y-%m-%d')
            paym['cost'] = payment['grossCost']
            paymentsList.append(paym)

        return render(request, 'hotel/payments/list.html', {'payments' : paymentsList, 'paymentForm' : PaymentForm(), 'info' : info, 'warnings' : warnings})
    return HttpResponse(status=r.status_code)

@tokenRequiredDecorator.tokenRequired
@require_http_methods(["POST"])
def paymentPay(request, payment_id):
    token = request.COOKIES.get('token')
    account = request.COOKIES.get('account')
    paymentType = request.POST['type']
    paymentValue = request.POST['value']
    url = '%spayment/%s/%s/pay?%s=%s' % (settings.WEBSERVICE_URL, account, payment_id, 'credit_card' if paymentType == 'cardNo' else 'transfer', paymentValue)
    r = requests.post(url, headers={'Token-Auth' : token})
    return HttpResponse(status=r.status_code)