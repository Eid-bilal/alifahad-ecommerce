from django import forms
from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    mobile = forms.CharField(max_length=15, required=True)
    confirmPassword = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        fields = ['username', 'mobile', 'email', 'password', 'confirmPassword']


from django import forms

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)


    
