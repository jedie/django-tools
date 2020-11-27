# Django-Tools - Serve User Media File

About ```django_tools.serve_media_app``` django app:

* Serve ```settings.MEDIA_ROOT``` only for allowed users
* Works currently for ```FileSystemStorage```

Files are stored in these file path:

```
/{settings.MEDIA_ROOT}/{random-user-token}/{random-file-token}/
```

Example:

```
/media/w7tytv3lyupc/fm4kf9hp0c_vfx3onskrffw1/filename.ext
```


Note: The files served by streaming HTTP response. But serve files from the application is slow.
It's faster to use ```sendfile``` from the web server.
This is on the TODO:

* Support ```sendfile``` via https://pypi.org/project/django-sendfile2/


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
from django_tools import serve_media_app

urlpatterns = [
    # ...
    path(settings.MEDIA_URL.lstrip('/'), include(serve_media_app.urls)),
    # ...
]
```


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



