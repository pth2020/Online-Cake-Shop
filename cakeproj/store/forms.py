from django import forms
from django.forms import ModelForm
from .models import Contact

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email Address")
    
#the form fields are automatically tied to the Contact model, 
# so any submitted data will be saved to the Contact table in the database.
class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'message')
        
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'email':forms.EmailInput(attrs={'class':'form-control'}),
            'message':forms.Textarea(attrs={'class':'form-control'})
        }
        
