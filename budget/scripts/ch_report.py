from django.contrib.auth.models import User
from purchases.models import Purchase
from purchases.models import Tag

import datetime


def get_date(date_str):
    date_str = date_str.replace("\"", "")
    parts = date_str.split("/")
    month = int(parts[0])
    day = int(parts[1])
    year = int(parts[2])
    d = datetime.date(month=month, day=day, year=year)
    return d


def get_entered_tags(user):
    """Return list of tags entered by the user."""
    tags = []
    print "Enter tags:"
    tag = raw_input()
    while tag != "":
        tags.append(tag)
        parents = user.userprofile.get_parents(tag)
        for parent in parents:
            print parent
            tags.append(parent)
        tag = raw_input()
    return tags


def should_save_purchase():
    """Ask whether we should save the purchase. Return boolean."""
    print "Save purchase? (y/n)"
    answer = raw_input()
    return "y" in answer.lower()


def run(*script_args):
    user = User.objects.get(username="zg")
    filename = script_args[0]
    f = open(filename)
    lines = f.readlines()
    f.close()
    lines = lines[1:]
    for line in lines:
        purchase = line.split(",")
        dt = get_date(purchase[1])
        description = purchase[3].replace("\"", "")
        price = -   float(purchase[4])
        p = Purchase(
            description=description,
            price=price,
            user=user
        )
        print p.description, p.price, dt
        if should_save_purchase():
            p.save()
            p.timestamp = dt
            p.save()
            tags = get_entered_tags(user)
            for tag in tags:
                t, created = Tag.objects.get_or_create(name=tag)
                t.save()
                p.tags.add(t)
