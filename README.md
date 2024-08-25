![django-tools](https://raw.githubusercontent.com/jedie/django-tools/master/logo/logo.svg "django-tools")

Miscellaneous tools for django.

Look also at the siblings project: [django-cms-tools](https://github.com/jedie/django-cms-tools) (Tools/helpers around Django-CMS).

| ![PyPi](https://img.shields.io/pypi/v/django-tools?label=django-tools%20%40%20PyPi "PyPi")                                             | [https://pypi.python.org/pypi/django-tools/](https://pypi.python.org/pypi/django-tools/) |
| ![Build Status on github](https://github.com/jedie/django-tools/workflows/test/badge.svg?branch=main "Build Status on github")         | [github.com/jedie/django-tools/actions](https://github.com/jedie/django-tools/actions)   |
| ![Coverage Status on codecov.io](https://codecov.io/gh/jedie/django-tools/branch/main/graph/badge.svg "Coverage Status on codecov.io") | [codecov.io/gh/jedie/django-tools](https://codecov.io/gh/jedie/django-tools)             |
| ![Coverage Status on coveralls.io](https://coveralls.io/repos/jedie/django-tools/badge.svg "Coverage Status on coveralls.io")          | [coveralls.io/r/jedie/django-tools](https://coveralls.io/r/jedie/django-tools)           |

![Python Versions](https://img.shields.io/pypi/pyversions/django-tools "Python Versions")
![License](https://img.shields.io/pypi/l/django-tools "License")

(Logo contributed by [@reallinfo](https://github.com/reallinfo) see [#16](https://github.com/jedie/django-tools/pull/16))

## try-out

e.g.:
```
~$ git clone https://github.com/jedie/django-tools.git
~$ cd django-tools/
~/django-tools$ ./manage.py
```

## existing stuff

### Serve User Media File

Serve `settings.MEDIA_ROOT` files only for allowed users.

See separate README here: [django_tools/serve_media_app](https://github.com/jedie/django-tools/tree/main/django_tools/serve_media_app)

### Mode Version Protect

Protect a model against overwriting a newer entry with an older one, by adding a auto increment version number.

See separate README here: [django_tools/model_version_protect](https://github.com/jedie/django-tools/tree/main/django_tools/model_version_protect)

### OverwriteFileSystemStorage

A django filesystem storage that will overwrite existing files and can create backups, if content changed.
usage:
```
class ExampleModel(models.Model):
    foo_file = models.FileField(
        storage=OverwriteFileSystemStorage(create_backups=True)
    )
    bar_image = models.ImageField(
        storage=OverwriteFileSystemStorage(create_backups=False)
    )
```

Backup made by appending a suffix and sequential number, e.g.:


* source....: foo.bar
* backup 1..: foo.bar.bak
* backup 2..: foo.bar.bak0
* backup 3..: foo.bar.bak1

Backup files are only made if file content changed. But at least one time!

### Django Logging utils

Put this into your settings, e.g.:
```
from django_tools.unittest_utils.logging_utils import CutPathnameLogRecordFactory, FilterAndLogWarnings

# Filter warnings and pipe them to logging system
# Warnings of external packages are displayed only once and only the file path.
warnings.showwarning = FilterAndLogWarnings()

# Adds 'cut_path' attribute on log record. So '%(cut_path)s' can be used in log formatter.
logging.setLogRecordFactory(CutPathnameLogRecordFactory(max_length=50))

LOGGING = {
    # ...
    'formatters': {
        'verbose': {
            'format': '%(levelname)8s %(cut_path)s:%(lineno)-3s %(message)s'
        },
    },
    # ...
}
```

(Activate warnings by, e.g.: `export PYTHONWARNINGS=all`)

#### ThrottledAdminEmailHandler

[ThrottledAdminEmailHandler](https://github.com/jedie/django-tools/blob/master/django_tools/log_utils/throttle_admin_email_handler.py) works similar as the origin [django.utils.log.AdminEmailHandler](https://docs.djangoproject.com/en/1.11/topics/logging/#django.utils.log.AdminEmailHandler)
but is will throttle the number of mails that can be send in a time range.
usage e.g.:
```
LOGGING = {
    # ...
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "class": "django_tools.log_utils.throttle_admin_email_handler.ThrottledAdminEmailHandler",
            "formatter": "email",
            "min_delay_sec": 20, # << -- skip mails in this time range
        },
        # ...
    },
    # ...
}
```

### django_tools.template.loader.DebugCacheLoader

Insert template name as html comments, e.g.:
```
<!-- START 'foo/bar.html' -->
...
<!-- END 'foo/bar.html' -->
```

To use this, you must add **django_tools.template.loader.DebugCacheLoader** as template loader.

e.g.: Activate it only in DEBUG mode:
```
if DEBUG:
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        (
            "django_tools.template.loader.DebugCacheLoader", (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            )
        )
    ]
```

### send text+html mails

A helper class to send text+html mails used the django template library.

You need two template files, e.g.:


* [mail_test.txt](https://github.com/jedie/django-tools/blob/master/django_tools_test_project/django_tools_test_app/templates/mail_test.txt)
* [mail_test.html](https://github.com/jedie/django-tools/blob/master/django_tools_test_project/django_tools_test_app/templates/mail_test.html)

You have to specify the template file like this: `template_base="mail_test.{ext}"`

Send via Celery task:
```
# settings.py
SEND_MAIL_CELERY_TASK_NAME="mail:send_task"

from django_tools.mail.send_mail import SendMailCelery
SendMailCelery(
    template_base="mail_test.{ext}",
    mail_context={"foo": "first", "bar": "second"},
    subject="Only a test",
    recipient_list="foo@bar.tld"
).send()
```

Send without Celery:
```
from django_tools.mail.send_mail import SendMail
SendMail(
    template_base="mail_test.{ext}",
    mail_context={"foo": "first", "bar": "second"},
    subject="Only a test",
    recipient_list="foo@bar.tld"
).send()
```

See also the existing unittests:


* [django_tools_tests/test_email.py](https://github.com/jedie/django-tools/blob/master/django_tools_tests/test_email.py)

### Delay tools

Sometimes you want to simulate when processing takes a little longer.
There exists `django_tools.debug.delay.SessionDelay` and `django_tools.debug.delay.CacheDelay` for this.
The usage will create logging entries and user messages, if user is authenticated.

More info in seperate [django_tools/debug/README.creole](https://github.com/jedie/django-tools/blob/master/django_tools/debug/README.creole) file.

### Filemanager library

Library for building django application like filemanager, gallery etc.

more info, read [./filemanager/README.creole](https://github.com/jedie/django-tools/blob/master/django_tools/filemanager/README.creole)

### per-site cache middleware

Similar to [django UpdateCacheMiddleware and FetchFromCacheMiddleware](https://docs.djangoproject.com/en/1.4/topics/cache/#the-per-site-cache),
but has some enhancements: ['per site cache' in ./cache/README.creole](https://github.com/jedie/django-tools/blob/master/django_tools/cache/README.creole#per-site-cache-middleware)

### smooth cache backends

Same as django cache backends, but adds `cache.smooth_update()` to clears the cache smoothly depend on the current system load.
more info in: ['smooth cache backends' in ./cache/README.creole](https://github.com/jedie/django-tools/blob/master/django_tools/cache/README.creole#smooth-cache-backends)

### local sync cache

Keep a local dict in a multi-threaded environment up-to-date. Usefull for cache dicts.
More info, read DocString in [./local_sync_cache/local_sync_cache.py](https://github.com/jedie/django-tools/blob/master/django_tools/local_sync_cache/local_sync_cache.py).

### threadlocals middleware

For getting request object anywhere, use [./middlewares/ThreadLocal.py](https://github.com/jedie/django-tools/blob/master/django_tools/middlewares/ThreadLocal.py)

### Dynamic SITE_ID middleware

Note: Currently not maintained! TODO: Fix unittests for all python/django version

Set settings.SITE_ID dynamically with a middleware base on the current request domain name.
Domain name alias can be specify as a simple string or as a regular expression.

more info, read [./dynamic_site/README.creole](https://github.com/jedie/django-tools/blob/master/django_tools/dynamic_site/README.creole).

### StackInfoStorage

Message storage like LegacyFallbackStorage, except, every message would have a stack info, witch is helpful, for debugging.
Stack info would only be added, if settings DEBUG or MESSAGE_DEBUG is on.
To use it, put this into your settings:
```
MESSAGE_STORAGE = "django_tools.utils.messages.StackInfoStorage"
```

More info, read DocString in [./utils/messages.py](https://github.com/jedie/django-tools/blob/master/django_tools/utils/messages.py).

### limit to usergroups

Limit something with only one field, by selecting:


* anonymous users
* staff users
* superusers
* ..all existing user groups..

More info, read DocString in [./limit_to_usergroups.py](https://github.com/jedie/django-tools/blob/master/django_tools/limit_to_usergroups.py)

### permission helpers

See [django_tools.permissions](https://github.com/jedie/django-tools/blob/master/django_tools/permissions.py)
and unittests: [django_tools_tests.test_permissions](https://github.com/jedie/django-tools/blob/master/django_tools_tests/test_permissions.py)

### form/model fields


* [Directory field](https://github.com/jedie/django-tools/blob/master/django_tools/fields/directory.py) - check if exist and if in a defined base path
* [language code field with validator](https://github.com/jedie/django-tools/blob/master/django_tools/fields/language_code.py)
* [Media Path field](https://github.com/jedie/django-tools/blob/master/django_tools/fields/media_path.py) browse existign path to select and validate input
* [sign seperated form/model field](https://github.com/jedie/django-tools/blob/master/django_tools/fields/sign_separated.py) e.g. comma seperated field
* [static path field](https://github.com/jedie/django-tools/blob/master/django_tools/fields/static_path.py)
* [url field](https://github.com/jedie/django-tools/blob/master/django_tools/fields/url.py) A flexible version of the original django form URLField

## unittests helpers

### Selenium Test Cases

There are Firefox and Chromium test cases, with and without django StaticLiveServerTestCase!

Chromium + StaticLiveServer example:
```
from django_tools.selenium.chromedriver import chromium_available
from django_tools.selenium.django import SeleniumChromiumStaticLiveServerTestCase

@unittest.skipUnless(chromium_available(), "Skip because Chromium is not available!")
class ExampleChromiumTests(SeleniumChromiumStaticLiveServerTestCase):
    def test_admin_login_page(self):
        self.driver.get(self.live_server_url + "/admin/login/")
        self.assert_equal_page_title("Log in | Django site admin")
        self.assert_in_page_source('<form action="/admin/login/" method="post" id="login-form">')
        self.assert_no_javascript_alert()
```

Firefox + StaticLiveServer example:
```
from django_tools.selenium.django import SeleniumFirefoxStaticLiveServerTestCase
from django_tools.selenium.geckodriver import firefox_available

@unittest.skipUnless(firefox_available(), "Skip because Firefox is not available!")
class ExampleFirefoxTests(SeleniumFirefoxStaticLiveServerTestCase):
    def test_admin_login_page(self):
        self.driver.get(self.live_server_url + "/admin/login/")
        self.assert_equal_page_title("Log in | Django site admin")
        self.assert_in_page_source('<form action="/admin/login/" method="post" id="login-form">')
        self.assert_no_javascript_alert()
```

Test cases without StaticLiveServer:
```
from django_tools.selenium.chromedriver import SeleniumChromiumTestCase
from django_tools.selenium.geckodriver import SeleniumFirefoxTestCase
```

See also existing unitests here:


* [/django_tools/django_tools_tests/test_unittest_selenium.py](https://github.com/jedie/django-tools/blob/master/django_tools/django_tools_tests/test_unittest_selenium.py)

#### Setup Web Drivers

Selenium test cases needs the browser and the web driver.

`SeleniumChromiumTestCase` and `SeleniumFirefoxTestCase` will automaticly install the web driver via [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager)

There is a small CLI (called `django_tools_selenium`) to check / install the web drivers, e.g.:
```
~/django-tools$ poetry run django_tools_selenium install
~/django-tools$ poetry run django_tools_selenium info
```

### Mockup utils

Create dummy PIL/django-filer images with Text, see:


* [/django_tools/unittest_utils/mockup.py](https://github.com/jedie/django-tools/blob/master/django_tools/unittest_utils/mockup.py)

usage/tests:


* [/django_tools_tests/test_mockup.py](https://github.com/jedie/django-tools/blob/master/django_tools_tests/test_mockup.py)

### Model instance unittest code generator

Generate unittest code skeletons from existing model instance. You can use this feature as django manage command or as admin action.

Usage as management command, e.g.:
```
$ ./manage.py generate_model_test_code auth.
...
#
# pk:1 from auth.User <class 'django.contrib.auth.models.User'>
#
user = User.objects.create(
    password='pbkdf2_sha256$36000$ybRfVQDOPQ9F$jwmgc5UsqRQSXxJs/NrZeTLguieUSSZfaSZbMmC+L5w=', # CharField, String (up to 128)
    last_login=datetime.datetime(2018, 4, 24, 8, 27, 49, 578107, tzinfo=<UTC>), # DateTimeField, Date (with time)
    is_superuser=True, # BooleanField, Boolean (Either True or False)
    username='test', # CharField, String (up to 150)
    first_name='', # CharField, String (up to 30)
    last_name='', # CharField, String (up to 30)
    email='', # CharField, Email address
    is_staff=True, # BooleanField, Boolean (Either True or False)
    is_active=True, # BooleanField, Boolean (Either True or False)
    date_joined=datetime.datetime(2018, 3, 6, 17, 15, 50, 93136, tzinfo=<UTC>), # DateTimeField, Date (with time)
)
...
```

### create users

[/unittest_utils/user.py](https://github.com/jedie/django-tools/blob/master/django_tools/unittest_utils/user.py):


* `django_tools.unittest_utils.user.create_user()` - create users, get_super_user
* `django_tools.unittest_utils.user.get_super_user()` - get the first existing superuser

### Isolated Filesystem decorator / context manager

[django_tools.unittest_utils.isolated_filesystem.isolated_filesystem](https://github.com/jedie/django-tools/blob/master/django_tools/unittest_utils/isolated_filesystem.py) acts as either a decorator or a context manager.
Useful to for tests that will create files/directories in current work dir, it does this:


* create a new temp directory
* change the current working directory to the temp directory
* after exit:
* Delete an entire temp directory tree

usage e.g.:
```
from django_tools.unittest_utils.isolated_filesystem import isolated_filesystem

with isolated_filesystem(prefix="temp_dir_prefix"):
    open("foo.txt", "w").write("bar")
```

### BaseUnittestCase

**django_tools.unittest_utils.unittest_base.BaseUnittestCase** contains some low-level assert methods:


* assertEqual_dedent()

Note: assert methods will be migrated to: `django_tools.unittest_utils.assertments` in the future!

_django_tools.unittest_utils.tempdir_ contains **TempDir**, a Context Manager Class:
```
with TempDir(prefix="foo_") as tempfolder:
    # create a file:
    open(os.path.join(tempfolder, "bar"), "w").close()

# the created temp folder was deleted with shutil.rmtree()
```

usage/tests:


* [/django_tools_tests/test_unittest_utils.py](https://github.com/jedie/django-tools/blob/master/django_tools_tests/test_unittest_utils.py)

### DjangoCommandMixin

Helper to run shell commands. e.g.: "./manage.py cms check" in unittests.

usage/tests:


* [/django_tools_tests/test_unittest_django_command.py](https://github.com/jedie/django-tools/blob/master/django_tools_tests/test_unittest_django_command.py)

### DOM compare in unittests

The Problem:
You can’t easy check if e.g. some form input fields are in the response,
because the form rendering use a dict for storing all html attributes.
So, the ordering of form field attributes are not sorted and varied.

The Solution:
You need to parse the response content into a DOM tree and compare nodes.

We add the great work of Gregor Müllegger at his GSoC 2011 form-rendering branch.
You will have the following assert methods inherit from: django_tools.unittest_utils.unittest_base.BaseTestCase


* self.assertHTMLEqual() – for compare two HTML DOM trees
* self.assertDOM() – for check if nodes in response or not.
* self.assertContains() – Check if ond node occurs 'count’ times in response

More info and examples in [./django_tools_tests/test_dom_asserts.py](https://github.com/jedie/django-tools/blob/master/django_tools/django_tools_tests/test_dom_asserts.py)

### @set_string_if_invalid() decorator

Helper to check if there are missing template tags by set temporary `'string_if_invalid'`, see: [https://docs.djangoproject.com/en/1.8/ref/templates/api/#invalid-template-variables](https://docs.djangoproject.com/en/1.8/ref/templates/api/#invalid-template-variables)

Usage, e.g.:
```
from django.test import SimpleTestCase
from django_tools.unittest_utils.template import TEMPLATE_INVALID_PREFIX, set_string_if_invalid

@set_string_if_invalid()
class TestMyTemplate(SimpleTestCase):
    def test_valid_tag(self):
        response = self.client.get('/foo/bar/')
        self.assertNotIn(TEMPLATE_INVALID_PREFIX, response.content)
```

You can also decorate the test method ;)

### unittest_utils/signals.py


* `SignalsContextManager` connect/disconnet signal callbacks via with statement

### unittest_utils/assertments.py

The file contains some common assert functions:


* `assert_startswith` - Check if test starts with prefix.
* `assert_endswith` - Check if text ends with suffix.
* `assert_locmem_mail_backend` - Check if current email backend is the In-memory backend.
* {{{assert_language_code() - Check if given language_code is in settings.LANGUAGES
* `assert_installed_apps()` - Check entries in settings.INSTALLED_APPS
* `assert_is_dir` - Check if given path is a directory
* `assert_is_file` - Check if given path is a file
* `assert_path_not_exists` - Check if given path doesn't exists

### Speedup tests

Speedup test run start by disable migrations, e.g.:
```
from django_tools.unittest_utils.disable_migrations import DisableMigrations
MIGRATION_MODULES = DisableMigrations()
```

### small tools

#### debug_csrf_failure()

Display the normal debug page and not the minimal csrf debug page.
More info in DocString here: [django_tools/views/csrf.py](https://github.com/jedie/django-tools/blob/master/django_tools/views/csrf.py)

#### import lib helper

additional helper to the existing `importlib`
more info in the sourcecode: [./utils/importlib.py](https://github.com/jedie/django-tools/blob/master/django_tools/utils/importlib.py)

#### http utils

Pimped HttpRequest to get some more information about a request.
More info in DocString here: [django_tools/utils/http.py](https://github.com/jedie/django-tools/blob/master/django_tools/utils/http.py)

#### @display_admin_error

Developer helper to display silent errors in ModelAdmin.list_display callables.
See: **display_admin_error** in [decorators.py](https://github.com/jedie/django-tools/blob/master/django_tools/decorators.py)

### upgrade virtualenv

A simple commandline script that calls `pip install —-upgrade XY` for every package thats installed in a virtualenv.
Simply copy/symlink it into the root directory of your virtualenv and start it.

**Note:**[Seems that this solution can't observe editables right.](https://github.com/pypa/pip/issues/319)

To use it, without installing django-tools:
```
~/$ cd goto/your_env
.../your_env/$ wget https://github.com/jedie/django-tools/raw/master/django_tools/upgrade_virtualenv.py
.../your_env/$ chmod +x upgrade_virtualenv.py
.../your_env/$ ./upgrade_virtualenv.py
```

This script will be obsolete, if [pip has a own upgrade command](https://github.com/pypa/pip/issues/59).

### django_tools.utils.url.GetDict

Similar to origin django.http.QueryDict but:


* urlencode() doesn't add "=" to empty values: "?empty" instead of "?empty="
* always mutable
* output will be sorted (easier for tests ;)

More info, see tests: [django_tools_tests/test_utils_url.py](https://github.com/jedie/django-tools/blob/master/django_tools_tests/test_utils_url.py)

#### SignedCookieStorage

Store information in signed Cookies, use **django.core.signing**.
So the cookie data can't be manipulated from the client.
Sources/examples:


* [/django_tools/utils/client_storage.py](https://github.com/jedie/django-tools/blob/master/django_tools/utils/client_storage.py)
* [/django_tools_tests/test_signed_cookie.py](https://github.com/jedie/django-tools/blob/master/django_tools_tests/test_signed_cookie.py)

### Print SQL Queries

Print the used SQL queries via context manager.

usage e.g.:
```
from django_tools.unittest_utils.print_sql import PrintQueries

# e.g. use in unittests:
class MyTests(TestCase):
    def test_foobar(self):
        with PrintQueries("Create object"):
            FooBar.objects.create("name"=foo)

# e.g. use in views:
def my_view(request):
    with PrintQueries("Create object"):
        FooBar.objects.create("name"=foo)
```

the output is like:
```
_______________________________________________________________________________
 *** Create object ***
1 - INSERT INTO "foobar" ("name")
    VALUES (foo)
-------------------------------------------------------------------------------
```

### SetRequestDebugMiddleware

middleware to add debug bool attribute to request object.
More info: [./debug/README.creole](https://github.com/jedie/django-tools/blob/master/django_tools/debug/README.creole)

### TracebackLogMiddleware

Put traceback in log by call [logging.exception()](https://docs.python.org/3/library/logging.html#logging.Logger.exception) on `process_exception()`
Activate with:
```
MIDDLEWARE_CLASSES = (
    ...
    'django_tools.middlewares.TracebackLogMiddleware.TracebackLogMiddleware',
    ...
)
```

### FnMatchIps() - Unix shell-style wildcards in INTERNAL_IPS / ALLOWED_HOSTS

settings.py e.g.:
```
from django_tools.settings_utils import FnMatchIps

INTERNAL_IPS = FnMatchIps(["127.0.0.1", "::1", "192.168.*.*", "10.0.*.*"])
ALLOWED_HOSTS = FnMatchIps(["127.0.0.1", "::1", "192.168.*.*", "10.0.*.*"])
```

### StdoutStderrBuffer()

redirect stdout + stderr to a string buffer. e.g.:
```
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer

with StdoutStderrBuffer() as buffer:
    print("foo")
output = buffer.get_output() # contains "foo\n"
```

### Management commands

#### permission_info

List all permissions for one django user.
(Needs `'django_tools'` in INSTALLED_APPS)

e.g.:
```
$ ./manage.py permission_info
No username given!

All existing users are:
foo, bar, john, doe

$ ./manage.py permission_info foo
All permissions for user 'test_editor':
	is_active    : yes
	is_staff     : yes
	is_superuser : no
[*] admin.add_logentry
[*] admin.change_logentry
[*] admin.delete_logentry
[ ] auth.add_group
[ ] auth.add_permission
[ ] auth.add_user
...
```

#### logging_info

Shows a list of all loggers and marks which ones are configured in settings.LOGGING:
```
$ ./manage.py logging_info
```

#### nice_diffsettings

Similar to django 'diffsettings', but used pretty-printed representation:
```
$ ./manage.py nice_diffsettings
```

#### database_info

Just display some information about the used database and connections:
```
$ ./manage.py database_info
```

#### list_models

Just list all existing models in app_label.ModelName format. Useful to use this in 'dumpdata' etc:
```
$ ./manage.py list_models
```

### ..all others…

There exist many miscellaneous stuff. Look in the source, luke!

## Backwards-incompatible changes

Old changes archived in git history here:


* [>=v0.47](https://github.com/jedie/django-tools/tree/v0.49.0#backwards-incompatible-changes)
* [>=v0.35](https://github.com/jedie/django-tools/tree/v0.35.0#backwards-incompatible-changes)

### v0.51

All Selenium helper are deprecated, please migrate to [Playwright](https://playwright.dev/python/) ;)

### v0.50

Removed old selenium helper function, [deprecated since v0.43](https://github.com/jedie/django-tools/tree/v0.43.0#v043)

Make all Selenium web driver instances persistent for the complete test run session.
This speedup tests and fixed some bugs in Selenium.

This result in the same browser/webdriver settings for all test classes!

### v0.55

Move supported Django/Python min. versions to:
* Django 4.1, 4.2, 5.1
* Python 3.11, 3.12


## Django compatibility

| django-tools     | django version | python          |
|------------------|----------------|-----------------|
| >= v0.56.0       | 4.1, 4.2, 5.1  | 3.11, 3.12      |
| >= v0.52.0       | 3.2, 4.0, 4.1  | 3.8, 3.9, 3.10  |
| >= v0.50.0       | 2.2, 3.2, 4.0  | 3.8, 3.9, 3.10  |
| >= v0.49.0       | 2.2, 3.1, 3.2  | 3.7, 3.8, 3.9   |
| >= v0.47.0       | 2.2, 3.0, 3.1  | >= 3.6, pypy3   |
| >= v0.39         | 1.11, 2.0      | 3.5, 3.6, pypy3 |
| >= v0.38.1       | 1.8, 1.11      | 3.5, 3.6, pypy3 |
| >= v0.38.0       | 1.8, 1.11      | 3.5, 3.6        |
| >= v0.37.0       | 1.8, 1.11      | 3.4, 3.5        |
| >= v0.33.0       | 1.8, 1.11      | 2.7, 3.4, 3.5   |
| v0.30.1-v0.32.14 | 1.8, 1.9, 1.10 | 2.7, 3.4, 3.5   |
| v0.30            | 1.8, 1.9       | 2.7, 3.4        |
| v0.29            | 1.6 - 1.8      | 2.7, 3.4        |
| v0.26            | <=1.6          |                 |
| v0.25            | <=1.4          |                 |

(See also combinations for [tox in pyproject.toml](https://github.com/jedie/django-tools/blob/master/pyproject.toml))

## history

[comment]: <> (✂✂✂ auto generated history start ✂✂✂)

* [v0.56.1](https://github.com/jedie/django-tools/compare/v0.56.0...v0.56.1)
  * 2024-08-25 - Use typeguard in tests
  * 2024-08-25 - Use cli_base update-readme-history
  * 2024-08-25 - Update via manageprojects
* [v0.56.0](https://github.com/jedie/django-tools/compare/v0.54.0...v0.56.0)
  * 2024-08-25 - Bugfix local test run with a real terminal ;)
  * 2024-08-25 - Fix CI
  * 2023-04-10 - Upgrade: use managed-django-projec, Remove deprecations, update supported versions
* [v0.54.0](https://github.com/jedie/django-tools/compare/v0.53.0...v0.54.0)
  * 2022-09-15 - Bugfix version check
  * 2022-08-23 - Replace README.creole with README.md
  * 2022-08-26 - Run safety check in CI
  * 2022-08-25 - NEW: SyslogHandler for easy logging to syslog
* [v0.53.0](https://github.com/jedie/django-tools/compare/v0.52.0...v0.53.0)
  * 2022-08-18 - v0.53.0
  * 2022-08-18 - fix readme
  * 2022-08-18 - Fix tests
  * 2022-08-18 - order and clean run server kwargs
  * 2022-08-18 - fix gitignore
  * 2022-08-18 - fix tox run
  * 2022-08-18 - Bugfix Python 3.8 support
  * 2022-08-18 - polish run_testserver command
  * 2022-08-18 - update test project settings
  * 2022-08-18 - Fix "database_info" command and pprint to self.stdout stream
  * 2022-08-18 - Fix manage.sh by set "local" settings
  * 2022-08-18 - run-server: do not make stderr output -> use style
  * 2022-08-18 - NEW: MassContextManagerBase, DenyStdWrite + Updated: StdoutStderrBuffer

<details><summary>Expand older history entries ...</summary>

* [v0.52.0](https://github.com/jedie/django-tools/compare/v0.51.0...v0.52.0)
  * 2022-08-17 - code cleanup
  * 2022-08-17 - Restrict `AlwaysLoggedInAsSuperUserMiddleware` to the admin.
  * 2022-08-17 - Move `run_testserver` management command from `django_tools_test_app` to `django_tools` and polish it.
  * 2022-07-02 - speedup CI
  * 2022-08-16 - fix tox and CI
  * 2022-08-16 - Update requirements
  * 2022-08-12 - Test with Django 3.2, 4.0 and 4.1
  * 2022-08-12 - fix code style
* [v0.51.0](https://github.com/jedie/django-tools/compare/v0.50.0...v0.51.0)
  * 2022-07-26 - NEW: check_editor_config() + release as v0.51.0
  * 2022-07-26 - fix wrong editor config
  * 2022-07-26 - Add fancy icons to README
  * 2022-07-15 - Update requirements
  * 2022-07-02 - NEW: Playwright base Unittest class and login helper
  * 2022-07-02 - DEPRECATE all Selenium helper
  * 2022-07-02 - use: codecov/codecov-action@v2
* [v0.50.0](https://github.com/jedie/django-tools/compare/v0.49.0...v0.50.0)
  * 2022-05-29 - Update requirements
  * 2022-05-29 - fix Makefile
  * 2022-05-16 - replace assert_html_snapshot with assert_html_response_snapshot
  * 2022-05-16 - fix code style
  * 2022-04-15 - Update pythonapp.yml
  * 2022-02-05 - Enable console log output in *.log file
  * 2022-02-05 - Refactor selenium helper and use webdriver-manager to setup the webdriver
  * 2022-02-05 - Update publish.py
  * 2022-02-05 - lower max line length to 100
  * 2022-02-05 - Remove linting in github actions, because it's done via pytest plugins
  * 2022-01-30 - Update README
  * 2022-01-30 - Expand tests with Python 3.10 and Django 4.0
  * 2022-01-30 - Use darker as code formatter
  * 2022-01-13 - Fix github actions
  * 2022-01-13 - Apply flynt run
  * 2022-01-13 - Move flynt settings into pyproject.toml
* [v0.49.0](https://github.com/jedie/django-tools/compare/v0.48.3...v0.49.0)
  * 2021-11-22 - Refactor selenium helper:
  * 2021-11-22 - log the found executable
  * 2021-11-22 - Remove w3c change
  * 2021-11-22 - change webdriver local to 'en_US.UTF-8'
  * 2021-11-22 - Fix #21 Set chrome accept_languages in headless mode
  * 2021-11-21 - fix test
  * 2021-11-20 - NEW: Model Version Protect
  * 2021-11-21 - Update selenium test helper
  * 2021-11-21 - update README
  * 2021-11-21 - refactor CI
  * 2021-11-21 - Remove Python 3.6
  * 2021-11-21 - Update pythonapp.yml
  * 2021-11-21 - Refactor settings and move all project test files
  * 2021-11-21 - update project urls.py
  * 2021-11-21 - remove migration tests
  * 2021-11-21 - Pass current envrionment in call_manage_py()
  * 2021-11-20 - Bugfix test project
  * 2021-11-21 - NEW: AlwaysLoggedInAsSuperUserMiddleware
  * 2021-11-21 - Update README and check if "make" help always up2date
  * 2021-11-21 - Fix code style and make targets for this
  * 2021-11-21 - Update Makefile
  * 2021-11-21 - Refactor selenium test helpers
  * 2021-11-21 - code style
  * 2021-11-21 - copy DesiredCapabilities dict
  * 2021-11-21 - Fix make "lint" + "fix-code-style" and run fixing by tests
  * 2021-11-20 - Bugfix selenium chrome tests on github
  * 2021-11-20 - Bugfix tests: remove aboslute path from snapshots
  * 2021-11-20 - try to install chromedriver and geckodriver via seleniumbase in CI
  * 2021-11-20 - fix typo in log message
  * 2021-11-20 - Django update: smart_text() -> smart_str()
  * 2021-11-20 - use snapshot tests
  * 2021-11-20 - sync README
  * 2021-11-20 - Add "bx_py_utils" and use snapshot in tests
  * 2021-11-20 - Update README.creole
  * 2021-11-20 - Update tests
  * 2021-11-20 - Bugfix isolated_filesystem: It doesn't work as class decorator!
  * 2021-11-20 - Modernize the test project
  * 2021-11-20 - Update test
  * 2021-11-20 - Add poetry.lock and update requirements
  * 2021-11-20 - move tests
* [v0.48.3](https://github.com/jedie/django-tools/compare/v0.48.2...v0.48.3)
  * 2020-12-20 - NEW: ImageDummy().in_memory_image_file() useful for e.g.: POST a image upload via Django's test client
* [v0.48.2](https://github.com/jedie/django-tools/compare/v0.48.1...v0.48.2)
  * 2020-12-06 - relase as v0.48.2
  * 2020-12-06 - test 0.48.2rc2
  * 2020-12-06 - Handle if user token not exists
  * 2020-12-06 - change "serve_media_app" migration: Create UserMediaTokenModel for existing users
* [v0.48.1](https://github.com/jedie/django-tools/compare/v0.48.0...v0.48.1)
  * 2020-12-06 - add .../serve_media_app/migrations/0001_initial.py
  * 2020-12-06 - add ./manage.sh helper
* [v0.48.0](https://github.com/jedie/django-tools/compare/v0.47.0...v0.48.0)
  * 2020-12-06 - fist 'fix-code-style' then 'pytest'
  * 2020-12-06 - fix code style
  * 2020-12-06 - update README
  * 2020-12-06 - fix and update tests
  * 2020-12-06 - Add more info in logging output
  * 2020-12-06 - Add a note to "pytest-randomly"
  * 2020-12-06 - Support app config entries in get_filtered_apps()
  * 2020-12-06 - bugfix test project urls setup
  * 2020-11-27 - Update README.md
  * 2020-11-27 - NEW: "Serve User Media File" reuseable app
  * 2020-11-27 - NEW: django_tools.unittest_utils.signals.SignalsContextManager
  * 2020-11-27 - Change `ImageDummy` and make `text` optional
* [v0.47.0](https://github.com/jedie/django-tools/compare/v0.46.1...v0.47.0)
  * 2020-11-26 - code style
  * 2020-11-26 - fix test setup and github actions
  * 2020-11-26 - update AUTHORS
  * 2020-11-26 - update .gitignore
  * 2020-11-26 - Update README and set v0.47.dev0
  * 2020-11-26 - expand tox envlist, bugfix coverage settings and pytest call
  * 2020-11-26 - fix DjangoCommandMixin
  * 2020-11-26 - remove LoggingBuffer and update tests
  * 2020-11-26 - NEW: assert_in_logs()
  * 2020-11-26 - remove warnings check (Because of warnings from external apps)
  * 2020-11-26 - force_text -> force_str
  * 2020-11-26 - NEW: assert_warnings() and assert_no_warnings()
  * 2020-11-26 - fix test_set_env()
  * 2020-11-26 - use os.environ.setdefault
  * 2020-11-26 - ugettext -> gettext
  * 2020-11-26 - remove assertment
  * 2020-11-26 - Update some django imports for new django version
  * 2020-11-26 - update test_update_rst_readme()
  * 2020-11-26 - update pyproject.toml and move some external meta config files
  * 2020-11-05 - Disable fail-fast
  * 2020-11-05 - Fix broken UTs
  * 2020-11-05 - Ignore non-test files
  * 2020-11-05 - Ignore doctest import errors
  * 2020-11-05 - Fix two import errors
  * 2020-11-05 - Fix version compare
  * 2020-09-06 - CHORE: Add django 3.1 compatibility
  * 2020-11-05 - Trigger test job on pull_request event
  * 2020-11-05 - Fix broken UT due to deprecated options of pytest
  * 2020-07-04 - use f-strings
  * 2020-07-04 - render_to_response() -> render()
  * 2020-07-04 - update README.rst
  * 2020-07-04 - add github action badge
  * 2020-07-04 - Add "make update"
  * 2020-07-04 - Update README.creole
  * 2019-04-03 - Add files via upload
  * 2019-04-03 - Delete logo_white.png
  * 2019-04-03 - Delete logo_black.png
  * 2019-04-03 - Delete logo.png
* [v0.46.1](https://github.com/jedie/django-tools/compare/v0.46.0...v0.46.1)
  * 2020-02-19 - Fix manage tests
  * 2020-02-19 - fixup! use shutil.which() in SeleniumChromiumTestCase()
  * 2020-02-19 - set "accept_languages" and disable "headless" mode
  * 2020-02-19 - use shutil.which() in SeleniumChromiumTestCase()
  * 2020-02-19 - NEW: "django_tools.middlewares.LogHeaders.LogRequestHeadersMiddleware"
  * 2020-02-19 - bugfix running test project dev. server
  * 2020-02-19 - merge code by using test code from poetry-publish
  * 2020-02-19 - less restricted dependency specification
* [v0.46.0](https://github.com/jedie/django-tools/compare/v0.45.3...v0.46.0)
  * 2020-02-13 - update README and release as v0.46.0
  * 2020-02-13 - work-a-round for failed test on github...
  * 2020-02-13 - WIP: Fix github CI
  * 2020-02-13 - +django_tools_tests/test_project_setup.py
  * 2020-02-13 - don't publish if README is not up-to-date
  * 2020-02-13 - use tox-gh-actions on github CI
  * 2020-02-13 - enable linting on CI
  * 2020-02-13 - fix code style
  * 2020-02-13 - code cleanup: remove six stuff
  * 2020-02-13 - apply code style
  * 2020-02-13 - update Makefile
  * 2020-02-13 - apply pyupgrade
  * 2020-02-13 - update tests
  * 2020-02-13 - Bugfix: Don't set settings.MEDIA_ROOT in DocTest
  * 2020-02-13 - use f-strings
  * 2020-02-13 - update selenium test
  * 2020-02-13 - update test setup
  * 2020-02-13 - remove "dynamic_site"
  * 2020-02-12 - WIP: use poetry
  * 2020-02-12 - remove lxml and use bleach.clean() in html2text()
  * 2020-02-12 - Update requirements-dev.txt
* [v0.45.3](https://github.com/jedie/django-tools/compare/v0.45.2...v0.45.3)
  * 2019-08-25 - release v0.45.3
  * 2019-08-25 - Add "excepted_exit_code" into DjangoCommandMixin methods
* [v0.45.2](https://github.com/jedie/django-tools/compare/v0.45.1...v0.45.2)
  * 2019-06-25 - update test settings: MIDDLEWARE_CLASSES -> MIDDLEWARE
  * 2019-06-25 - add: ThrottledAdminEmailHandler
  * 2019-06-13 - Bugfix wrong BaseUnittestCase.assertEqual_dedent() refactoring
* [v0.45.1](https://github.com/jedie/django-tools/compare/v0.45.0...v0.45.1)
  * 2019-04-03 - Bugfix print_mailbox if attachment is MIMEImage instance
  * 2019-04-01 - code cleanup
* [v0.45.0](https://github.com/jedie/django-tools/compare/v0.44.2...v0.45.0)
  * 2019-04-01 - __version__ = "0.45.0"
  * 2019-04-01 - Update README.creole
  * 2019-04-01 - bugfix: str() needed for python 3.5
  * 2019-04-01 - +=== OverwriteFileSystemStorage
  * 2019-04-01 - move "assert_equal_dedent" and "assert_in_dedent"
  * 2019-03-30 - use assert_pformat_equal for assertEqual_dedent, too
  * 2019-03-30 - only code formatting with black
  * 2019-03-30 - NEW: OverwriteFileSystemStorage
  * 2019-03-30 - new: assert_pformat_equal
  * 2019-03-30 - use python-colorlog
  * 2019-03-26 - NEW: {{{print_exc_plus()}}} - traceback with a listing of all the local variables
  * 2019-02-21 - Update email.py
  * 2019-02-21 - handle attachments/alternatives in unittest_utils.email.print_mailbox
* [v0.44.2](https://github.com/jedie/django-tools/compare/v0.44.1...v0.44.2)
  * 2019-01-02 - typo in docstring
  * 2019-01-02 - only code formatting
  * 2019-01-02 - work-a-round for: https://github.com/andymccurdy/redis-py/issues/995
  * 2019-01-02 - python3 + code formatting
* [v0.44.1](https://github.com/jedie/django-tools/compare/v0.44.0...v0.44.1)
  * 2019-01-02 - only code formatting
  * 2019-01-02 - Don't deactivate existing log handler, just append the buffer handler.
* [v0.44.0](https://github.com/jedie/django-tools/compare/v0.43.2...v0.44.0)
  * 2018-12-13 - NEW: {{{django_file = ImageDummy().create_django_file_info_image(text="")}}}
  * 2018-12-13 - mockup.ImageDummy: remove old API + make it useable without django-filer
* [v0.43.2](https://github.com/jedie/django-tools/compare/v0.43.1...v0.43.2)
  * 2018-12-11 - Bugfix Selenium refactor: Use the class with the same functionality if old usage places are used.
* [v0.43.1](https://github.com/jedie/django-tools/compare/v0.43.0...v0.43.1)
  * 2018-12-11 - v0.43.1 - Bugfix: Selenium test cases: clear window.localStorage after test run
* [v0.43.0](https://github.com/jedie/django-tools/compare/v0.42.4...v0.43.0)
  * 2018-12-11 - NEW: Selenium helper to access window.localStorage
  * 2018-12-11 - Split selenium test cases: with and without Django StaticLiveServerTestCase
  * 2018-12-11 - only code cleanup
  * 2018-12-11 - bugfix test_filter_and_log_warnings_create_warning()
  * 2018-12-11 - move selenium helpers
  * 2018-12-11 - add DeprecationWarning decorators
* [v0.42.4](https://github.com/jedie/django-tools/compare/v0.42.3...v0.42.4)
  * 2018-10-12 - bugfix: Some auth backends needs request object (e.g.: django-axes)
  * 2018-10-12 - only code cleanup
* [v0.42.3](https://github.com/jedie/django-tools/compare/v0.42.2...v0.42.3)
  * 2018-10-10 - v0.42.3
  * 2018-10-10 - update old tests
  * 2018-10-10 - ADD: assert is dir/file and assert_path_not_exists
* [v0.42.2](https://github.com/jedie/django-tools/compare/v0.42.1...v0.42.2)
  * 2018-09-18 - NEW: assert_installed_apps() - Check entries in settings.INSTALLED_APPS
  * 2018-09-18 - +DeprecationWarning
* [v0.42.1](https://github.com/jedie/django-tools/compare/v0.42.0...v0.42.1)
  * 2018-09-17 - release v0.42.1
  * 2018-09-17 - NEW: django_tools.unittest_utils.assertments.assert_language_code
* [v0.42.0](https://github.com/jedie/django-tools/compare/v0.41.0...v0.42.0)
  * 2018-09-07 - update tests
  * 2018-09-07 - v0.42.0
  * 2018-09-07 - move manage commands "list_models" and "nice_diffsettings"
  * 2018-09-07 - update README
  * 2018-09-07 - remove old Backwards-incompatible changes entries from README
  * 2018-09-07 - bugfix email tests
  * 2018-09-07 - remove all celery helper
  * 2018-09-06 - Create logging_info.py
  * 2018-09-05 - +print_celery_info()
  * 2018-09-05 - fixup! check if task runs async by check if returned obj is AsyncResult
  * 2018-09-05 - default change to not eager mode
  * 2018-09-05 - check if task runs async by check if returned obj is AsyncResult
  * 2018-09-05 - test_task() -> on_message_test_task()
  * 2018-09-05 - use async_result.wait() with timeout as work-a-round for: https://github.com/celery/celery/issues/5034
  * 2018-09-05 - +note about https://github.com/celery/celery/issues/5034
  * 2018-09-05 - work-a-round for https://github.com/celery/celery/issues/5033
  * 2018-09-05 - WIP: celery task unittest helpers
  * 2018-09-05 - pluggy>0.7 for https://github.com/pytest-dev/pytest/issues/3753
* [v0.41.0](https://github.com/jedie/django-tools/compare/v0.40.6...v0.41.0)
  * 2018-08-28 - v0.41.0
  * 2018-08-28 - update test project and tests
  * 2018-08-28 - add test assertments
  * 2018-08-28 - remove obsolete tests
  * 2018-08-28 - NEW: unittest_utils/assertments.py
  * 2018-08-28 - remove the @task_always_eager() decorator.
* [v0.40.6](https://github.com/jedie/django-tools/compare/v0.40.5...v0.40.6)
  * 2018-08-28 - v0.40.6
  * 2018-08-28 - code style update
  * 2018-08-28 - Bugfix @task_always_eager() decorator
* [v0.40.5](https://github.com/jedie/django-tools/compare/v0.40.4...v0.40.5)
  * 2018-08-27 - release 0.40.5
  * 2018-08-27 - Bugfix: Use given manage.py filename
* [v0.40.4](https://github.com/jedie/django-tools/compare/v0.40.3...v0.40.4)
  * 2018-08-21 - release v0.40.4
  * 2018-08-21 - +test default value +test delete value
  * 2018-08-21 - Update README.creole
  * 2018-08-21 - NEW: django_tools.debug.delay
* [v0.40.3](https://github.com/jedie/django-tools/compare/v0.40.2...v0.40.3)
  * 2018-07-18 - update README
  * 2018-07-18 - enhance selenium test cases
* [v0.40.2](https://github.com/jedie/django-tools/compare/v0.40.1...v0.40.2)
  * 2018-07-04 - release v0.40.2
  * 2018-07-04 - Fix tests, see: https://travis-ci.org/jedie/django-tools/jobs/400136378
  * 2018-07-04 - Skip own selenium tests, if driver not available
  * 2018-07-04 - Bugfix selenium Test Case if driver is None
  * 2018-07-04 - code cleanup
  * 2018-07-04 - add yapf style config
  * 2018-07-04 - Update for django API change
* [v0.40.1](https://github.com/jedie/django-tools/compare/v0.40.0...v0.40.1)
  * 2018-06-28 - Bugfix selenium test case if executable can't be found.
  * 2018-06-18 - Add django bug ticket links, too.
* [v0.40.0](https://github.com/jedie/django-tools/compare/v0.39.6...v0.40.0)
  * 2018-06-14 - +== try-out
  * 2018-06-14 - setup django requirements
  * 2018-06-14 - add example code into README
  * 2018-06-14 - +chromium_available() and firefox_available()
  * 2018-06-14 - update DocTests
  * 2018-06-14 - typo in "executable"
  * 2018-06-14 - try without "MOZ_HEADLESS=1" because "headless" set here:
  * 2018-06-14 - cleanup
  * 2018-06-14 - fixup! fix travis CI: install geckodriver
  * 2018-06-14 - fix travis CI: install geckodriver
  * 2018-06-14 - fixup! try to fix travis and chromedriver
  * 2018-06-14 - +SeleniumFirefoxTestCase and more docs
  * 2018-06-14 - try to fix travis and chromedriver
  * 2018-06-13 - fixup! try to find the webdriver executeable
  * 2018-06-13 - try to find the webdriver executeable
  * 2018-06-13 - +django-debug-toolbar
  * 2018-06-13 - Add selenium test cases, fix test project and tests
  * 2018-06-13 - just add admindocs and flatpages into test project settings
  * 2018-06-13 - better error messages
* [v0.39.6](https://github.com/jedie/django-tools/compare/v0.39.5...v0.39.6)
  * 2018-05-04 - README
  * 2018-05-04 - Don't hide Autofields
  * 2018-05-04 - code style cleanup
* [v0.39.5](https://github.com/jedie/django-tools/compare/v0.39.4...v0.39.5)
  * 2018-04-24 - +nargs="?"
  * 2018-04-24 - yield sorted
  * 2018-04-24 - we add "admin_tools"
  * 2018-04-24 - Update README.creole
  * 2018-04-24 - NEW: Model unittest code generator as admin action and manage command
  * 2018-04-24 - update pytest and use new --new-first
  * 2018-04-06 - clarify what CutPathnameLogRecordFactory does
* [v0.39.4](https://github.com/jedie/django-tools/compare/v0.39.3...v0.39.4)
  * 2018-04-06 - NEW: FilterAndLogWarnings and CutPathnameLogRecordFactory
* [v0.39.3](https://github.com/jedie/django-tools/compare/v0.39.2...v0.39.3)
  * 2018-03-22 - add kwarg 'exclude_actions' to get_filtered_permissions
* [v0.39.2](https://github.com/jedie/django-tools/compare/v0.39.1...v0.39.2)
  * 2018-03-22 - NEW: ParlerDummyGenerator + iter_languages
* [v0.39.1](https://github.com/jedie/django-tools/compare/v0.39.0...v0.39.1)
  * 2018-03-19 - ignore 'pypy3-django111' failure
  * 2018-03-19 - remove obsolete code
  * 2018-03-19 - return result from SendMailCelery().send()
  * 2018-03-19 - +test_SendMailCelery_more_mails()
  * 2018-03-19 - +django_tools.unittest_utils.email.print_mailbox()
  * 2018-03-11 - Update setup.py
* [v0.39.0](https://github.com/jedie/django-tools/compare/v0.38.9...v0.39.0)
  * 2018-03-02 - run tests with django 2.0 instead of django 1.8
  * 2018-03-02 - Bugfix for python <=3.5
  * 2018-03-02 - django_tools/unittest_utils/{celery.py => celery_utils.py}
  * 2018-03-02 - update history
  * 2018-03-02 - +Isolated Filesystem decorator / context manager
  * 2018-02-19 - +.pytest_cache
  * 2018-02-19 - update tests
  * 2018-02-19 - remove Py2 stuff
* [v0.38.9](https://github.com/jedie/django-tools/compare/v0.38.8...v0.38.9)
  * 2018-02-05 - lowering log level "error" -> "debug" on missing permissions
* [v0.38.8](https://github.com/jedie/django-tools/compare/v0.38.7...v0.38.8)
  * 2018-02-05 - release v0.38.8
  * 2018-02-05 - bugfix compare link
  * 2018-02-05 - use from celery import shared_task instead of djcelery_transactions
  * 2018-02-05 - +skip_missing_interpreters = True
  * 2018-01-19 - better error message if app label not found in get_filtered_permissions()
* [v0.38.7](https://github.com/jedie/django-tools/compare/v0.38.6...v0.38.7)
  * 2018-01-15 - Add missing arguments (like "attachments", "cc" etc.) to SendMailCelery
* [v0.38.6](https://github.com/jedie/django-tools/compare/v0.38.5...v0.38.6)
  * 2018-01-08 - update README
  * 2018-01-08 - add POST data to browser debug
  * 2018-01-08 - better sort
  * 2018-01-08 - remove duplicate entries from template list
  * 2018-01-03 - +./manage.py clear_cache
* [v0.38.5](https://github.com/jedie/django-tools/compare/v0.38.4...v0.38.5)
  * 2018-01-02 - +test_wrong_messages()
  * 2018-01-02 - NEW: assertMessages()
* [v0.38.4](https://github.com/jedie/django-tools/compare/v0.38.3...v0.38.4)
  * 2017-12-28 - Bugfix attach user group on existing user
* [v0.38.3](https://github.com/jedie/django-tools/compare/v0.38.2...v0.38.3)
  * 2017-12-28 - remove permissions, too
* [v0.38.2](https://github.com/jedie/django-tools/compare/v0.38.1...v0.38.2)
  * 2017-12-27 - add: ./manage.py update_permissions
  * 2017-12-27 - +Helper to start pytest with arguments
  * 2017-12-27 - use log.exception() if permission not found
* [v0.38.1](https://github.com/jedie/django-tools/compare/v0.38.0...v0.38.1)
  * 2017-12-21 - Update setup.py
  * 2017-12-20 - + coveralls
  * 2017-12-20 - cleanup
  * 2017-12-20 - use pypy3 ans -tox-travis
  * 2017-12-20 - refactor travis/tox/pytest
  * 2017-12-20 - don't test with unsupported django versions
  * 2017-12-20 - update travis/tox config and try to tests with more django versions
  * 2017-12-20 - Fix Tests, see:
  * 2017-12-20 - Update .travis.yml
* [v0.38.0](https://github.com/jedie/django-tools/compare/v0.37.0...v0.38.0)
  * 2017-12-19 - use python3
  * 2017-12-19 - +test_get_or_create_user_and_group()
  * 2017-12-19 - test with python 3.5 and 3.6
  * 2017-12-19 - update README
  * 2017-12-19 - work-around for https://github.com/travis-ci/travis-ci/issues/4794
  * 2017-12-19 - split user and group creation code
  * 2017-12-19 - +get_or_create_user_and_group()
  * 2017-12-14 - +BaseUnittestCase.get_admin_add_url()
  * 2017-12-13 - Bugfix tests
  * 2017-12-13 - NEW: BaseUnittestCase.get_admin_change_url()
  * 2017-12-13 - if print_filtered_html: print used template
  * 2017-12-12 - NEW: BaseUnittestCase.assert_startswith() and BaseUnittestCase.assert_endswith()
* [v0.37.0](https://github.com/jedie/django-tools/compare/v0.36.0...v0.37.0)
  * 2017-12-08 - +print_filtered_html
  * 2017-12-08 - add "dir" agument to debug_response()
  * 2017-12-07 - unify permission sort
  * 2017-12-07 - Use always the permission format from user.has_perm(): "<appname>.<codename>"
  * 2017-12-07 - NEW: get_filtered_permissions() and pprint_filtered_permissions()
  * 2017-12-05 - Bugfix TypeError: expected string or bytes-like object
  * 2017-12-05 - Bugfix ALLOWED_HOSTS support
  * 2017-12-05 - Add tests for django_tools.settings_utils.FnMatchIps
  * 2017-12-05 - rename InternalIps to FnMatchIps and make it useable for ALLOWED_HOSTS, too.
  * 2017-12-04 - Add DocString
  * 2017-12-04 - Skip official support for python v2 (remove from text matrix)
  * 2017-12-04 - Don't test with django 2.0, yet.
  * 2017-12-04 - fixup! +on_delete
  * 2017-12-04 - +on_delete
  * 2017-12-04 - refactor test user stuff
  * 2017-12-01 - NEW: ./manage.py permission_info
  * 2017-11-22 - Bugfix Py2
  * 2017-11-22 - update README
  * 2017-11-22 - create coverage html report
  * 2017-11-22 - bugfix/enhance permission stuff
  * 2017-11-22 - work-a-round for sqlite
  * 2017-11-22 - Raise AssertionError in DEBUG mode if permission doesn't exists
* [v0.36.0](https://github.com/jedie/django-tools/compare/v0.35.0...v0.36.0)
  * 2017-11-20 - +author_email
  * 2017-11-20 - Call also "./setup.py check"
  * 2017-11-20 - raise error also if "publish" command runs
  * 2017-11-20 - update "./setup.py publish" code
  * 2017-11-20 - Update README.creole
  * 2017-11-20 - Bugfix ModelPermissionMixin and add tests
  * 2017-11-20 - Bugfix DocTests
  * 2017-11-17 - completely deactivate dynamic site tests, see:
  * 2017-11-17 - Bugfix TestUserFixtures() compare
  * 2017-11-17 - Bugfix TestPermissions, see:
  * 2017-11-17 - unify path before assertment, see:
  * 2017-11-17 - fixup! Bugfix "database_info" test
  * 2017-11-17 - Bugfix "database_info" test
  * 2017-11-17 - display qslite module/lib version, too.
  * 2017-11-17 - add codecov.io badge
  * 2017-11-17 - +DocString tip
  * 2017-11-17 - mark "Dynamic SITE_ID middleware" as unmaintained
  * 2017-11-17 - Update .travis.yml
  * 2017-10-20 - NEW: "database_info" manage command
  * 2017-10-06 - Bugfix 'module' object has no attribute 'getLogRecordFactory' for Python < v3.2
  * 2017-10-06 - bugfix: https://travis-ci.org/jedie/django-tools/jobs/284216389
  * 2017-10-06 - try to fix dynamic site by clean cache?!?
  * 2017-10-06 - ADD: django_tools.unittest_utils.user.user_fixtures()
  * 2017-10-06 - nicer log output
  * 2017-10-04 - Bugfix ImageDummy.draw_centered_text() if text is multiline :(
  * 2017-09-28 - "migrate --list" was removed in django 1.10
  * 2017-09-28 - add some basic tests
  * 2017-09-28 - add isort config
  * 2017-09-28 - bugfix editorconfig: double config
* [v0.35.0](https://github.com/jedie/django-tools/compare/v0.34.0...v0.35.0)
  * 2017-09-26 - Refactor mockup picture creation
* [v0.34.0](https://github.com/jedie/django-tools/compare/v0.33.0...v0.34.0)
  * 2017-08-21 - Bugfix in mockup.create_pil_image: Created images has wrong sizes ;)
  * 2017-08-17 - Use django_tools.unittest_utils.user.create_user()
  * 2017-08-17 - Create test user via UserCreationForm to verify values
  * 2017-08-08 - Bugfix: usernames should not contain spaces ;)
* [v0.33.0](https://github.com/jedie/django-tools/compare/v0.32.14...v0.33.0)
  * 2017-07-11 - Update render_template_file() for Django v1.11
  * 2017-07-11 - fix travis
  * 2017-07-11 - Run tests only against Django 1.8TLS and 1.11TLS
  * 2017-07-11 - README, AUTHORS and set version to v0.32.15
  * 2017-07-07 - Add support for new-style middleware.
  * 2017-07-03 - NEW: django_tools.utils.request.create_fake_request()
  * 2017-07-03 - +install_requires "lxml"
  * 2017-06-30 - NEW: django_tools.utils.html_utils.html2text()
  * 2017-06-22 - Bugfix ModelPermissionMixin and add example to DocString
  * 2017-06-21 - WIP: ModelPermissionMixin
* [v0.32.14](https://github.com/jedie/django-tools/compare/v0.32.13...v0.32.14)
  * 2017-06-14 - installed by setup.py
  * 2017-06-14 - for Python 2 'mock" backport is needed ;)
* [v0.32.13](https://github.com/jedie/django-tools/compare/v0.32.12...v0.32.13)
  * 2017-05-24 - add used requirements files ;)
  * 2017-05-24 - update editorconfig
  * 2017-05-24 - remove some test run warnings and cleanup
* [v0.32.12](https://github.com/jedie/django-tools/compare/v0.32.11...v0.32.12)
  * 2017-05-04 - +unicode_literals
  * 2017-05-04 - fix tests for Python 2
  * 2017-05-04 - NEW: self.assertIn_dedent()
* [v0.32.11](https://github.com/jedie/django-tools/compare/v0.32.10...v0.32.11)
  * 2017-05-02 - refactor
* [v0.32.10](https://github.com/jedie/django-tools/compare/v0.32.9...v0.32.10)
  * 2017-05-02 - remove old PyDev configs
  * 2017-05-02 - move __version__
  * 2017-05-02 - cleanup README
  * 2017-05-02 - Update README.creole
  * 2017-05-02 - assert that manage.py is executeable
  * 2017-05-02 - update meta files
  * 2017-05-02 - +django_tools.mail
  * 2017-04-25 - It's a IndexError if no user exists ;)
  * 2017-03-23 - add README
* [v0.32.9](https://github.com/jedie/django-tools/compare/v0.32.8...v0.32.9)
  * 2017-03-21 - bugfxi test: exclude line number ;)
  * 2017-03-21 - add "template doesn't exists" test
  * 2017-03-21 - fixup! Bugfix if TemplateDoesNotExist was raised
  * 2017-03-21 - Bugfix if TemplateDoesNotExist was raised
* [v0.32.8](https://github.com/jedie/django-tools/compare/v0.32.7...v0.32.8)
  * 2017-03-16 - bugfix: remove request after exception
  * 2017-03-16 - +=== django_tools.template.loader.DebugCacheLoader
  * 2017-03-16 - fix unittests
  * 2017-03-16 - don't set max. version number
  * 2017-03-16 - cleanup
  * 2017-03-16 - Add debug template loader that add template name as html comment
  * 2017-03-15 - update temp file prefix and cleanup
* [v0.32.7](https://github.com/jedie/django-tools/compare/v0.32.6...v0.32.7)
  * 2017-03-10 - + django_tools.permissions
  * 2017-03-10 - cleanup
  * 2017-03-06 - Use: unittest_utils.user.create_user() in tests
  * 2017-03-03 - +=== create users
  * 2017-03-03 - NEW: django_tools.unittest_utils.user
* [v0.32.6](https://github.com/jedie/django-tools/compare/v0.32.5...v0.32.6)
  * 2017-02-22 - set CELERY_EAGER_PROPAGATES_EXCEPTIONS=True, too
* [v0.32.5](https://github.com/jedie/django-tools/compare/v0.32.4...v0.32.5)
  * 2017-02-10 - Add 'template_name' to 'assertResponse'
  * 2017-02-10 - add assertResponse() test
* [v0.32.4](https://github.com/jedie/django-tools/compare/v0.32.3...v0.32.4)
  * 2017-02-01 - test "create users"
  * 2017-02-01 - Bugfix: set active flag on test users
  * 2017-01-25 - Doesn't work in every case, but has been worked, see:
* [v0.32.3](https://github.com/jedie/django-tools/compare/v0.32.2...v0.32.3)
  * 2017-01-25 - just a helper to start pytest
  * 2017-01-25 - +@task_always_eager() decorator
  * 2017-01-25 - django-filer v1.2.6 was released
  * 2017-01-25 - fix import error with python v2
  * 2017-01-25 - ADD unittest helper '@task_always_eager()'
  * 2017-01-25 - fix tests
  * 2017-01-25 - refactor TemplateInvalidMixin to @set_string_if_invalid() decorator
  * 2017-01-25 - +TemplateInvalidMixin
  * 2017-01-25 - NEW: TemplateInvalidMixin
  * 2017-01-19 - Fix UnicodeDecodeError in BrowserDebug
* [v0.32.2](https://github.com/jedie/django-tools/compare/v0.32.1...v0.32.2)
  * 2017-01-13 - link to testfile
  * 2017-01-13 - NEW: django_tools.utils.url.GetDict
* [v0.32.1](https://github.com/jedie/django-tools/compare/v0.32.0...v0.32.1)
  * 2016-12-29 - +TracebackLogMiddleware
* [v0.32.0](https://github.com/jedie/django-tools/compare/v0.31.0...v0.32.0)
  * 2016-12-19 - NEW: django_tools.template.render.render_template_file
  * 2016-12-19 - typo
  * 2016-12-09 - whitespace cleanup
  * 2016-12-09 - + @display_admin_error
  * 2016-12-08 - change to app_label.ModelName format
  * 2016-12-08 - +manage commands: nice_diffsettings & list_models
  * 2016-12-08 - +cov
  * 2016-12-08 - update tests
  * 2016-12-08 - run pytest
  * 2016-12-08 - remove doctest + cleanup
  * 2016-12-08 - move doctests to unittests
  * 2016-12-08 - remove outdated stuff
  * 2016-12-07 - about pytest
  * 2016-12-07 - WIP: use pytest-django
* [v0.31.0](https://github.com/jedie/django-tools/compare/v0.30.4...v0.31.0)
  * 2016-11-03 - move tests
  * 2016-11-03 - work-a-round for https://github.com/divio/django-filer/issues/899
  * 2016-11-03 - Update .travis.yml
  * 2016-11-03 - fix test: domain name provided is not valid according to RFC 1034/1035
  * 2016-11-03 - add Mockup utils to create dummy PIL/django-filer images with Text
  * 2016-10-28 - fix tests:
* [v0.30.4](https://github.com/jedie/django-tools/compare/v0.30.3...v0.30.4)
  * 2016-10-27 - enhance DjangoCommandMixin:
* [v0.30.3](https://github.com/jedie/django-tools/compare/v0.30.2...v0.30.3)
  * 2016-10-27 - +requirements-dev.txt
  * 2016-10-27 - +.../django-tools $ tox
  * 2016-10-27 - +DjangoCommandMixin
  * 2016-10-27 - +django_tools.unittest_utils.django_command
* [v0.30.2](https://github.com/jedie/django-tools/compare/v0.30.1...v0.30.2)
  * 2016-10-05 - Bugfix Python 2 compatibility
  * 2016-09-13 - Update language classifiers to show python 3 support.
* [v0.30.1](https://github.com/jedie/django-tools/compare/v0.30.0...v0.30.1)
  * 2016-08-26 - allways coverage
  * 2016-08-26 - update README
  * 2016-08-26 - fix unittests for django v1.10
  * 2016-08-26 - fix tox/travis settings
  * 2016-08-26 - use tox in travis
  * 2016-08-26 - v0.30.1 add 'DisableMigrations'
* [v0.30.0](https://github.com/jedie/django-tools/compare/v0.29.5...v0.30.0)
  * 2016-04-27 - v0.30.0
  * 2016-04-27 - update from:
  * 2016-04-27 - add naegelyd
  * 2016-04-04 - Remove unused django.utils.unittest import
  * 2016-04-04 - Revert "Add flake8 to the local and Travis CI test process"
  * 2016-04-04 - Use ranges for Django versions in tox file
  * 2016-04-02 - Add Python 3.4 to the tox envlist
  * 2016-04-02 - Make sure setUpClass and tearDownClass call super methods
  * 2016-04-02 - Update SQL test for Django 1.9
  * 2016-04-02 - Use Python's importlib instead of Django's
  * 2016-04-02 - Use Django 1.9 compatible cache accessor
  * 2016-04-02 - Just use Python's logging module instead of django.utils.log
  * 2016-04-02 - Ignore the raw_input reference in flake8
  * 2016-04-02 - Only reference raw_input when using Python 2
  * 2016-04-02 - Use Python 3 compatible open() to open file for write
  * 2016-04-02 - Use Python 3 compatible sort kwarg
  * 2016-04-01 - Update version to 0.30.0
  * 2016-04-01 - Add flake8 to the local and Travis CI test process
  * 2016-04-01 - Redirect both stdout and stderror like warning message says
  * 2016-04-01 - Limit supported Django versions to 1.8 and 1.9
  * 2016-04-01 - Fix filemanage subdir test
  * 2016-04-01 - Construct the absolute URL from the base and rest URLs
  * 2016-04-01 - Remove unnecessary assignment of rest_path
  * 2016-04-01 - Use  module instead of /Users/donald/Sites/django-tools for group name retrieval
  * 2016-04-01 - Fix and remove broken BaseFilesystemBrowser tests
  * 2016-04-01 - Use self.absolute_path instead of missing self.abs_path
  * 2016-04-01 - Add tox file
  * 2016-04-01 - Add coverage_html to .gitignore
  * 2016-04-01 - Ignore PyDev IDE files
  * 2016-02-29 - Update README.creole
* [v0.29.5](https://github.com/jedie/django-tools/compare/v0.29.4...v0.29.5)
  * 2015-08-11 - +@python_2_unicode_compatible
* [v0.29.4](https://github.com/jedie/django-tools/compare/v0.29.3...v0.29.4)
  * 2015-08-11 - update from:
  * 2015-08-11 - --source=django_tools
  * 2015-08-11 - remove debug print
  * 2015-08-10 - TODO: all should work!
  * 2015-08-10 - Speedup tests
  * 2015-08-10 - Don't mixin SimpleTestCase
  * 2015-08-10 - simpler solution to run tests
  * 2015-08-10 - http://docs.travis-ci.com/user/migrating-from-legacy/
  * 2015-08-10 - Skip test in django 1.6
  * 2015-08-10 - turn off logging in unittests
  * 2015-08-10 - Install latest minor release of django
  * 2015-08-10 - upgrade pip and see which django version will be installed
  * 2015-08-10 - Bugfix for:
  * 2015-08-10 - Fix some unittests imports for django 1.6
  * 2015-08-10 - bugfix import for older django version and cleanup
  * 2015-08-10 - country code will be change
  * 2015-08-10 - run tests with django 1.6, too
  * 2015-08-10 - update utils.http for older django versions and add unittests
  * 2015-08-10 - bugfix running test in older django versions
  * 2015-08-10 - Bugfix for older django version
  * 2015-08-10 - remove old google links
* [v0.29.3](https://github.com/jedie/django-tools/compare/v0.29.2...v0.29.3)
  * 2015-08-08 - Clean up spelling and grammar
  * 2015-08-08 - Add myself to authors for https://github.com/jedie/django-tools/pull/7
  * 2015-08-07 - Fix weird capitalization in test name
  * 2015-08-07 - Fix bytes to str conversion for python 3 compatibility
  * 2015-08-07 - Bump version to reflect changed behavior
  * 2015-08-07 - Fix failing tests by removing the _thread_locals.request variable when the response is processed
  * 2015-08-07 - Add failing test for when exceptions are raised in the view
  * 2015-08-07 - Add failing test that _thread_locals.current_request is cleared after request-response cycle completes
  * 2015-08-07 - Correct typos in documentation
  * 2015-07-02 - +donation
  * 2015-06-19 - code cleanup
* [v0.29.2](https://github.com/jedie/django-tools/compare/v0.29.1...v0.29.2)
  * 2015-06-19 - release v0.29.2
  * 2015-06-19 - doesn't help in every cases :(
  * 2015-06-17 - add QueryLogMiddleware - TODO: test it!
  * 2015-06-17 - use existing assertContains / assertNotContains
  * 2015-06-17 - typo in docstring
  * 2015-06-17 - Check if user exist and raise helpfull message
  * 2015-06-17 - 0.29.2.dev0
  * 2015-06-17 - render nicer
* [v0.29.1](https://github.com/jedie/django-tools/compare/v0.29.0...v0.29.1)
  * 2015-06-17 - add StdoutStderrBuffer() to README and release as v0.29.1
  * 2015-06-17 - add links to github compare views
  * 2015-06-16 - bugfix for Py2 and Py3
  * 2015-06-16 - Bugfix if django 1.8 is used: SELECT COUNT(%s) AS...
  * 2015-06-16 - Use CaptureQueriesContext in PrintQueries and add unittest
  * 2015-06-16 - accept running subset of unittests
  * 2015-06-16 - +example
  * 2015-06-10 - use twine to upload
  * 2015-06-10 - WIP: use 'twine' for upload to PyPi
  * 2015-06-10 - add StdoutStderrBuffer()
  * 2015-06-10 - remove obsolete code
* [v0.29.0](https://github.com/jedie/django-tools/compare/v0.26.1...v0.29.0)
  * 2015-06-08 - temporary: deactivate DocTests
  * 2015-06-08 - remove non ASCII
  * 2015-06-08 - fix doctest for py2
  * 2015-06-08 - works in Py2 and Py3
  * 2015-06-08 - remove unused DocTests (unittests exists)
  * 2015-06-08 - run DocTests, too. But currently with unittest.expectedFailure()
  * 2015-06-08 - use ExistingDirValidator in BaseFilesystemBrowser
  * 2015-06-08 - +BaseUnittestCase and +TempDir
  * 2015-06-08 - Bugfix imports
  * 2015-06-08 - Bugfix for Py2
  * 2015-06-08 - +SignedCookieStorage in README
  * 2015-06-08 - ClientCookieStorage -> SignedCookieStorage
  * 2015-06-08 - TestGetFilteredApps
  * 2015-06-08 - catch more directory traversal attacks in BaseFilesystemBrowser
  * 2015-06-08 - Bugfix missing import
  * 2015-06-08 - +repo_token
  * 2015-06-08 - WIP: refactor tests
  * 2015-06-08 - WIP: travis, coveralls, landscape
  * 2015-06-08 - update .gitignore
  * 2015-03-27 - add InternalIps() - Unix shell-style wildcards in INTERNAL_IPS
  * 2015-03-04 - Bugfixes in **dynamic_site** for django 1.7
  * 2015-02-19 - add SECRET_KEY for unittests
  * 2015-02-19 - Bugfix for "django.core.exceptions.AppRegistryNotReady: Models aren't loaded yet." if using **UpdateInfoBaseModel**
  * 2015-02-12 - new Version number, because of PyPi stress
* [v0.26.1](https://github.com/jedie/django-tools/compare/v0.26.0...v0.26.1)
  * 2015-02-12 - Work-a-round for import loops
* [v0.26.0](https://github.com/jedie/django-tools/compare/v0.25.0...v0.26.0)
  * 2015-02-11 - relase as v0.26.0
  * 2015-02-11 - some Python 2 vs 3 compatiblity fixes
  * 2015-02-11 - log only an error, instead of raise AssertionError
  * 2014-10-02 - WIP: Just run 2to3
  * 2014-10-02 - "Django>=1.5,<1.8"
  * 2014-10-02 - WIP: Just add __future__ import
  * 2014-10-02 - update setup.py
  * 2014-04-14 - Update models.py
  * 2013-11-18 - update README
  * 2013-11-18 - fallback to "utf-8" if no encoding given
  * 2013-11-12 - Update README.creole
  * 2013-07-23 - from django.conf.urls.defaults import... -> from django.conf.urls import...
  * 2013-07-19 - add requires "Django>=1.5,<1.6" in setup.py
  * 2013-07-19 - Update URLValidator2 for django 1.5: verify_exists was removed with https://github.com/django/django/commit/9ed6e08ff99c18710c0e4875f827235f04c89d76
  * 2013-07-19 - move/add logging info into README
  * 2012-10-23 - correct README
  * 2012-10-23 - Better example
  * 2012-08-31 - wrong url
  * 2012-08-31 - update DocString
  * 2012-08-31 - split contact info
* [v0.25.0](https://github.com/jedie/django-tools/compare/v0.24.10...v0.25.0)
  * 2012-08-28 - v0.25 - SmoothCacheBackends API changed: Rename **cache.clear()** to **cache.smooth_update()**
* [v0.24.10](https://github.com/jedie/django-tools/compare/v0.24.8...v0.24.10)
  * 2012-08-24 - v0.24.10: * add SmoothCacheBackends * set AutoUpdateFileBasedCache as deprecated
  * 2012-08-24 - disable logging as default
  * 2012-08-24 - Better solution if cache entry doesn't exists.
  * 2012-08-24 - disable debug
  * 2012-08-24 - revert to saver method
* [v0.24.8](https://github.com/jedie/django-tools/compare/v0.24.6...v0.24.8)
  * 2012-08-24 - release v0.24.8
  * 2012-08-23 - no released, yet.
  * 2012-08-23 - Store some startus information about the cache usage.
  * 2012-08-22 - v0.24.8.pre: Add **SetRequestDebugMiddleware**
  * 2012-08-21 - * Add per-site cache middleware * Add import lib helper
* [v0.24.6](https://github.com/jedie/django-tools/compare/v0.20.0...v0.24.6)
  * 2012-08-21 - Move filemanager library from PyLucid: https://github.com/jedie/PyLucid/tree/d825cf73c8bb0005ff3a00721a5dae9c595c2420/pylucid_project/filemanager
  * 2012-08-07 - Update README.creole
  * 2012-08-06 - Add **Print SQL Queries** context manager.
  * 2012-07-26 - add some dates in changelist
  * 2012-07-26 - remove date from version string cause of side-effects e.g.: user clone the repo and has the filter not installed
  * 2012-07-26 - ignore error, if date not exists
  * 2012-07-25 - * "hardcode" the committer date in version number * see: https://github.com/jedie/django-tools/issues/1
  * 2012-07-10 - Split UpdateInfoBaseModel(): So you can only set "createtime", "lastupdatetime" or "createby", "lastupdateby" or both types
  * 2012-06-26 - we use it in PyLucid CMS. Add notes about limitations.
  * 2012-06-12 - * Add unittests for limit_to_usergroups * Add a test project. TODO: use this for all tests
  * 2012-06-12 - Add create_user() and create_testusers() to BaseTestCase
  * 2012-06-12 - Add normal users in UsergroupsModelField()
  * 2012-06-12 - Bugfix in UsergroupsModelField()
  * 2012-06-04 - Bugfix: wrong variable name :(
  * 2012-05-31 - start v0.24
  * 2012-05-31 - Don't use auto_now_add and auto_now
  * 2012-05-31 - * Update DocStrings * Add info: SQLite supports UNIQUE since 2.0 (from 2001) * Use new settings.DATABASES scheme first
  * 2012-05-14 - update link (for ReSt)
  * 2012-05-09 - * Do initial stuff only if settings.USE_DYNAMIC_SITE_MIDDLEWARE == True * Give better feedback, if FALLBACK_SITE_ID doesn't exists.
  * 2012-05-03 - v0.23.0 - Use cryptographic signing tools from django 1.4 in django_tools.utils.client_storage
  * 2012-04-24 - TODO: Use https://docs.djangoproject.com/en/1.4/topics/signing/ !
  * 2012-04-24 - "soc2011 form-rendering" si merged in django v1.4: assertContains() -> https://docs.djangoproject.com/en/1.4/topics/testing/#django.test.TestCase.assertContains assertHTMLEqual() -> https://docs.djangoproject.com/en/1.4/topics/testing/#django.test.SimpleTestCase.assertHTMLEqual
  * 2012-04-24 - add change info from https://github.com/jedie/django-tools/commit/9e984e09399644371a8e489b360a2ff8f83bd267
  * 2012-04-24 - * v0.22.0 ** Add static_path.py thats used settings.STATIC_ROOT. ** The old media_path.py which used settings.MEDIA_ROOT is deprecated and will be removed in the future.
  * 2012-04-23 - support django old and new DATABASE settings syntax
  * 2012-01-25 - Update readme examples
  * 2012-01-25 - Bugfixes in Dynamic Site
  * 2012-01-24 - small readme update
  * 2012-01-24 - Update readme
  * 2012-01-24 - * v0.21.0beta ** New: site alias function ** refractory 'DynamicSiteMiddleware' to a own app (**Backwards-incompatible change:** change your settings if you use the old DynamicSiteMiddleware.)
  * 2012-01-24 - add PyDev project file, for easier import in eclipse/aptana studio
  * 2012-01-09 - Add **untestet** and experimental \"auto update\" cache backend. Discuss in german here: http://www.python-forum.de/viewtopic.php?f=7&t=28227
  * 2012-01-06 - Update README/Version string
  * 2012-01-06 - NEW: debug_csrf_failure(): Display the normal debug page and not the minimal csrf debug page.
  * 2012-01-04 - better solution in example.
  * 2012-01-04 - * Bugfix for fallback ID: os environment variables are always strings * enable logging in unittests * add notes about unittests
  * 2012-01-02 - miss spell
* [v0.20.0](https://github.com/jedie/django-tools/compare/caeaaf4...v0.20.0)
  * 2012-01-02 - set version to v0.20.0
  * 2012-01-02 - Add DynamicSiteMiddleware to README
  * 2012-01-02 - use logging
  * 2012-01-02 - * Middleware must be activated with settings.USE_DYNAMIC_SITE_MIDDLEWARE = True * deactivate debug prints * code cleanup
  * 2012-01-01 - code cleanup
  * 2011-12-29 - NEW: Dynamic SITE ID - experimental, yet!
  * 2011-10-09 - cleanup
  * 2011-10-09 - Add middlewares/ThreadLocal.py
  * 2011-09-26 - Add south introspection rules
  * 2011-09-26 - Bugfix in django_tools.utils.messages.StackInfoStorage
  * 2011-09-23 - Add some south introspection rules for LanguageCodeModelField and jQueryTagModelField
  * 2011-09-13 - fallback if message for anonymous user can't created, because django.contrib.messages middleware not used.
  * 2011-09-07 - Add http://bugs.python.org/file22767/hp_fix.diff for https://github.com/gregmuellegger/django/issues/1
  * 2011-09-12 - bugfix
  * 2011-09-06 - relase as v0.19.4
  * 2011-09-06 - Nicer solution for template.filters.human_duration()
  * 2011-09-06 - Bugfix in template.filters.chmod_symbol()
  * 2011-08-31 - changes since python-creole 0.8.1, see: https://code.google.com/p/python-creole/wiki/UseInSetup
  * 2011-08-30 - update README
  * 2011-08-26 - Better solution for setup.long_description since python-creole v0.8, more info: https://code.google.com/p/python-creole/wiki/UseInSetup
  * 2011-08-26 - UnicodeEncodeError running pip install (which runs './setup.py egg_info')
  * 2011-08-15 - add example import
  * 2011-08-15 - Bugfix for PyPy in local_sync_cache get_cache_information(): sys.getsizeof() not implemented on PyPy
  * 2011-08-10 - v0.19.3 - Add support for https in utils/http.py
  * 2011-08-10 - missing socket import and typo
  * 2011-08-10 - Use timeout and add a work-a-round for Python < 2.6
  * 2011-08-10 - Better solution, see: http://www.python-forum.de/viewtopic.php?p=204899#p204899 (de)
  * 2011-08-09 - add PyPi url
  * 2011-08-09 - cleanup readme
  * 2011-08-09 - change version to 0.19.0
  * 2011-08-09 - Change README from textile to creole ;)
  * 2011-08-09 - NEW: Add utils/http.py with helpers to get a webpage via http GET in unicode
  * 2011-08-09 - merge rules
  * 2011-08-08 - Disable default stdout logging in \"runserver\" mode and make the check easier.
  * 2011-07-14 - spell error :(
  * 2011-07-14 - Bugfix: Add missing template in pypi package
  * 2011-07-13 - * Warn user for https://github.com/pypa/pip/issues/319 * user must explicit continue if pip is outdated
  * 2011-07-12 - Check if pip it out-dated.
  * 2011-07-12 - turn dry-run into a commandline options and add --verbose and --log options
  * 2011-07-12 - add \"dry-run\" mode
  * 2011-07-12 - some nicer output
  * 2011-07-12 - Don't activate virtualenv: Check on start, if env activated.
  * 2011-07-12 - v0.18 - Add DOM compare in unittests from the gread work of Gregor Müllegger at his GSoC 2011 form-rendering branch: https://github.com/gregmuellegger/django/tree/soc2011/form-rendering
  * 2011-07-12 - Bugfix: Don't escape twice
  * 2011-07-11 - escape html code in traceback.
  * 2011-07-08 - Bugfix in \"limit_to_usergroups\": Make choices \"lazy\": Don't access the database in __init__
  * 2011-07-08 - textile typo ;)
  * 2011-07-08 - add some info to README
  * 2011-07-08 - remove \"pre\" from version -> relase this version
  * 2011-07-08 - Add the script \"upgrade_virtualenv.py\", see also: https://github.com/pypa/pip/issues/59
  * 2011-07-06 - Don't check if it's int() try to convert to int() (e.g.: We get a 'long' back from MySQL)
  * 2011-07-06 - Bugfix in has_permission()
  * 2011-07-06 - Add \"Limit to usergroups\".
  * 2011-07-06 - Add some counters to LocalSyncCache and a pformat_cache_information() function.
  * 2011-07-05 - Add get_cache_information() (used in PyLucid)
  * 2011-07-05 - better logging example
  * 2011-07-05 - * Add documentation for \"Local sync cache\" * Use own cache backend, if exists * Store the last clear() time and restore it in django cache, if not exists * add some logging output
  * 2011-07-04 - Add \"local sync cache\"
  * 2011-06-30 - new argument \"skip_fail\" in get_filtered_apps(): If True: raise excaption if app is not importable
  * 2011-06-30 - render_to pass keyword arguments to render_to_response() (e.g.: mimetype=\"text/plain\")
  * 2011-06-15 - Don't use the first argument as request. Check all arguments. So @render_to is useable in classes, too. (Needs more tests)
  * 2011-06-14 - * Add models.UpdateInfoBaseModel * Update decorators.render_to
  * 2011-05-17 - for tests
  * 2011-05-17 - change version string
  * 2011-05-17 - v0.16.4 ** Bugfix: \"\"\"get_db_prep_save() got an unexpected keyword argument 'connection'\"\"\" when save a SignSeparatedModelField()
  * 2011-05-16 - v0.16.3 ** Update BrowserDebug: Use response.templates instead of response.template and make output nicer
  * 2011-04-11 - add it right
  * 2011-04-11 - bugfix: add error message
  * 2011-04-11 - Merge stack info code and display better stack info on browser debug page
  * 2011-04-11 - Update django_tools.utils.messages.StackInfoStorage for django code changes.
  * 2011-03-04 - v0.16.0 - NEW: path model field (check if direcotry exist) TODO: 1. Needs more tests! 2. implement the widget
  * 2011-02-25 - v0.15.0 ** NEW: Add a flexible URL field (own validator, model- and form-field)
  * 2010-12-21 - v0.14.1 -> Bugfix: make path in MediaPathModelField relativ (remove slashes)
  * 2010-12-08 - v0.14 - NEW: django-tagging addon: Display existing tags under a tag field
  * 2010-12-08 - cleanup DocString
  * 2010-11-22 - Add complete settings into browser debug page.
  * 2010-09-30 - Bugfix UnicodeEncodeError in Browser debug
  * 2010-09-28 - catch errors in setup.py
  * 2010-09-16 - include README.textile in MANIFEST.in Thanks Sridhar Ratna for reporting it: http://code.google.com/p/django-tools/issues/detail?id=3
  * 2010-09-14 - display user messages in browser debug
  * 2010-09-14 - * NEW: django_tools.utils.messages.failsafe_message * catch if MEDIA_ROOT is not accessable * add commit timestamp to version string
  * 2010-09-14 - diable debug print's by default
  * 2010-08-25 - NEW: Store data in a secure cookie, see: utils/client_storage.py
  * 2010-08-24 - use pformat for listing templates
  * 2010-08-24 - change version string to v0.10.1
  * 2010-08-24 - bugfix if templates doesn't exist
  * 2010-08-24 - Display used templates in unittest BrowserDebug
  * 2010-08-24 - catch if last message doesn't exist
  * 2010-07-08 - display debug info
  * 2010-07-02 - chmod +x update.sh
  * 2010-07-02 - add update.sh an info to README
  * 2010-07-01 - add utils around django messages
  * 2010-06-18 - Bugfix: database column was not created: don't overwrite get_internal_type()
  * 2010-06-18 - change README filename
  * 2010-06-18 - * v0.9 ** New: stuff in /django_tools/fields/ ** see also backwards-incompatible changes, above!
  * 2010-06-16 - remove os.walk followlinks argument (it's new in python 2.6)
  * 2010-06-15 - New: django_tools.widgets.SelectMediaPath(): Select a sub directory in settings.MEDIA_ROOT and new: SignSeparatedField
  * 2010-06-15 - Add "no_args" keyword argument to installed_apps_utils.get_filtered_apps()
  * 2010-04-09 - mere some unittest code and add more infos.
  * 2010-04-01 - info print: don't display same fileinfo again.
  * 2010-04-01 - bugfix in info print: add flush() method.
  * 2010-03-31 - * add: BaseTestCase.add_user_permissions() * better error message, if test usertype is wrong
  * 2010-03-25 -  * Add model LanguageCode field and form LanguageCode field in Accept-Language header format (RFC 2616)  * rename dir "unittest" to "unittest_utils"  * Change version scheme
  * 2010-03-17 - use absolute path to AUTHORS and README
  * 2010-03-05 - Add decorators.py
  * 2009-11-25 -  * human_duration(): add hours  * Add DocTest
  * 2009-08-20 - v0.6.0 - Add forms_utils.LimitManyToManyFields, crosspost: http://www.djangosnippets.org/snippets/1691/
  * 2009-08-18 - - v0.5.0
  * 2009-08-10 - remove settings import: Better if info print used in settings himself ;)
  * 2009-08-10 -  * add: assertStatusCode(): assert response status code, if wrong, do a browser traceback.  * add: assertRedirect(): assert than response is a redirect to the right destination, if wrong, do a browser traceback.
  * 2009-08-05 - add url to exception message
  * 2009-07-14 - update version info + history
  * 2009-07-14 - add usage example.
  * 2009-07-14 - add experimental "warn_invalid_template_vars"
  * 2009-07-14 - add get_filtered_apps(): Filter settings.INSTALLED_APPS and create a list of all Apps witch can resolve the given url >resolve_url<
  * 2009-07-14 - Bugfix: Exclude the instance if it was saved in the past.
  * 2009-07-14 - simpler browser_traceback
  * 2009-07-13 - skip check, if a necessary field is missing.
  * 2009-07-13 - Add models_utils, see: http://www.jensdiemer.de/_command/118/blog/detail/67/ (de)
  * 2009-06-18 - add get_current_user()
  * 2009-06-17 - add threadlocals middleware
  * 2009-06-17 - Add info_print:
  * 2009-06-16 - add "SlowerDevServer": Simple slow down the django developer server. The middleware insert in every 200 response a time.sleep
  * 2009-05-27 - Bugfix: use smart_str in assertResponse (encoding errors e.g.: running in terminal)
  * 2009-05-14 - add missing __init__.py ;)
  * 2009-05-14 - template render tools
  * 2009-05-12 - add "_headers" to response info list
  * 2009-05-07 - Use normal unittest.TestCase and add direct_run() function.
  * 2009-05-07 - add __init__.py
  * 2009-05-07 - rename directory
  * 2009-05-07 -  * add unittest stuff from http://code.google.com/p/django-dbpreferences/  * add initial stuff

</details>


[comment]: <> (✂✂✂ auto generated history end ✂✂✂)

## links

| Homepage | [https://github.com/jedie/django-tools](https://github.com/jedie/django-tools)           |
| PyPi     | [https://pypi.python.org/pypi/django-tools/](https://pypi.python.org/pypi/django-tools/) |

## donation


* [paypal.me/JensDiemer](https://www.paypal.me/JensDiemer)
* [Flattr This!](https://flattr.com/submit/auto?uid=jedie&url=https%3A%2F%2Fgithub.com%2Fjedie%2Fdjango-tools%2F)
* Send [Bitcoins](https://www.bitcoin.org/) to [1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F](https://blockexplorer.com/address/1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F)
