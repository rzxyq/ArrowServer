from django.db import models

# Create your models here.
class User(models.Model):
    num = models.CharField(max_length=15)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=30)
    date = models.DateTimeField(auto_now_add=True)