from bx_py_utils.test_utils.unittest_utils import BaseDocTests

import django_tools
import django_tools_project


class DocTests(BaseDocTests):
    def test_doctests(self):
        self.run_doctests(
            modules=(django_tools, django_tools_project),
        )
