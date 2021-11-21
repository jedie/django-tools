# Django-Tools -  Mode Version Protect

Protect a model against overwriting a newer entry with an older one, by adding a auto increment version number.

## Problem

If you work in Django Admin with more than one Browser Tabs,
then it can happen that the user loses the overview and has the same object open in two tabs.
Maybe one tab contains a older version than the current version in database.

Normally the user is not protect to overwrite a newer version with the old one, because
he an Django can't see the state of the model.

## Solution

`VersionProtectBaseModel` model will add a auto increment `version` number to every instance
and raise `ValidationError` in `full_clean()` if a older version should be saved.

Note: `VersionProtectBaseModel` will call `full_clean()` in `save()` if not done before!

## Usage

change settings:

```
INSTALLED_APPS = (
    ...
    'django_tools.model_version_protect.apps.ModelVersionProtectConfig',
    ...
)
```

Use it as model mixin, e.g.:
```
class FooBarModel(VersionProtectBaseModel):
    name = models.CharField(max_length=100)
```

## Examples

Test project model `VersioningTestModel` is here: django_tools_test_project/django_tools_test_app/models.py
Tests are here: django_tools/model_version_protect/tests/*.py

How a admin overwrite error looks, can you see here: django_tools/model_version_protect/tests/test_admin_basic_2.snapshot.html
