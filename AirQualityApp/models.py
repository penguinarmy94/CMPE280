from django.db import models
import datetime

class User(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    email = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=5)

    def __str__(self):
        return self.email

class AQ(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    city = models.CharField(max_length=300)
    state = models.CharField(max_length=300)
    country = models.CharField(max_length=300)
    zipcode = models.CharField(max_length=5)
    latitude = models.FloatField()
    longitude = models.FloatField()
    pm = models.FloatField()
    ozone = models.FloatField()
    stamp = models.DateField()

    def __str__(self):
        return str(self.pm)

class Zip(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.code


class History(models.Model):
    city = models.CharField(max_length=300)
    state = models.CharField(max_length=300)
    country = models.CharField(max_length=300)
    zipcode = models.CharField(max_length=5, primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    pm = models.FloatField()
    ozone = models.FloatField()
    stamp = models.DateField()

    def __str__(self):
        return str(self.pm)
