from django.contrib.auth.models import User
from purchases.models import Purchase
from purchases.models import Tag

import datetime
from datetime import date


def get_date(date_str):
    date_str = date_str.replace("\"", "")
    parts = date_str.split("/")
    month = int(parts[0])
    day = int(parts[1])
    year = int(parts[2])
    d = datetime.date(month=month, day=day, year=year)
    return d


def run(*script_args):
    user = User.objects.get(username="zg")
    filename = script_args[0]
    f = open(filename)
    lines = f.readlines()
    f.close()
    lines = lines[3:]
    for line in lines:
        purchase = line.split(",")
        dt = get_date(purchase[0])
        description = purchase[1].replace("\"", "")
        price = float(purchase[2][1:])
        tags = purchase[3:]
        p = Purchase(
            description=description,
            price=price,
            user=user
        )
        p.timestamp = dt
        p.save()
        print price
        for tag in tags:
            tag = tag.replace("\r\n", "").replace("\"", "")
            tag = tag.strip()
            print tag
            t, created = Tag.objects.get_or_create(name=tag)
            t.save()
            p.tags.add(t)
        print ""
