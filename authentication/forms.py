from django import forms

from .models import Register
from django.core.validators import RegexValidator, FileExtensionValidator


class SignupForm(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "First Name", "class": "form-control"}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Last Name", "class": "form-control"}
        )
    )
    email = forms.EmailField(
        max_length=200,
        help_text="Required",
        widget=forms.EmailInput(
            attrs={"placeholder": "Email", "class": "form-control"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm Password", "class": "form-control"}
        ),
        label="confirm password",
        required=True,
        min_length=8,
        # validators=[
        #     # RegexValidator(
        #     #     "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$",
        #     #     message="password too week",
        #     # )
        # ],
    )
    phone = forms.CharField(
        label="phone number",
        validators=[
            RegexValidator(
                "^01[0125][0-9]{8}$", message="Enter a Valid Egyptian Phone Number"
            )
        ],
        widget=forms.TextInput(
            attrs={"placeholder": "Phone Number", "class": "form-control"}
        ),
    )
    profile_img = forms.ImageField(
        label="profile image",
        validators=[FileExtensionValidator(["jpg", "png", "jpeg"])],
        widget=forms.FileInput(
            attrs={"placeholder": "Profile Image", "class": "form-control"}
        ),
        required=True,
    )

    def clean(self):
        errors = {}
        val_password = self.cleaned_data.get("password")
        val_confirm_password = self.cleaned_data.get("confirm_password")
        if val_password != val_confirm_password:
            errors["confirm_password"] = "password not match"
        email = self.cleaned_data.get("email")
        if Register.objects.filter(email=email).exists():
            errors["email"] = "Email exists"
        phone = self.cleaned_data.get("phone")
        if Register.objects.filter(phone=phone).exists():
            errors["phone"] = "phone exists"

        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = Register
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "phone",
            "profile_img",
        )


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=200,
        help_text="Required",
        widget=forms.EmailInput(
            attrs={"placeholder": "Email", "class": "form-control"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )

    def clean(self):
        errors = {}
        email = self.cleaned_data.get("email")
        if not Register.objects.filter(email=email).exists():
            errors["email"] = "Email not exists"
        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = Register
        fields = ("email", "password")
