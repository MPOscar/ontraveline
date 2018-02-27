from django import forms

class Add_Twilio_Client(forms.Form):
    email = forms.EmailField(label = 'E-mail', max_length = 64, required = True)
    account = forms.CharField(label = 'Account', max_length = 255, required = True)
    token = forms.CharField(label = 'Token', max_length = 255, required = True)

class Add_Twilio_Number(forms.Form):
    numero = forms.CharField(label = 'Número', max_length = 16, required = True)
    sid = forms.CharField(label = 'SID', max_length = 255, required = True)