from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.


class Register(AbstractUser):
    phone = models.CharField(max_length=11, unique=True, null=True)
    profile_img = models.ImageField(upload_to="user/images/", null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    facebook_profile = models.URLField(null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.username
