# Generated by Django 3.1.4 on 2020-12-06 08:23
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import django_tools.serve_media_app.models


def forward_code(apps, schema_editor):
    app_name, model_name = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_model(app_name, model_name)
    UserMediaTokenModel = apps.get_model('serve_media_app', 'UserMediaTokenModel')
    for user in User.objects.all():
        UserMediaTokenModel.objects.get_or_create(user_id=user.pk)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMediaTokenModel',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('token',
                 models.CharField(
                     default=django_tools.serve_media_app.models.generate_token,
                     max_length=12,
                     unique=True)),
                ('user',
                 models.ForeignKey(
                     editable=False,
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='token',
                     to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RunPython(
            forward_code,
            reverse_code=migrations.RunPython.noop),
    ]
