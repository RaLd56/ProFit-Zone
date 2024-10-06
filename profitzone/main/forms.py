from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Форма для входа
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', max_length=100)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

# Форма для регистрации
class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)
    username = forms.CharField(label='Имя пользователя')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
