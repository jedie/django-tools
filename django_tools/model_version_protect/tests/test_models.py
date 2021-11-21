import logging
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from model_bakery import baker

from django_tools.model_version_protect.tests.utils import shorten_logs
from django_tools_test_project.django_tools_test_app.models import VersioningTestModel


class ModelVersionProtectTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(get_user_model())

    def test_version_increment(self):
        instance = VersioningTestModel(
            id=1,
            user=self.user,
            name='foo'
        )
        assert instance.version == 0  # initial value!

        # Nothing saved, yet:
        assert list(VersioningTestModel.objects.values('version',)) == []

        with self.assertLogs('django_tools', level=logging.DEBUG) as logs:
            instance.save()
        logs = shorten_logs(logs.output)
        assert logs == [
            'WARNING: No full clean called -> Call it from save()!',
            'DEBUG: Create new VersioningTestModel instance with version 1',
            'DEBUG: Save and update version from 0 to 1'
        ]
        assert instance.version == 1

        # Check DB:
        assert list(VersioningTestModel.objects.values('version',)) == [{'version': 1}]

        # After save() call, we increment in full_clean(), but it's still the old version:
        with self.assertLogs('django_tools', level=logging.DEBUG) as logs:
            instance.full_clean()
        logs = shorten_logs(logs.output)
        assert logs == [
            'DEBUG: VersioningTestModel (pk:1) version 1',
            'DEBUG: Version is incremented to 2.'
        ]
        assert instance.version == 1
        assert instance._new_version == 2

        # full_clean() increment only one time:
        with self.assertLogs('django_tools', level=logging.DEBUG) as logs:
            instance.full_clean()
        logs = shorten_logs(logs.output)
        assert logs == [
            'DEBUG: VersioningTestModel (pk:1) version 1'
        ]
        assert instance.version == 1
        assert instance._new_version == 2

        # Before save: Get the current version, used below to test overwriting:
        old_version = VersioningTestModel.objects.first()
        assert old_version.version == 1
        assert old_version._new_version is None  # full_clean() not called, yet

        # Now save the new version:
        with self.assertLogs('django_tools', level=logging.DEBUG) as logs:
            instance.save()
        logs = shorten_logs(logs.output)
        assert logs == [
            'DEBUG: Save and update version from 1 to 2'
        ]
        assert instance.version == 2  # New version!
        assert instance._new_version is None  # reset to None by save()

        # Try to overwrite with old version:

        with self.assertLogs('django_tools', level=logging.DEBUG) as logs, \
                self.assertRaises(ValidationError) as cm:
            old_version.full_clean()
        logs = shorten_logs(logs.output)
        assert logs == [
            'DEBUG: VersioningTestModel (pk:1) version 1',
            'ERROR: Old Version: 2 is not current version 1'
        ]
        error_dict = cm.exception.message_dict
        assert error_dict == {
            '__all__': ['Version error: Overwrite version 2 with 1 is forbidden!'],
            'version': ['Version changed:<pre>- 2\n+ 1</pre>']
        }
        # Never increment on ValidationError, so it's stays to v2:
        assert instance.version == 2

    def test_auto_call_full_clean(self):
        with self.assertLogs('django_tools', level=logging.DEBUG) as logs:
            instance = VersioningTestModel.objects.create(
                id=1,
                user=self.user,
                name='foo'
            )
        logs = shorten_logs(logs.output)
        assert logs == [
            'WARNING: No full clean called -> Call it from save()!',
            'DEBUG: Create new VersioningTestModel instance with version 1',
            'DEBUG: Save and update version from 0 to 1',
        ]
        assert instance.version == 1

        with self.assertLogs('django_tools', level=logging.DEBUG) as logs:
            instance.save()
        logs = shorten_logs(logs.output)
        assert logs == [
            'WARNING: No full clean called -> Call it from save()!',
            'DEBUG: VersioningTestModel (pk:1) version 1',
            'DEBUG: Version is incremented to 2.',
            'DEBUG: Save and update version from 1 to 2'
        ]
        assert instance.version == 2

        with self.assertLogs('django_tools', level=logging.DEBUG) as logs:
            instance.full_clean()
            instance.save()
        logs = shorten_logs(logs.output)
        assert logs == [
            'DEBUG: VersioningTestModel (pk:1) version 2',
            'DEBUG: Version is incremented to 3.',
            'DEBUG: Save and update version from 2 to 3'
        ]
        assert instance.version == 3

    def test_protect_overwrite(self):
        with self.assertLogs('django_tools'):
            VersioningTestModel.objects.create(
                pk=UUID('00000000-0000-0000-1111-000000000001'),
                user=self.user,
                name='The Name 1'
            )

        assert list(VersioningTestModel.objects.values('version', 'name')) == [
            {'name': 'The Name 1', 'version': 1}
        ]

        instance1 = VersioningTestModel.objects.first()
        assert instance1.version == 1
        instance2 = VersioningTestModel.objects.first()
        assert instance2.version == 1

        with self.assertLogs('django_tools'):
            instance1.name = 'The New Name'
            instance1.save()

        assert list(VersioningTestModel.objects.values('version', 'name')) == [
            {'name': 'The New Name', 'version': 2}
        ]

        with self.assertLogs('django_tools'):
            instance2.name = 'Other Name'
            with self.assertRaises(ValidationError) as cm:
                assert instance2.version == 1
                instance2.full_clean()

            assert instance2.version == 1  # not increment in full_clean() !

            error_dict = cm.exception.message_dict
            assert error_dict['__all__'] == [
                'Version error: Overwrite version 2 with 1 is forbidden!'
            ]
            assert error_dict['name'] == [
                'changes between version 2 and 1:'
                '<pre>'
                '- &quot;The New Name&quot;\n'
                '+ &quot;Other Name&quot;'
                '</pre>'
            ]
