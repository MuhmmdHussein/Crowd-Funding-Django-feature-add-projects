from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django import forms
from authentication.models import Register


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control",
            }
        ),
        min_length=2,
        max_length=10,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Last Name", "class": "form-control"}
        ),
        min_length=2,
        max_length=10,
    )
    phone = forms.CharField(
        label="phone number",
        validators=[
            RegexValidator(
                "^01[0125][0-9]{8}$", message="Enter a Valid Egyption Phone Number"
            )
        ],
        widget=forms.TextInput(
            attrs={"placeholder": "Phone Number", "class": "form-control"}
        ),
    )
    image = forms.ImageField(
        required=False,
        label="profile image",
        validators=[FileExtensionValidator(["jpg", "png", "jpeg"])],
        widget=forms.FileInput(
            attrs={"placeholder": "Profile Image", "class": "form-control"}
        ),
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        ),
    )
    # TODO:add regex to password
    confirm_password = forms.CharField(
        required=False,
        label="confirm password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm Password", "class": "form-control"}
        ),
    )
    country = forms.CharField(
        required=False,
        validators=[
            RegexValidator("^[A-Za-z]+$", message="Enter a Valid Country Name")
        ],
        widget=forms.TextInput(
            attrs={"placeholder": "Country", "class": "form-control"}
        ),
    )
    birthdate = forms.DateField(
        required=False,
        widget=forms.NumberInput(
            attrs={"placeholder": "BirthDate", "type": "date", "class": "form-control"}
        ),
    )
    facebook_profile = forms.URLField(
        required=False,
        error_messages={"required": "Please Enter a valid Url"},
        widget=forms.URLInput(
            attrs={"placeholder": "Profile Facebook Url", "class": "form-control"}
        ),
    )

    def clean(self):
        errors = {}
        cleaned_data = super().clean()
        valpassword = self.cleaned_data.get("password")
        valconfirm_password = self.cleaned_data.get("confirm_password")
        if valpassword != valconfirm_password:
            errors["confirm_password"] = "password not match"
        phone = self.cleaned_data.get("phone")
        if Register.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            errors["phone"] = "phone exists"

        if errors:
            raise forms.ValidationError(errors)

    class Meta:
        model = Register
        fields = (
            "first_name",
            "last_name",
            "phone",
            "image",
            "country",
            "password",
            "confirm_password",
            "birthdate",
            "facebook_profile",
        )
