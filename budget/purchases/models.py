"""Models for the main purchases app."""

from django.db import models
from django.contrib.auth.models import User

import datetime
from jsonfield import JSONField


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    parent_tags = JSONField()


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
    def purchases(user, month=None, year=None):
        """Return purchases for the given timeframe.

        Returns one month's worth of purchases given the start date.

        """
        now = datetime.datetime.now()
        month = month if month is not None else now.month
        year = year if year is not None else now.year
        next_month = month + 1 if month != 12 else 1
        next_year = year if month != 12 else year + 1

        month_start = datetime.datetime(
            year=year,
            month=month,
            day=1
        )
        month_end = datetime.datetime(
            year=next_year,
            month=next_month,
            day=1
        )
        purchases = Purchase.objects.filter(
            user=user,
            timestamp__gte=month_start,
            timestamp__lt=month_end
        )
        return purchases

    @staticmethod
    def total(purchases):
        sum = 0
        for purchase in purchases:
            sum += purchase.price
        return sum
