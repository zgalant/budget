"""Models for the main purchases app."""

from django.db import models
from django.contrib.auth.models import User
import datetime


class Tag(models.Model):
    name = models.CharField(max_length=200)

    @staticmethod
    def tags_for_purchases(purchases):
        all_tags = []
        for purchase in purchases:
            all_tags.extend(purchase.tags.all())
        all_tags = list(set(all_tags))
        return all_tags

    def total_across_purchases(self, purchases):
        purchases = purchases.filter(tags__in=[self])
        return Purchase.total(purchases)


class Purchase(models.Model):
    user = models.ForeignKey(User)
    description = models.CharField(max_length=1000)
    price = models.FloatField()
    timestamp = models.DateField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='purchases')

    @staticmethod
    def purchases_this_month(user):
        now = datetime.datetime.now()
        month_start = datetime.datetime(
            year=now.year,
            month=now.month,
            day=1
        )
        purchases = Purchase.objects.filter(
            user=user,
            timestamp__gte=month_start
        )
        return purchases

    @staticmethod
    def total(purchases):
        sum = 0
        for purchase in purchases:
            sum += purchase.price
        return sum
