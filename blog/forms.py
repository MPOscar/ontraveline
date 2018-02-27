from django import forms

class Blog_Form(forms.Form):
    search = forms.CharField(label = 'Buscar', max_length = 64, required = False)