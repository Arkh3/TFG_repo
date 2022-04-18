from django import forms

class Register1(forms.Form):
    """Formulario para autenticar usuarios"""
    username = forms.CharField(label='', initial='Nombre') 
    mail = forms.EmailField(label='' , initial='Correo@electronico') 
    
class Register2(forms.Form):
    """Formulario para autenticar usuarios"""
    pass1 = forms.CharField(widget=forms.PasswordInput, label='Contraseña', initial='Contraseña')
    pass2 = forms.CharField(widget=forms.PasswordInput, label='Repite la contraseña', initial='Repite la contraseña')  

class Register3(forms.Form):
    """Formulario para autenticar usuarios"""
    username = forms.CharField(label='Nombre', initial='Nombre') 
    mail = forms.EmailField(label='Correo electronico' , initial='Correo@electronico') 
    pass1 = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    pass2 = forms.CharField(widget=forms.PasswordInput, label='Repite la contraseña')   
    