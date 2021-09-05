from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


class CustomUser(AbstractUser):
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
                                unique=True,
                                # default='user'+'f{user.id}'
                                )
    bio = models.TextField('О себе',
                           blank=True
                           )
    email = models.EmailField('Адрес электронной почты',
                              unique=True
                              )
    is_staff = models.BooleanField(default=False
                                   )
    created_at = models.DateTimeField(auto_now_add=True
                                      )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
