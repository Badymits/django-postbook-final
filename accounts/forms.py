from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Account

class LoginModelForm(forms.ModelForm):
    
    class Meta:
        model = Account
        fields = ['email', 'password']
        
        widgets ={
            "email": forms.TextInput(
                attrs={
                    "class": "border border-solid w-full h-[40px] rounded-lg",
                    "placeholder": "Enter email",
                    
                }
            
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "border border-solid w-full h-[40px] rounded-lg ",
                    "placeholder": "Enter password",
                }
            )
        }

class RegisterModelForm(UserCreationForm):
    
    
    password1           = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "class": "border border-solid w-full h-[40px] rounded-lg",
            "placeholder": "Confirm Password",
            "name": "password1"
        }),
        label="Confirm Password",
        required=True
    )
    password           = forms.CharField(widget=forms.PasswordInput(
        attrs={
                "class": "border border-solid w-full h-[40px] rounded-lg",
                "placeholder": "Enter Password",
                "name": "password",
            }),
        label="Password",
        required=True
    )
    
    class Meta:
        model = Account
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password1']
        
        widgets ={
            "email": forms.TextInput(
                attrs={
                    "class": "border border-solid w-full h-[40px] rounded-lg",
                    "placeholder": "Enter email",
                    "name": "email"
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "border border-solid w-full h-[40px] rounded-lg ",
                    "placeholder": "Enter First Name",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "border border-solid w-full h-[40px] rounded-lg",
                    "placeholder": "Enter Username",
                    "name": "username",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "border border-solid w-full h-[40px] rounded-lg",
                    "placeholder": "Enter Last Name",
                }
            )
            
                
        }
    def __init__(self, *args, **kwargs):
        super(RegisterModelForm, self).__init__(*args, **kwargs)
        del self.fields['password2']
        

class EditProfileForm(forms.ModelForm):
    
    class Meta:
        
        model = Account
        fields = ['bio', 'profile_pic', 'banner_pic']
    
    