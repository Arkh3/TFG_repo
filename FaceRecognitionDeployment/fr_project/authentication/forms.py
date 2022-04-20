from django import forms

class LoginForm(forms.Form):
    """Formulario para autenticar usuarios"""
    email = forms.EmailField(label='Email', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    """Formulario para autenticar usuarios"""
    email = forms.EmailField(label='Email', max_length=100)
    pass1 = forms.CharField(label='Password', widget=forms.PasswordInput())     
    pass2 = forms.CharField(label='Repeat your password', widget=forms.PasswordInput())     