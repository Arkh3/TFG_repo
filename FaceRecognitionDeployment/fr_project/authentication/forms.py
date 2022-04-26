from django import forms

# WARNING: si cambiamos los nombres o añadimos campos, hay que plasmarlo en login2.html
class LoginPwdForm(forms.Form):
    """Formulario para recolectar la contraseña usuarios"""
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class LoginEmailForm(forms.Form):
    """Formulario para recolectar el email usuarios"""
    email = forms.EmailField(label='Email', max_length=100)

class RegisterForm(forms.Form):
    """Formulario para registrar usuarios"""
    email = forms.EmailField(label='Email', max_length=100)
    pass1 = forms.CharField(label='Password', widget=forms.PasswordInput)     
    pass2 = forms.CharField(label='Repeat your password', widget=forms.PasswordInput)