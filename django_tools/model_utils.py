# coding: utf-8

"""
    models utils
    ~~~~~~~~~~~~

    :copyleft: 2009-2012 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function



from django.conf import settings
from django.db.models import signals
from django.utils.text import get_text_list
from django.db import connection, IntegrityError
from django.utils.translation import ugettext as _
from django.db.models.fields import FieldDoesNotExist


def check_unique_together(sender, **kwargs):
    """
    Check models unique_together manually. Because Django will only
    enforced unique together at database level with UNIQUE, but
    some databases (e.g. SQLite) doesn't support this.
    
    NOTE: SQLite supports UNIQUE since 2.0 (from 2001) !
    
    usage:
        from django.db.models import signals
        from django_tools.model_utils import check_unique_together
        signals.pre_save.connect(check_unique_together, sender=MyModelClass)
        
    or use:
        from django_tools.model_utils import auto_add_check_unique_together
        auto_add_check_unique_together(MyModelClass)
        
    This will add the signal only if a Database doesn't support UNIQUE, see below.
    """
    instance = kwargs["instance"]
    for field_names in sender._meta.unique_together:
        model_kwargs = {}
        for field_name in field_names:
            try:
                data = getattr(instance, field_name)
            except FieldDoesNotExist:
                # e.g.: a missing field, which is however necessary.
                # The real exception on model creation should be raised. 
                continue
            model_kwargs[field_name] = data

        query_set = sender.objects.filter(**model_kwargs)
        if instance.pk != None:
            # Exclude the instance if it was saved in the past
            query_set = query_set.exclude(pk=instance.pk)

        count = query_set.count()
        if count > 0:
            field_names = get_text_list(field_names, _('and'))
            msg = _("%(model_name)s with this %(field_names)s already exists.") % {
                'model_name': str(instance.__class__.__name__),
                'field_names': str(field_names)
            }
            raise IntegrityError(msg)


def auto_add_check_unique_together(model_class):
    """
    Add only the signal handler check_unique_together, if a database without UNIQUE support is used.
    
    NOTE: SQLite supports UNIQUE since 2.0 (from 2001) !
    """
    try:
        # new setting scheme
        engine = settings.DATABASES["default"]["ENGINE"]
    except AttributeError:
        # fall back to old scheme
        engine = settings.DATABASE_ENGINE

    if "sqlite3" in engine: # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
        signals.pre_save.connect(check_unique_together, sender=model_class)
