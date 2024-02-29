from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_manager = models.BooleanField(verbose_name='Manager status', default=False)
    idnumber = models.CharField(verbose_name='ID Number', max_length=30, blank=True, null=True)
    fullname = models.CharField(verbose_name='Full Name', max_length=100, blank=True, null=True)
    postalcode = models.CharField(verbose_name='Postal Code', max_length=10, blank=True, null=True)
    address = models.TextField(verbose_name='Address', blank=True)
    telephone = models.CharField(verbose_name='Telephone Number', max_length=16, blank=True, null=True)
    birthday = models.DateField(verbose_name='Birthday', blank=True, null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
