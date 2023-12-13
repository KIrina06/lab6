from datetime import datetime

from django.contrib.auth.models import User, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone

from painting.utils.utils import format_time

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_moderator', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Custom fields
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=30)
    is_moderator = models.BooleanField(default=False)

    # Necessary fields for django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Expertises(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    expertise_id = models.AutoField(primary_key=True)
    picture = models.CharField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=70, unique=True)
    price = models.CharField(blank=True, null=True)
    context = models.CharField(blank=True, null=True)
    expertise_status = models.IntegerField(choices=STATUS_CHOICES, default=1)

class Requests(models.Model):
    STATUS_CHOICES = (
        (1, 'Черновик'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален'),
    )

    request_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    expertises = models.ManyToManyField(Expertises)
    closed_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    formated_date = models.DateTimeField(blank=True, null=True)
    req_status = models.IntegerField(choices=STATUS_CHOICES, default=1)  # This field type is a guess.
    moder_id = models.IntegerField(blank=True, null=True)


class ReqExps(models.Model):
    re_id = models.BigAutoField(primary_key=True)
    expertise = models.ForeignKey('Expertises', models.DO_NOTHING)
    request = models.ForeignKey('Requests', models.DO_NOTHING)

    class Meta:
        unique_together = (('expertise', 'request'),)
