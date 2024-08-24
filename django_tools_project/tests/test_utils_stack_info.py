import unittest

from django_tools.utils.stack_info import get_stack_info


class TestStackInfo(unittest.TestCase):
    def test_get_stack_info(self):
        stack_info = get_stack_info(filepath_filter='django_tools')

        text_block = '\n'.join(stack_info)

        self.assertIn('File "django_tools_project/tests/test_utils_stack_info.py", line ', text_block)
        self.assertIn('File "django_tools/utils/stack_info.py", line ', text_block)
