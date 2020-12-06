# Django-Tools - Serve User Media File

The `django_tools.serve_media_app` django app serves `settings.MEDIA_ROOT` file requests only for allowed users. So you can limit the access to these files.

The idea is, that `settings.STATIC_ROOT` is for public files (css, js etc) and should be served by the web server.
`settings.MEDIA_ROOT` is not public and served by the django application to restrict the access to active user session.

Files are stored in these file path:

```
/{settings.MEDIA_ROOT}/{random-user-token}/{random-file-token}/
```

Example:

```
/media/w7tytv3lyupc/fm4kf9hp0c_vfx3onskrffw1/filename.ext
```

The `{random-user-token}` will be created automatically via signals and stored into `django_tools.serve_media_app.models.UserMediaTokenModel` to identify the owner of the requested file.


Limitations:

* Works currently only for `FileSystemStorage`
* Dosen't support faster `sendfile` solution

The files served by streaming HTTP response. But serve files from the application is slow.
It's faster to use `sendfile` from the web server.
Maybe use https://pypi.org/project/django-sendfile2/


## usage


settings:
```
INSTALLED_APPS = (
    # ...
    'django_tools.serve_media_app.apps.UserMediaFilesConfig',
    # ...
)
```


urls:
```
urlpatterns = [
    # ...
    path(settings.MEDIA_URL.lstrip('/'), include('django_tools.serve_media_app.urls')),
    # ...
]
```
(See: `django_tools_test_project/urls.py`)


You can use it in models like this (optional):
```
from django_tools.serve_media_app.models import user_directory_path

class ExampleModel(models.Model):
    user = models.ForeignKey(  # "Owner" of this entry, field name must be "user" !
        settings.AUTH_USER_MODEL,
        related_name='+',
        on_delete=models.CASCADE,
    )
    # e.g.:
    foo = models.FileField(upload_to=user_directory_path)
    bar = models.ImageField(upload_to=user_directory_path)
```
(see: ```django_tools_test_project.django_tools_test_app.models.UserMediaFiles```)

Note: The model will not checked in file request!
You can add own access checks by signals, e.g.:
```
from django_tools.serve_media_app.views.serve_user_files import serve_file_request

def access_callback(user, path, media_path, **kwargs):
    # ... check the access ...
    if not access:
        raise PermissionDenied

serve_file_request.connect(access_callback)
```


If you manually save files for users, do this:
```
from django_tools.serve_media_app.models import generate_media_path

file_path = generate_media_path(user, filename='foobar.txt')
with open(file_path, 'wb') as f:
    f.write(...something...)
```



