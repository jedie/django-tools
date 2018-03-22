
"""
    django-tools test models
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2012-2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.db import models

from parler.models import TranslatableModel, TranslatedFields

# https://github.com/jedie/django-tools
from django_tools import limit_to_usergroups
from django_tools.parler_utils.parler_fixtures import ParlerDummyGenerator
from django_tools.permissions import ModelPermissionMixin, check_permission


class LimitToUsergroupsTestModel(models.Model):
    permit_edit = limit_to_usergroups.UsergroupsModelField()
    permit_view = limit_to_usergroups.UsergroupsModelField()


class PermissionTestModel(ModelPermissionMixin, models.Model):
    foo = models.CharField(max_length=127)

    @classmethod
    def has_extra_permission_permission(cls, user, raise_exception=True):
        permission = cls.extra_permission_name(action="extra_permission")
        return check_permission(user, permission, raise_exception)

    class Meta:
        # https://docs.djangoproject.com/en/1.8/ref/models/options/#permissions
        permissions = (
            ("extra_permission", "Extra permission"),
        )


#_____________________________________________________________________________
# for django_tools.parler_utils.parler_fixtures.ParlerDummyGenerator


class SimpleParlerModel(TranslatableModel):
    translations = TranslatedFields(
        slug=models.SlugField()
    )


def generate_simple_parler_dummies():
    ParlerDummyGenerator(
        ParlerModelClass=SimpleParlerModel,
        publisher_model=False,
        unique_translation_field="slug"
    ).get_or_create(count=5)



#-----------------------------------------------------------------------------


# TODO:
# class ParlerPublisherModel(PublisherParlerModel):
#     shared = models.CharField(max_length=127)
#     translations = TranslatedFields(
#         foo=models.CharField(max_length=127)
#     )
#
#
# class ParlerPublisherModelFixtures(ParlerDummyGenerator):
#     def get_unique_translation_field_value(self, no, language_code):
#         return "%s %s no.%i" % (self.class_name, language_code, no)
#
#     def add_instance_values(self, instance, language_code, lang_name, no):
#         instance.shared="This is No.%i" % no
#         return instance
#
#
# def generate_parler_publisher_dummies():
#     ParlerPublisherModelFixtures(
#         ParlerModelClass=ParlerPublisherModel,
#         publisher_model=True,
#         unique_translation_field="foo"
#     ).get_or_create(count=3)
