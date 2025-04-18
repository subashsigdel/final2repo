from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import os


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, user_type=None):
        if not email:
            raise ValueError("Email is required")
        if not user_type:
            raise ValueError("User type is required")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, user_type=user_type)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password, user_type='admin')
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


# Profile Model for Student with Profile Picture
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.name} Profile'

    # Override delete to delete the profile picture file when Profile is deleted
    def delete(self, *args, **kwargs):
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)


# Notes Model
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='notes/')
    date = models.DateTimeField(null= True, blank= True)  # Automatically sets the date when the note is created

    def __str__(self):
        return f'{self.title} - {self.user.email}'

    # Override delete to remove the note file when Note is deleted
    def delete(self, *args, **kwargs):
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

# Question Model
class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    question = models.TextField()
    
    def __str__(self):
        return f'Question by {self.name}'
