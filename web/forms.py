from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

from accounts.models import Profile, User


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'autofocus': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Email"


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, validators=[validate_password], )

    class Meta:
        model = User
        fields = [
            'email',
        ]

    def save(self, commit=True):
        email = self.cleaned_data['email']
        base = email.split('@')[0][:140]
        username, i = base, 1

        while User.objects.filter(username=username).exists():
            i += 1
            username = f'{base}{i}'
        return User.objects.create_user(
            username=username,
            email=email,
            password=self.cleaned_data['password']
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'gender', 'weight', 'height', 'birth_date', 'activity', 'goal']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}
