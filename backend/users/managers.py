from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if email is None:
            raise ValueError('Users must have an email address!')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        superuser = self.create_user(email, password, **extra_fields)
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save()

        if superuser.is_staff is not True:
            raise ValueError('Superuser must have is_staff=True')

        if superuser.is_superuser is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return superuser
