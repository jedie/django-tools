import logging

from bx_py_utils.test_utils.assertion import pformat_ndiff
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.forms import NumberInput
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from django_tools.model_utils import compare_model_instance


logger = logging.getLogger(__name__)


class VersionFormWidgetInput(NumberInput):
    """
    Display the version and send is via hidden field for comparison.
    """
    template_name = 'model_version_protect/version_widget.html'


class VersionModelField(models.PositiveIntegerField):
    """
    Just change the PositiveIntegerField widget to our own.
    """

    def formfield(self, **kwargs):
        field = super().formfield(**kwargs)
        field.widget = VersionFormWidgetInput()
        return field


class VersionProtectBaseModel(models.Model):
    """
    Add a auto increment "version" number to the model and check it
    to protect overwriting a new version with a older one.

    Raise nice Form errors with diffs (Sadly not for relation fields!)
    """
    version = VersionModelField(
        editable=True,  # Needed to send the current version in admin back!
        null=False, blank=False, default=0,
        help_text=_(
            'Internal version number of this entry.'
            ' Used to protect the overwriting of an older entry.'
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._new_version = None  # Will be set in full_clean() and applied in save()
        self._full_clean_called = False

    def full_clean(self, version_increment=True, **kwargs):
        super().full_clean(**kwargs)

        ModelClass = self.__class__

        if self.version == 0:
            # A new instance has no old version, so we must not check anything ;)
            if version_increment and self._new_version is None:
                self._new_version = 1
                logger.debug(
                    'Create new %s instance with version %s', ModelClass.__name__, self._new_version
                )
        else:
            # Check old version with current one.
            # raise ValidationError if there are not the same.
            logger.debug('%s (pk:%s) version %s', ModelClass.__name__, self.pk, self.version)

            old_instance = ModelClass.objects.only('version').get(pk=self.pk)
            old_version = old_instance.version
            if old_version != self.version:
                logger.error('Old Version: %s is not current version %s', old_version, self.version)

                # Add a generic error message on the top of the form/page:
                errors = {NON_FIELD_ERRORS: _(
                    'Version error:'
                    f' Overwrite version {old_version} with {self.version} is forbidden!'
                )}

                # Add errors to every changed field.
                # FIXME: How to check relations, too?!?
                for model_field, value1, value2 in compare_model_instance(old_instance, self):
                    if model_field == 'version':
                        msg = _('Version changed:')  # The diff contains old/current version ;)
                    else:
                        msg = _(f'changes between version {old_version} and {self.version}:')

                    # Display the changed part of this model field in the form error:
                    diff = escape(pformat_ndiff(value1, value2))
                    errors[model_field] = mark_safe(f'{msg}<pre>{diff}</pre>')

                raise ValidationError(errors)

            if version_increment and self._new_version is None:
                self._new_version = self.version + 1
                logger.debug('Version is incremented to %s.', self._new_version)

        self._full_clean_called = True

    def save(self, auto_full_clean=True, **kwargs):
        if auto_full_clean and not self._full_clean_called:
            # The version will be checks and increment in full_clean()
            # So it's needed to call it on every save, to protect overwriting.
            # Note: Django admin will always call full_clean()
            logger.warning('No full clean called -> Call it from save()!')
            self.full_clean()

        if self._new_version is not None:
            logger.debug('Save and update version from %s to %s', self.version, self._new_version)
            self.version = self._new_version
            self._new_version = None

        if kwargs.get('update_fields'):
            # Save the new version, too ;)
            update_fields = list(kwargs['update_fields'])
            update_fields.append('version')
            kwargs['update_fields'] = update_fields

        super().save(**kwargs)

        # Reset the flag, because you can call save again (e.g.: in tests) ;)
        self._full_clean_called = False

    class Meta:
        abstract = True
