# Generated by Django 4.2 on 2023-04-11 18:55

import django.db.models.deletion
import parler.fields
import parler.models
from django.conf import settings
from django.db import migrations, models

import django_tools.file_storage.file_system_storage
import django_tools.limit_to_usergroups
import django_tools.model_version_protect.models
import django_tools.permissions
import django_tools.serve_media_app.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LimitToUsergroupsTestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'permit_edit',
                    django_tools.limit_to_usergroups.UsergroupsModelField(
                        choices=[(0, 'anonymous users'), (-3, 'normal users'), (-1, 'staff users'), (-2, 'superusers')]
                    ),
                ),
                (
                    'permit_view',
                    django_tools.limit_to_usergroups.UsergroupsModelField(
                        choices=[(0, 'anonymous users'), (-3, 'normal users'), (-1, 'staff users'), (-2, 'superusers')]
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='OverwriteFileSystemStorageModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'file',
                    models.FileField(
                        storage=django_tools.file_storage.file_system_storage.OverwriteFileSystemStorage(
                            create_backups=True, location='media/overwrite_file_storage'
                        ),
                        upload_to='',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='PermissionTestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foo', models.CharField(max_length=127)),
            ],
            options={
                'permissions': (('extra_permission', 'Extra permission'),),
            },
            bases=(django_tools.permissions.ModelPermissionMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SimpleParlerModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='VersioningTestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'version',
                    django_tools.model_version_protect.models.VersionModelField(
                        default=0,
                        help_text='Internal version number of this entry. Used to protect the overwriting of an older entry.',
                    ),
                ),
                ('name', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserMediaFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=django_tools.serve_media_app.models.user_directory_path)),
                ('image', models.ImageField(upload_to=django_tools.serve_media_app.models.user_directory_path)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='SimpleParlerModelTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('slug', models.SlugField()),
                (
                    'master',
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='translations',
                        to='django_tools_test_app.simpleparlermodel',
                    ),
                ),
            ],
            options={
                'verbose_name': 'simple parler model Translation',
                'db_table': 'django_tools_test_app_simpleparlermodel_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
