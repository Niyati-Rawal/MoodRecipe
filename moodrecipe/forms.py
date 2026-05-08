from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={
        "placeholder": "you@example.com", "class": "field-input",
    }))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "field-input")
        self.fields["username"].widget.attrs["placeholder"] = "choose_a_username"
        self.fields["password1"].widget.attrs["placeholder"] = "password"
        self.fields["password2"].widget.attrs["placeholder"] = "confirm password"


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "field-input", "placeholder": "your_username"})
        self.fields["password"].widget.attrs.update({"class": "field-input", "placeholder": "password"})
