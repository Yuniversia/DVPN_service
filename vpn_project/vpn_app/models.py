# vpn_app/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid
from datetime import timedelta

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        
        # Генерируем уникальный peer_id при создании пользователя
        user.peer_id = uuid.uuid4().hex
        
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class Group(models.Model):
    name = models.CharField(max_length=150, unique=True)
    ip_address = models.CharField(max_length=39, null=True, blank=True) # e.g., "10.0.0.1/24"
    creator = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, related_name='created_groups')
    group_admins = models.ManyToManyField('CustomUser', related_name='admin_groups', blank=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    current_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    group_ip = models.CharField(max_length=15, null=True, blank=True) # e.g., "10.0.0.2"
    peer_id = models.CharField(max_length=32, unique=True, blank=True) # Храним как hex

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def save(self, *args, **kwargs):
        if not self.peer_id:
            self.peer_id = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Link(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    expires_in_hours = models.PositiveIntegerField(null=True, blank=True) # Длительность в часах
    expiration_time = models.DateTimeField(null=True, blank=True) # Рассчитанное время
    is_admin_link = models.BooleanField(default=False)
    link_code = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    max_uses = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Рассчитываем expiration_time при сохранении, если задано expires_in_hours
        if self.expires_in_hours and not self.expiration_time:
            self.expiration_time = timezone.now() + timedelta(hours=self.expires_in_hours)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Link for {self.group.name} by {self.author.username}"

class Peer_link(models.Model):
    link = models.CharField(max_length=15, unique=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f"Peer link {self.link} for {self.group.name}"