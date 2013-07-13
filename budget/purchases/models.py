"""Models for the main purchases app."""

from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200)


class Purchase(models.Model):
    user = models.ForeignKey(User)
    description = models.CharField(max_length=1000)
    price = models.FloatField()
    timestamp = models.DateField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='purchases')
