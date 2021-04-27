from django import forms

# Create your forms here.

class ContactForm(forms.Form):
	first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control rounded-1', 'placeholder':'First Name'}))
	last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control rounded-1', 'placeholder':'Last Name'}))
	email_address = forms.CharField(max_length = 150, widget=forms.EmailInput(attrs={'class': 'form-control rounded-1', 'placeholder':'email'}))
	message = forms.CharField(widget = forms.Textarea(attrs={'class': 'form-control rounded-1', 'placeholder':'Your Message'}), max_length = 2000)