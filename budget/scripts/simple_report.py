from django.contrib.auth.models import User
from purchases.models import Purchase
from purchases.models import Tag

import datetime
from datetime import date


def get_date(date_str):
    date_str = date_str.replace("\"", "")
    parts = date_str.split("/")
    month = int(parts[1])
    day = int(parts[2])
    year = int(parts[0])
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
        description = purchase[7]
        price = float(purchase[3][1:])
        tags = purchase[8:9]
        p = Purchase(
            description=description,
            price=price,
            user=user
        )
        p.save()
        p.timestamp = dt
        p.save()
        print dt
        print description
        print price
        if "Philz" in description:
            tags.append("philz")
            tags.append("coffee")
            tags.append("drinks")
        for tag in tags:
            tag = tag.replace("\r\n", "").replace("\"", "")
            tag = tag.strip()
            if tag == "Uncategorized":
                continue
            if tag == "Food & Drink":
                tag = "food"
            print tag
            t, created = Tag.objects.get_or_create(name=tag)
            t.save()
            p.tags.add(t)
        print ""
