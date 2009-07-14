# coding: utf-8

"""   
    unittest base
    ~~~~~~~~~~~~~
    
    :copyleft: 2009 by the django-dbpreferences team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import unittest

from django.core import management
from django.utils.encoding import smart_str
from django.contrib.auth.models import User

from BrowserDebug import debug_response



class BaseTestCase(unittest.TestCase):
    # Should we open a bwoser traceback?
    browser_traceback = True

    TEST_USERS = {
        "superuser": {
            "username": "superuser",
            "email": "superuser@example.org",
            "password": "superuser_password",
            "is_staff": True,
            "is_superuser": True,
        },
        "staff": {
            "username": "staff test user",
            "email": "staff_test_user@example.org",
            "password": "staff_test_user_password",
            "is_staff": True,
            "is_superuser": False,
        },
        "normal": {
            "username": "normal test user",
            "email": "normal_test_user@example.org",
            "password": "normal_test_user_password",
            "is_staff": False,
            "is_superuser": False,
        },
    }

    def _pre_setup(self):
        super(BaseTestCase, self).setUp()
        self._create_testusers()

    def login(self, usertype):
        """
        Login the user defined in self.TEST_USERS
        """
        ok = self.client.login(username=self.TEST_USERS[usertype]["username"],
                               password=self.TEST_USERS[usertype]["password"])
        self.failUnless(ok, "Can't login test user '%s'!" % usertype)
        return self._get_user(usertype)

    def _get_user(self, usertype):
        return User.objects.get(username=self.TEST_USERS[usertype]["username"])

    def _create_testusers(self):
        """
        Create all available testusers.
        """
        def create_user(username, password, email, is_staff, is_superuser):
            """
            Create a user and return the instance.
            """
            defaults = {'password':password, 'email':email}
            user, created = User.objects.get_or_create(
                username=username, defaults=defaults
            )
            if not created:
                user.email = email
            user.set_password(password)
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
        for usertype, userdata in self.TEST_USERS.iteritems():
            create_user(**userdata)

    def assertResponse(self, response, must_contain=(), must_not_contain=()):
        """
        Check the content of the response
        must_contain - a list with string how must be exists in the response.
        must_not_contain - a list of string how should not exists.
        """
        def error(respose, msg):
            debug_response(
                response, self.browser_traceback, msg, display_tb=False
            )
            raise self.failureException, msg

        for txt in must_contain:
            txt = smart_str(txt, response._charset)
            if not txt in response.content:
                error(response, "Text not in response: '%s'" % txt)

        for txt in must_not_contain:
            txt = smart_str(txt, response._charset)
            if txt in response.content:
                error(response, "Text should not be in response: '%s'" % txt)


def direct_run(raw_filename):
    """
    Run a test direct from a unittest file.
    A unittest file should add something like this:
    
    if __name__ == "__main__":
        # Run this unitest directly
        direct_run(__file__)
    """
    appname = os.path.splitext(os.path.basename(raw_filename))[0]
    management.call_command('test', appname)
