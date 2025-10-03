from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import customBaseManager

# Create your models here.
class signupModel(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = customBaseManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name_plural = "Users"
        db_table = 'users'

    def __str__(self) -> str:
        return self.email