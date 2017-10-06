# coding: utf-8

from __future__ import unicode_literals

import logging

import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

log = logging.getLogger(__name__)


def create_user(
    username, password=None, email="",
    is_staff=False, is_superuser=False,
    encrypted_password=None, groups=None,
    update_existing=False
    ):
    """
    Create a user and return the instance.

    :param password: Plain Text password
    :param encrypted_password: Hashed password (e.g. cloned vom other user)
    :param groups: List of user group names
    :return: created user instance
    """
    if password is None and encrypted_password is None:
        raise RuntimeError("'password' or 'encrypted_password' needed.")

    User=get_user_model()

    user = None
    if update_existing:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        else:
            created=False

    if user is None:
        # Create user with origin form to validate username:
        user_form_data={
            "username": username,
            "password1": password,
            "password2": password,
        }

        if password is None:
            # encrypted_password set later!
            # Set something, to run validation.
            user_form_data["password1"] = user_form_data["password2"] = "A temp password!"

        user_form = UserCreationForm(user_form_data)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            created = True
        else:
            raise ValidationError("%s" % user_form.errors)

    user.email = email
    user.is_staff = is_staff
    user.is_superuser = is_superuser

    if encrypted_password:
        log.critical("Set encrypted user password, ok.")
        user.password = encrypted_password
    elif password:
        user.set_password(password)
    else:
        raise RuntimeError # should never happen, see above ;)

    user.save()

    if groups:
        for group_name in groups:
            try:
                user_group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                raise RuntimeError('User group "%s" not found!' % group_name)
            user.groups.add(user_group)

    if created:
        log.debug("Create new user %r account" % user)
    else:
        log.debug("Update existing %r account" % user)

    return user


def get_super_user():
    """
    :return: the first 'superuser'
    """
    User=get_user_model()
    try:
        super_user = User.objects.filter(is_superuser=True)[0]
    except (User.DoesNotExist, IndexError):
        log.error("Can't get a superuser. Please create first!")
        raise RuntimeError("No superuser")
    return super_user


TEST_USERS = {
    "superuser": {
        "username": "superuser",
        "email": "superuser@example.org",
        "password": "superuser_password",
        "is_staff": True,
        "is_superuser": True,
    },
    "staff": {
        "username": "staff_test_user",
        "email": "staff_test_user@example.org",
        "password": "staff_test_user_password",
        "is_staff": True,
        "is_superuser": False,
    },
    "normal": {
        "username": "normal_test_user",
        "email": "normal_test_user@example.org",
        "password": "normal_test_user_password",
        "is_staff": False,
        "is_superuser": False,
    },
}

@pytest.fixture(scope="session")
def user_fixtures():
    for user_data in TEST_USERS.values():
        create_user(update_existing=True, **user_data)
