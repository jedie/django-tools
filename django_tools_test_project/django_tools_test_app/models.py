# coding: utf-8

"""
    django-tools test models
    ~~~~~~~~~~~~~~~~~~~~~~~~
        
    :copyleft: 2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models
from django_tools import limit_to_usergroups


class LimitToUsergroupsTestModel(models.Model):
    permit_edit = limit_to_usergroups.UsergroupsModelField()
    permit_view = limit_to_usergroups.UsergroupsModelField()