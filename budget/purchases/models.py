"""Models for the main purchases app."""

from django.db import models
from django.contrib.auth.models import User

import datetime
import json
from jsonfield import JSONField


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    parent_tags = JSONField()

    def get_parent_tags(self):
        parents = json.loads(self.parent_tags)
        return parents

    def is_ancestor(self, tag, ancestor):
        families = self.get_parent_tags()
        if tag in families:
            tag_parents = families[tag]
            if ancestor in tag_parents:
                return True
            for parent in tag_parents:
                if self.is_ancestor(parent, ancestor):
                    return True
        return False

    def get_parents(self, tag):
        """Return list of strings that are parents of the given tag string."""
        families = self.get_parent_tags()
        try:
            return families[tag]
        except Exception:
            return []

    def add_parent_tag(self, tag, parent):
        families = self.get_parent_tags()
        if self.is_ancestor(parent, tag):
            # This means that we'd create a loop
            return
        if tag in families:
            families[tag].append(parent)
        else:
            families[tag] = [parent]
        self.parent_tags = json.dumps(families)
        self.save()


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
    timestamp = models.DateField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='purchases')

    @staticmethod
    def total(purchases):
        sum = 0
        for purchase in purchases:
            sum += purchase.price
        return sum
