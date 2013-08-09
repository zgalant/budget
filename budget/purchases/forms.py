from django import forms
from django.contrib.auth.models import User
import datetime


class RegistrationForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password"
    )
    password_match = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )

    def clean_email(self):
        """
        Custom form validation that verifies the email
        address is unique.
        """
        try:
            User.objects.get(email=self.cleaned_data['email'])
            raise forms.ValidationError(
                "That email address has already been registered!"
            )
        except User.DoesNotExist:
            pass
        return self.cleaned_data['email']

    def clean_password_match(self):
        """
        Custom form validation that verifies the entered passwords
        match.
        """
        try:
            match = self.cleaned_data['password_match']
            password = self.cleaned_data['password']
        except KeyError:
            password = ''
            match = ''

        if password != '' and match != password:
            raise forms.ValidationError("Passwords did not match!")
        return match


class AddPurchaseForm(forms.Form):
    description = forms.CharField()
    price = forms.DecimalField(
        decimal_places=2,
        widget=forms.TextInput(
            attrs={'placeholder': "$"}
        )
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': "Hit Enter or , to save a tag"}
        )
    )
    month = forms.IntegerField(
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': "optional: default is today"}
        )
    )
    day = forms.IntegerField(
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': "optional: default is today"}
        )
    )


class EditPurchaseForm(forms.Form):
    description = forms.CharField()
    price = forms.DecimalField(
        decimal_places=2,
        widget=forms.TextInput(
            attrs={'placeholder': "$"}
        )
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': "Hit Enter or , to save a tag"}
        )
    )
    month = forms.IntegerField()
    day = forms.IntegerField()


class AddParentTagForm(forms.Form):
    tag = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': "Child Tag"}
        )
    )
    parent = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': "Parent Tag"}
        )
    )

    def clean_parent(self):
        tag = self.cleaned_data['tag']
        parent = self.cleaned_data['parent']

        if tag == parent:
            raise forms.ValidationError("Tag Can't Have a Parent Be Itself!")

        return parent
