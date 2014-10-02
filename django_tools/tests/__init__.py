# coding: utf-8

#Hack to automatically import all tests
#from django_tools.tests.test_limit_to_usergroups import LimitToUsergroupsTest

import os
import glob
import unittest

if __name__ == "__main__":
    # run unittest directly
    os.environ["DJANGO_SETTINGS_MODULE"] = "django_tools_test_project.test_settings"

from django.test.testcases import SimpleTestCase


if __name__ != "__main__": # do it only if we imported
    print("import all django-tools tests:")
    _BASE_PATH = os.path.abspath(os.path.dirname(__file__))
#    print "_BASE_PATH:", _BASE_PATH
    for filename in glob.glob("*.py"):
        if not filename.startswith("test_"):
            continue
#        print "_"*79
#        print filename
        file_basename = os.path.splitext(filename)[0]
        _module = "django_tools.tests.%s" % file_basename
#        print _module
        if file_basename in locals():
    #        print "Skip!"
            continue
        _test_module = __import__(_module, globals(), locals(), ["*"])
    #    print "globals:", globals()
    #    print "locals:", locals().keys()
#        print _test_module
        
        # assimilate all local settings from modul, see: http://stackoverflow.com/a/2916810/746522
        for key in dir(_test_module):
            if key.startswith("_"):
                continue
            if "Test" in key:
                print("Add test class: %s.%s" % (_module, key))
                obj = getattr(_test_module, key)
                locals()[key] = obj

    
if __name__ == "__main__":
    # Run this unitest directly
    from django.core import management
    management.call_command('test',
        "django_tools",
        verbosity=2,
#        failfast=True
    )
#    unittest.main()
