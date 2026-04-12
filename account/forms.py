from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field
class RegistrationForm(forms.ModelForm):
    password=forms.CharField(label='Password',widget=forms.PasswordInput(attrs={
        'class': 'appearance-none block w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none', 'placeholder': '••••••••'
    }))    
    confirm_password=forms.CharField(label='Confirm password',widget=forms.PasswordInput(attrs={
        'class': 'appearance-none block w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none', 'placeholder': '••••••••'
    }))

    class Meta:
        model=User
        fields=['username','email','first_name','last_name']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'appearance-none block w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none', 'placeholder': 'user name'}),
            'first_name': forms.TextInput(attrs={'class': 'appearance-none block w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none', 'placeholder': 'first name'}),
            'last_name': forms.TextInput(attrs={'class': 'appearance-none block w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none', 'placeholder': 'last name'}),
            'email': forms.EmailInput(attrs={'class': 'appearance-none block w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none', 'placeholder': 'mail'}),
        }

        def clean_email(self):
            email = self.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                raise ValidationError("Email already used")
            return email
        
        def clean_confirm_message(self):
            cd=self.cleaned_data
            if cd['password']==cd['confirm_password']:
                return cd['confirm_password']
            else:
                raise forms.ValidationError('Password do not match')

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field('username', placeholder="Username", css_class="mb-0"), css_class='form-group col-md-6 mb-0'),
                Column(Field('first_name', placeholder="First Name"), css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column(Field('last_name', placeholder="Last Name"), css_class='form-group col-md-6 mb-0'),
                Column(Field('email', placeholder="Email"), css_class='form-group col-md-6 mb-0'),
            ),
        )
       
        self.fields['username'].help_text = None

    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.exclude(
        id=self.instance.id
        ).filter(
        email=data
        )
        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avater', 'dob','mob','gender']
        widgets = {
            'dob': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'w-full px-5 py-3.5 bg-gray-50 border border-gray-100 rounded-2xl focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all outline-none font-medium text-gray-700',
                }
            ),
            'avater': forms.FileInput(
                attrs={
                    'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-bold file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100 transition-all cursor-pointer',
                }
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('avater', css_class="file-input-style")
        )

class ChangePaswordForm(forms.Form):
    prev_pass=forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class':'form-control passfield',
            'placeholder':'Enter current password'
        })
    )
    pass1=forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(
            attrs={
                'class':'form-control passfield',
                'placeholder':'Enter new password'
            }
        )
    )
    pass2=forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class':'form-control passfield',
            'placeholder':'Enter confirm password'
        })
    )

    def clean(self):
        cleaned_data=super().clean()
        pass1=cleaned_data.get('pass1')
        pass2=cleaned_data.get('pass2')

        if pass1 and pass2 and pass1!=pass2:
            raise forms.ValidationError('Password not match')
        return cleaned_data
