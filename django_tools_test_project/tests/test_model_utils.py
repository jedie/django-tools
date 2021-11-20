from uuid import UUID

from django.test import TestCase

from django_tools.model_utils import compare_model_instance, serialize_instance
from django_tools.unittest_utils.assertments import assert_pformat_equal
from django_tools_test_project.django_tools_test_app.models import VersioningTestModel


class ModelUtilsTestCase(TestCase):
    def test_serialize_instance(self):
        instance = VersioningTestModel(
            pk=UUID('00000000-0000-0000-1111-000000000001'),
            name='Foo Bar'
        )
        result = serialize_instance(instance)
        assert_pformat_equal(result, {'name': 'Foo Bar', 'user': None, 'version': 0})

    def test_compare_model_instance(self):
        instance1 = VersioningTestModel(
            pk=UUID('00000000-0000-0000-1111-000000000001'),
            name='Instance One Name'
        )
        instance2 = VersioningTestModel(
            pk=UUID('00000000-0000-0000-1111-000000000001'),
            name='Instance Two Name'
        )
        result = list(compare_model_instance(instance1, instance2))
        assert_pformat_equal(result, [('name', 'Instance One Name', 'Instance Two Name')])
