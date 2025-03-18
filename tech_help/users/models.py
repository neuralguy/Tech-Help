from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(_('biography'), max_length=500, blank=True)
    birth_date = models.DateField(_('birth date'), null=True, blank=True)
    
    # Делаем email обязательным полем
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
