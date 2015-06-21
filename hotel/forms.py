from django import forms
from django.forms import extras


class LoginForm(forms.Form):
    login = forms.CharField(label='Login', max_length=255)
    password = forms.CharField(label='Hasło', max_length=255, widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    firstName = forms.CharField(label='Name', max_length=255)
    lastName = forms.CharField(label='Surname', max_length=255)
    email = forms.EmailField()
    birthDate = forms.CharField(label="Birth date", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    street= forms.CharField(label='Street', max_length=255)
    houseNumber = forms.CharField(label='House number', max_length=255)
    postalCode = forms.RegexField(label='Postal code', max_length=6, regex=r'^[0-9]{2}\-[0-9]{3}$', error_message = ("Invalid postcode format"))
    city = forms.CharField(label='City', max_length=255)
    country = forms.CharField(label='Country', max_length=255)
    password = forms.CharField(label='Password', max_length=255, widget=forms.PasswordInput())
    password2 = forms.CharField(label='Repeat password', max_length=255, widget=forms.PasswordInput())

class ReservationForm(forms.Form):
    reservationDates = forms.CharField(label='wybierz terminy rezerwacji', widget=forms.TextInput())

class PaymentForm(forms.Form):
    type = forms.ChoiceField(choices=[("cardNo", "cardNo"), ("bankName", "bankName")], widget=forms.RadioSelect(), initial="cardNo")
    value = forms.CharField(label='Nazwa banku lub numer karty kredytowej', widget=forms.TextInput())