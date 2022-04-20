from django import forms

class LoginForm(forms.Form):
    """Formulario para autenticar usuarios"""
    username = forms.CharField(label='Nombre de usuario', max_length=100) 
    password = forms.CharField(label='Contraseña', max_length=100, widget=forms.PasswordInput)
    
    # TODO: cambiar en username por :forms.EmailField o forms.EmailInput?
    #       username = forms.EmailField(label='Email', max_length=100)