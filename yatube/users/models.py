from django.db import models
from django.core.validators import MinLengthValidator


class PasswordChange(models.Model):
    old_password = models.CharField(max_length=50)
    new_password1 = models.CharField(max_length=100)
    new_password2 = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(8)]
    )
