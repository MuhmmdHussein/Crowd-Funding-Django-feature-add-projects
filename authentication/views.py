from datetime import timezone, datetime
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator

from authentication.forms import LoginForm, SignupForm
from authentication.models import Register
from core import settings


# Create your views here.


def auth_login(request):
    if "user_id" not in request.session:
        msg = None
        if request.method == "POST":
            form = LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                password = form.cleaned_data["password"]
                try:
                    user = Register.objects.get(email=email)
                except ObjectDoesNotExist:
                    user = None
                if user is not None and check_password(password, user.password):
                    if user.is_active:
                        user.last_login = datetime.now()
                        user.is_login = True
                        user.save()
                        login(request, user)
                        request.session["user_id"] = user.id
                        msg = f"You are now logged in as {user.first_name}"
                        return redirect("/")
                    else:
                        msg = "please check your email to activate it!"
                else:
                    msg = "user doesn't exist "
            else:
                if form.errors:
                    msg = ""
                    for key, value in form.errors.items():
                        msg += str(value) + "\n"
                else:
                    msg = "Invalid email or password."

        form = LoginForm()
        return render(
            request=request,
            template_name="auth/login.html",
            context={"login_form": form, "msg": msg},
        )
    else:
        return redirect("/")


def auth_signup(request):
    msg = None
    if "user_id" not in request.session:
        if request.method == "POST":
            form = SignupForm(request.POST, files=request.FILES)
            if form.is_valid():
                hashed_password = make_password(form.cleaned_data["password"])
                check = check_password(form.cleaned_data["password"], hashed_password)
                print(check)
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]
                email = form.cleaned_data["email"]
                password = hashed_password
                phone = form.cleaned_data["phone"]
                image = form.cleaned_data["profile_img"]

                print(first_name, last_name, email, password, phone, image)

                user = Register.objects.create(
                    username=email,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                    phone=phone,
                    profile_img=image,
                )
                user.is_active = False
                user.save()
                send_activation_email(user, request)
                msg = "Please confirm your email address to complete the registration"

            else:
                if form.errors:
                    msg = ""
                    for key, value in form.errors.items():
                        msg += str(value) + "\n"
                else:
                    msg = "User already exists"
        else:
            form = SignupForm()
        return render(request, "auth/signup.html", {"signup_form": form, "msg": msg})
    else:
        return redirect("/")


def activate(request, uidb64, token):
    print(f"UIDB64: {uidb64}")
    print(f"Token: {token}")
    uid = force_str(urlsafe_base64_decode(uidb64))
    print(f"UID: {uid}")
    print(Register.objects.get(pk=uid))
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Register.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None

    print(user)
    print(default_token_generator.check_token(user, token))

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("login")
    else:
        return HttpResponse("Activation link is invalid!")


def send_activation_email(user, request):
    token = account_activation_token.make_token(user)
    current_site = get_current_site(request)
    mail_subject = 'Activate your account'
    message = render_to_string('auth/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token,

    })
    email = EmailMessage(subject=mail_subject, body=message, from_email=settings.EMAIL_HOST_USER, to=[user.email])
    email.send()

def logout(request):
    try:
        del request.session['user_id']
    except KeyError:
        print("you must login")
    return redirect("login")
