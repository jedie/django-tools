# coding: utf-8
"""
    models utils
    ~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.db.models import signals
from django.utils.text import get_text_list
from django.db import connection, IntegrityError
from django.utils.translation import ugettext as _
from django.db.models.fields import FieldDoesNotExist

def check_unique_together(sender, **kwargs):
    """
    Check models unique_together manually. Django enforced unique together only the database level, but
    some databases (e.g. SQLite) doesn't support this.
    
    usage:
        from django.db.models import signals
        signals.pre_save.connect(check_unique_together, sender=MyModelClass)
        
    or use auto_add_check_unique_together(), see below.
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
            msg = _(u"%(model_name)s with this %(field_names)s already exists.") % {
                'model_name': unicode(instance.__class__.__name__),
                'field_names': unicode(field_names)
            }
            raise IntegrityError(msg)

def auto_add_check_unique_together(model_class):
    """
    Add only the signal handler check_unique_together, if a database without UNIQUE support is used.
    """
    if settings.DATABASE_ENGINE in ('sqlite3',): # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
        signals.pre_save.connect(check_unique_together, sender=model_class)
