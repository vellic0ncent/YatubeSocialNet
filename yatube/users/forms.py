from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, CharField, PasswordInput
from django.contrib.auth import get_user_model
from .models import PasswordChange


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ChangePasswordForm(ModelForm):
    old_password = CharField(widget=PasswordInput)
    new_password1 = CharField(widget=PasswordInput)
    new_password2 = CharField(widget=PasswordInput)

    class Meta:
        model = PasswordChange
        fields = '__all__'
