from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm , SetPasswordForm
from django.contrib.auth.models import User


# Create your forms here.

class ContactForm(forms.Form):
	first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control rounded-1', 'placeholder':'First Name'}))
	last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control rounded-1', 'placeholder':'Last Name'}))
	email_address = forms.CharField(max_length = 150, widget=forms.EmailInput(attrs={'class': 'form-control rounded-1', 'placeholder':'email'}))
	message = forms.CharField(widget = forms.Textarea(attrs={'class': 'form-control rounded-1', 'placeholder':'Your Message'}), max_length = 2000)

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control rounded-1', 'placeholder':'Last Name'}))
    email = forms.CharField(max_length=254,required=True, help_text='Required. Inform a valid email address.', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'repeat password'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', )


class LogInForm(forms.Form):
	username = forms.CharField(max_length = 150, required=True,widget=forms.EmailInput(attrs={'class': 'form-control rounded-1', 'placeholder':'Your Email'}))
	passwd = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control rounded-1', 'placeholder':'Your Password'}))

class UserPasswordResetForm(PasswordResetForm):
    email = forms.CharField(max_length=254,required=True, help_text='Required. Inform a valid email address.', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Insert Your Email'}))

class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Insert New password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':'Repeat Password'}))

    class Meta:
        model = User
        fields = ('password1', 'password2',)