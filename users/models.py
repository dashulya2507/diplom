from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    TYPE_CHOICES = [('shop', 'Магазин'), ('buyer', 'Покупатель')]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='buyer')
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    def __str__(self):
        return self.email


class ConfirmEmailToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='confirm_email_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=64, unique=True, db_index=True)

    def __str__(self):
        return f'Email confirmation for {self.user.email}'
