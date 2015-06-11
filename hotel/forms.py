from django import forms
from django.forms import extras


class LoginForm(forms.Form):
    login = forms.CharField(label='Login', max_length=20)
    password = forms.CharField(label='Hasło', max_length=40, widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    firstName = forms.CharField(label='Name', max_length=20)
    lastName = forms.CharField(label='Surname', max_length=20)
    email = forms.EmailField()
    birthDate = forms.DateField(widget=extras.SelectDateWidget)
    street= forms.CharField(label='Street', max_length=20)
    houseNumber = forms.CharField(label='House number', max_length=20)
    postalCode = forms.CharField(label='Postal code', max_length=20)
    city = forms.CharField(label='City', max_length=20)
    country = forms.CharField(label='Country', max_length=20)
    password = forms.CharField(label='Password', max_length=40, widget=forms.PasswordInput())
    password2 = forms.CharField(label='Repeat password', max_length=40, widget=forms.PasswordInput())