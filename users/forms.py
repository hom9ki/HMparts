from django import forms
from django.core.exceptions import ValidationError

from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm


class LoginForm(forms.Form):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(required=False, max_length=30,
                                 widget=forms.TextInput(attrs={
                                     'class': 'form-control',
                                     'placeholder': 'Имя',
                                     'autofocus': 'true'
                                 }))

    last_name = forms.CharField(required=False, max_length=30,
                                widget=forms.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Фамилия'
                                }))
    email = forms.EmailField(required=True, max_length=100,
                             widget=forms.EmailInput(attrs={
                                 'class': 'form-control',
                                 'placeholder': 'Введите email',
                                 'autocomplete': 'email'
                             }))

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите логин'}), }

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean_password2(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают')
        return password2


class ChangePasswordForm(PasswordChangeForm):
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите новый пароль',
        'autocomplete':'new-password'
    }))
    new_password2 = forms.CharField(label='Повторите новый пароль', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Повторите новый пароль',
        'autocomplete': 'new-password'
    }))
    old_password = forms.CharField(label='Введите старый пароль', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите старый пароль',
        'autocomplete': 'current-password'
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите логин',
                'autofocus': 'true'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите email',})
        }
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
        }




