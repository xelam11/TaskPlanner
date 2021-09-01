from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager

# ROLE_CHOICES = {
#     'user': 'user',
#     'admin': 'admin',
# }


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField('Имя',
                                  max_length=30,
                                  blank=True
                                  )
    last_name = models.CharField('Фамилия',
                                 max_length=30,
                                 blank=True
                                 )
    username = models.CharField('Username',
                                max_length=30,
                                unique=True
                                )
    bio = models.TextField('О себе',
                           blank=True
                           )
    email = models.EmailField('Адрес электронной почты',
                              unique=True
                              )
    # role = models.CharField('Роль пользователя',
    #                         max_length=30,
    #                         choices=ROLE_CHOICES,
    #                         default=ROLE_CHOICES['user']
    #                         )
    is_active = models.BooleanField(default=True
                                    )
    is_staff = models.BooleanField(default=False
                                   )
    created_at = models.DateTimeField(auto_now_add=True
                                      )
    updated_at = models.DateTimeField(auto_now=True
                                      )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
