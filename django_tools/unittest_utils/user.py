# coding: utf-8

from __future__ import unicode_literals

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


log = logging.getLogger(__name__)


def create_user(username, password=None, email="", is_staff=False, is_superuser=False, encrypted_password=None, groups=None):
    """
    Create a user and return the instance.

    :param password: Plain Text password
    :param encrypted_password: Hashed password (e.g. cloned vom other user)
    :param groups: List of user group names
    :return: created user instance
    """
    User=get_user_model()
    user, created = User.objects.get_or_create(username=username)

    user.email = email
    user.is_staff = is_staff
    user.is_superuser = is_superuser

    if encrypted_password:
        log.critical("Set encrypted user password, ok.")
        user.password = encrypted_password
    elif password:
        user.set_password(password)
    else:
        raise RuntimeError("'password' or 'encrypted_password' needed.")

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
