"""Views for the main portion of the site."""

from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import Http404
import datetime
from datetime import date
from datetime import timedelta

from django.contrib.auth.models import User
from purchases.models import UserProfile

from purchases.models import Purchase
from purchases.models import Tag

from purchases.forms import RegistrationForm
from purchases.forms import AddPurchaseForm
from purchases.forms import AddParentTagForm
from purchases.forms import EditPurchaseForm


def index(request):
    if request.user.is_authenticated():
        return redirect("/purchases")
    else:
        return redirect("/login")
        # return render_to_response("index.html", {
        #     'title': "Purchases",
        #     "user": request.user,
        # },
        #     context_instance=RequestContext(request)
        # )


def add(request):
    if request.method == "POST":
        form = AddPurchaseForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            tagstring = form.cleaned_data['tags']
            tags = tagstring.split(",")
            purchase = Purchase(
                description=description,
                price=price,
                user=request.user
            )
            purchase.save()

            try:
                month = form.cleaned_data['month']
                day = form.cleaned_data['day']
                purchase.timestamp = purchase.timestamp.replace(
                    month=month,
                    day=day
                )
                purchase.save()
            except Exception:
                pass
            for tag in tags:
                tag = tag.strip()
                t, created = Tag.objects.get_or_create(name=tag)
                t.save()
                purchase.tags.add(t)
    return redirect("/purchases")


def delete(request, id):
    try:
        purchase = Purchase.objects.get(id=id)
        if purchase.user == request.user:
            purchase.delete()
        else:
            raise Http404
    except Exception:
        pass
    try:
        path = request.GET['path']
    except:
        path = "/purchases"
    return redirect(path)


def sync_tags(request):
    profile = UserProfile.objects.get(user=request.user)
    parent_tags = profile.get_parent_tags()

    for tag in parent_tags:
        tag_object = Tag.objects.get(name=tag)
        purchases = Purchase.objects.filter(
            user=request.user,
            tags__in=[tag_object]
        )
        for purchase in purchases:
            for parent in parent_tags[tag]:
                if not parent in purchase.tags.all():
                    parent_tag = Tag.objects.get(name=parent)
                    purchase.tags.add(parent_tag)

    return redirect("/parents")


def edit(request, id):
    try:
        purchase = Purchase.objects.get(id=id)
        if purchase.user != request.user:
            raise Http404
    except Exception:
        raise Http404

    profile = UserProfile.objects.get(user=request.user)
    parent_tags = profile.parent_tags

    if request.method == "GET":
        form = EditPurchaseForm(initial={
            "description": purchase.description,
            "price": purchase.price,
            "month": purchase.timestamp.month,
            "day": purchase.timestamp.day
        })
    else:
        form = EditPurchaseForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            month = form.cleaned_data['month']
            day = form.cleaned_data['day']
            purchase.description = description
            purchase.price = price
            purchase.timestamp = purchase.timestamp.replace(
                month=month,
                day=day
            )
            purchase.save()

            tagstring = form.cleaned_data['tags']
            tags = tagstring.split(",")
            purchase.tags.clear()
            for tag in tags:
                tag = tag.strip()
                t, created = Tag.objects.get_or_create(name=tag)
                t.save()
                purchase.tags.add(t)

    return render_to_response("edit_purchase.html", {
        'title': "Purchases",
        "user": request.user,
        "form": form,
        "purchase": purchase,
        "parent_tags": parent_tags,
        "purchase_tags": [tag.name for tag in purchase.tags.all()],
    },
        context_instance=RequestContext(request)
    )


def purchases(request):

    def get_date(s):
        """Get a date from the string. Return date"""
        t = [int(x) for x in s.split('/')]
        return date(t[2], t[0], t[1])

    start = end = None
    try:
        tag_filters = request.GET['tags']
        tag_filters = tag_filters.split(",")
        tag_filters = Tag.objects.filter(name__in=tag_filters)
    except Exception:
        tag_filters = []

    purchases = Purchase.objects.filter(
        user=request.user,
    )

    try:
        end = request.GET['end']
        end = get_date(end)
    except Exception:
        end = date.today() + timedelta(days=1)

    try:
        start = request.GET['start']
        start = get_date(start)
    except Exception:
        this_month = end - timedelta(days=1)
        start = datetime.datetime(
            year=this_month.year,
            month=this_month.month,
            day=1
        )

    purchases = purchases.filter(timestamp__range=(start, end))

    ## Fix the end so it shows up correctly in the UI
    end = end - timedelta(days=1)

    form = AddPurchaseForm()

    for tag_filter in tag_filters:
        purchases = purchases.filter(tags__in=[tag_filter])

    purchases = purchases.order_by('-timestamp')

    tags = Tag.tags_for_purchases(purchases)
    for tag in tags:
        setattr(tag, "total", tag.total_across_purchases(purchases))

    tags = sorted(tags, key=lambda tag: tag.total, reverse=True)

    profile = UserProfile.objects.get(user=request.user)
    parent_tags = profile.parent_tags

    return render_to_response("purchases.html", {
        'title': "Purchases",
        "user": request.user,
        "purchases": purchases,
        "form": form,
        "total": Purchase.total(purchases),
        "tags": tags,
        "filters": tag_filters,
        "start": start,
        "end": end,
        "parent_tags": parent_tags,
        "path": request.path,
    },
        context_instance=RequestContext(request)
    )


def parents(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        form = AddParentTagForm(request.POST)
        if form.is_valid():
            tag = form.cleaned_data['tag']
            parent = form.cleaned_data['parent']
            profile.add_parent_tag(tag, parent)
            return redirect("/parents")
    else:
        form = AddParentTagForm()

    parent_tags = profile.get_parent_tags()

    return render_to_response("parents.html", {
        'title': "Tag Family Tree",
        "user": request.user,
        "form": form,
        "parent_tags": parent_tags,
    },
        context_instance=RequestContext(request)
    )


def create_basic_user(form, request):
    ## Get the form data
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']

    MAX_LENGTH = 30
    username = email[:MAX_LENGTH]

    ## Create the User
    user = User.objects.create_user(
        username,  # email is username
        email,
        password
    )
    user.first_name = first_name
    user.last_name = last_name

    user.save()

    profile = UserProfile(user=user)
    profile.save()

    return user, password, profile


def register(request):
    """Registration Page for the site.

    GET: display registration form.
    POST: Handle registration process with form data.

    Returns HttpResponse

    """

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user, password, profile = create_basic_user(form, request)
            return authenticate(request, user.email, password)
    else:
        # setup the redirect url if user attempted to access a page
        # that required login
        if request.user.is_authenticated():
            return redirect("/")
        if 'next' in request.GET:
            request.session['next'] = request.GET['next']
        form = RegistrationForm()

    return render_to_response("register.html", {
        'form': form,
    },
        context_instance=RequestContext(request)
    )


def authenticate(request, email, password):
    """Authenticate a user.

    Parameters
    ----------
    request: HttpRequest
    email: string
    password: string

    Returns HttpResponse

    """

    MAX_LENGTH = 30
    username = email[:MAX_LENGTH]

    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect(
            '/login?msg=username_does_not_exist&start_email=%s' % email
        )

    user = auth.authenticate(username=username, password=password)
    if user is not None:
        if not user.is_active:
            auth.logout(request)
            return redirect('/?msg=notactive')

        auth.login(request, user)

        if 'next' in request.session:
            next = request.session['next']
            del request.session['next']
            return redirect(next)

        return redirect('/')

    else:
        return redirect('/login?msg=bad_pword&start_email=%s' % email)


@login_required
def logout(request):
    """Log the user out.

    Returns HttpResponse

    """

    auth.logout(request)
    return redirect('/')


@csrf_protect
def login(request):
    """Handle login.

    If this is a GET method, return the login form. There
    are possibly some messages to display, those will be given in the msg
    parameter. If we get a start_email parameters, keep the email in the form
    field.

    If it is a POST method, authenticate them.

    Returns HttpResponse

    """

    if request.method == "POST":
        return authenticate(
            request, request.POST['email'],
            request.POST['password']
        )

    MESSAGES = {
        'bad_pword': "The password did not match this email.",
        'notactive': "This account is not active.",
        'username_does_not_exist': "There is no user with this email."
    }

    start_email = None
    if 'start_email' in request.GET:
        start_email = request.GET['start_email']

    msg = None
    if 'msg' in request.GET:
        msg_key = request.GET['msg']
        if msg_key in MESSAGES:
            msg = MESSAGES[msg_key]

    form = RegistrationForm()

    return render_to_response("login.html", {
        'form': form,
        "msg": msg,
        "start_email": start_email,
    },
        context_instance=RequestContext(request)
    )
