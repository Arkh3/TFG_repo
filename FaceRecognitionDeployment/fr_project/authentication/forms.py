from django import forms

class LoginPwdForm(forms.Form):
    """Formulario para recolectar la contraseña usuarios"""
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    
class ResetPwdForm(forms.Form):
    """Formulario para recolectar la contraseña usuarios"""
    password0 = forms.CharField(label='Contraseña actual', widget=forms.PasswordInput)
    password1 = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repite la nueva contraseña', widget=forms.PasswordInput)

class LoginEmailForm(forms.Form):
    """Formulario para recolectar el email usuarios"""
    email = forms.EmailField(label='Email', max_length=100)

class RegisterForm(forms.Form):
    """Formulario para registrar usuarios"""
    email = forms.EmailField(label='Email', max_length=100)
    pass1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)     
    pass2 = forms.CharField(label='Repite la contraseña', widget=forms.PasswordInput)