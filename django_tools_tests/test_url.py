import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.utils import six
from django.test.utils import override_settings

import django_tools
from django_tools.validators import URLValidator2, ExistingDirValidator


@override_settings(DEBUG=False)
class TestExistingDirValidator(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestExistingDirValidator, cls).setUpClass()
        cls.media_root_validator = ExistingDirValidator()

    def test_default_media_root(self):
        self.media_root_validator(settings.MEDIA_ROOT)
        try:
            self.media_root_validator("does/not/exist")
        except ValidationError as err:
            self.assertEqual(six.text_type(err.message), "Directory doesn't exist!")

    @override_settings(DEBUG=True)
    def test_debug_message(self):
        path = os.path.abspath("does/not/exist")
        try:
            self.media_root_validator(path)
        except ValidationError as err:
            self.assertEqual(six.text_type(err.message), "Directory '%s' doesn't exist!" % path)

    def test_existing_dirs(self):
        BASE_PATH=os.path.abspath(os.path.dirname(django_tools.__file__))
        validator = ExistingDirValidator(BASE_PATH)
        for root, dirs, files in os.walk(BASE_PATH):
            for dir in dirs:
                path = os.path.join(root, dir)
                validator(path)

    def test_not_in_media_root1(self):
        try:
            self.media_root_validator("../")
        except ValidationError as err:
            self.assertEqual(six.text_type(err.message), "Directory is not in base path!")

    def test_not_in_media_root2(self):
        try:
            self.media_root_validator("//")
        except ValidationError as err:
            self.assertEqual(six.text_type(err.message), "Directory is not in base path!")

    def test_directory_traversal_attack_encodings(self):
        parts = (
            # URI encoded directory traversal:
            "%2e%2e%2f", # ../
            "%2e%2e/", # ../
            "..%2f", # ../
            "%2e%2e%5c", # ..\

            # Unicode / UTF-8 encoded directory traversal:
            "..%c1%1c", # ../
            "..%c0%af", # ..\
            "%c0%ae", # .
        )
        for part in parts:
            try:
                self.media_root_validator(part)
            except ValidationError as err:
                self.assertEqual(six.text_type(err.message), "Directory doesn't exist!")



class TestUrlValidator(SimpleTestCase):
    def test_scheme_without_netloc(self):
        try:
            URLValidator2(allow_all_schemes=True, allow_netloc=False)
        except AssertionError as err:
            self.assertEqual(str(err), "Can't allow schemes without netloc!")

    def test_no_allow_all_schemes(self):
        try:
            URLValidator2(allow_schemes=("http","ftp"), allow_all_schemes=True)
        except Warning as err:
            self.assertEqual(str(err), "allow_schemes would be ignored, while allow_all_schemes==True!")

    def test_not_start_with_allow_all_schemes(self):
        URLValidator2(allow_schemes=("svn",))("svn://domain.test")
        try:
            URLValidator2(allow_schemes=("http","ftp"))("svn://domain.test")
        except ValidationError as err:
            self.assertEqual(six.text_type(err.message), "The URL doesn't start with a allowed scheme.")

    def test_allow_query(self):
        validator = URLValidator2(allow_query=False)
        validator("http://www.domain.test/without/query/")
        try:
            validator("http://www.domain.test/with/?query")
        except ValidationError as err:
            self.assertEqual(six.text_type(err.message), "Enter a valid URL without a query.")

    def test_allow_fragment(self):
        validator = URLValidator2(allow_fragment=False)
        validator("http://www.domain.test/without/fragment/")
        try:
            validator("http://www.domain.test/with/a/#fragment")
        except ValidationError as err:
            self.assertEqual(six.text_type(err.message), "Enter a valid URL without a fragment.")

    def test_only_local_path1(self):
        validator = URLValidator2(allow_schemes=None, allow_netloc=False)
        validator("/path/?query#fragment")
        try:
            validator("http://domain.test/path/?query#fragment")
        except ValidationError as err:
            self.assertEqual(six.text_type(err.message), "Please enter a local URL (without protocol/domain).")

    def test_only_local_path2(self):
        """
        **Note:** Validating the network location (netloc):
        Following the syntax specifications in RFC 1808, urlparse recognizes a
        netloc only if it is properly introduced by '//'. Otherwise the input is
        presumed to be a relative URL and thus to start with a path component.
        See: http://docs.python.org/library/urlparse.html#urlparse.urlparse
        """
        validator = URLValidator2(allow_schemes=None, allow_netloc=False)
        validator("www.pylucid.org/path?query#fragment")
        try:
            validator("//www.pylucid.org/path?query#fragment")
        except ValidationError as err:
            self.assertEqual(six.text_type(err.message), "Please enter a local URL (without protocol/domain).")
