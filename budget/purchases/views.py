"""Views for the main portion of the site."""

from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User

from purchases.forms import RegistrationForm


def index(request):
    return render_to_response("index.html", {
        'title': "Purchases",
        "user": request.user
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

    return user, password


def register(request):
    """Registration Page for the site.

    GET: display registration form.
    POST: Handle registration process with form data.

    Returns HttpResponse

    """

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user, password = create_basic_user(form, request)
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

        return redirect('/')  # go to karel section

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
