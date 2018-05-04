"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.apps import apps
from django.db import models


class ModelTestGenerator:

    def _iter_model_label(self):
        app_configs = apps.get_app_configs()

        data = []
        for app_config in app_configs:
            models = app_config.get_models()
            for model in models:
                data.append((model._meta.label, model))

        yield from sorted(data)

    def get_model_by_label(self, model_label):
        for label, model in self._iter_model_label():
            if label == model_label:
                return model

    def get_models_startwith_label(self, prefix):
        models = []
        for label, model in self._iter_model_label():
            if label.startswith(prefix):
                models.append(model)

        return models

    def print_all_plugins(self):
        print("All models:")
        app_configs = apps.get_app_configs()
        for app_config in app_configs:
            models = app_config.get_models()
            for model in models:
                qs = model.objects.all()
                print("%6i instances: %r" % (qs.count(), model._meta.label))

    def test_code_for_instance(self, instance):
        prefix_lines = []
        lines = [
            "#", "# pk:{pk} from {label} {type}".format(
                pk=instance.pk,
                label=instance._meta.label,
                type=type(instance),
            ), "#", "{name} = {ClassName}.objects.create(".format(
                name=instance._meta.model_name,
                ClassName=instance._meta.object_name,
            )
        ]
        for field in instance._meta.fields:
            # field == django.db.models.fields.Field

            if field.hidden or field.auto_created:
                continue

            comment_post_line = False

            if not field.editable:
                comment_post_line = True

            internal_type = field.get_internal_type()

            value = getattr(instance, field.name)
            if isinstance(value, models.Model):
                prefix_lines += self.test_code_for_instance(instance=value)
                lines.append(
                    "    {name}={obj_name}.pk, # {internal_type} to {label}".format(
                        name=field.name,
                        obj_name=value._meta.model_name,
                        internal_type=internal_type,
                        label=value._meta.label
                    )
                )
                continue

            comment = field.description % {
                "max_length": field.max_length,
            }

            line = "{name}={value!r}, # {internal_type}, {comment}".format(
                name=field.name, value=value, internal_type=internal_type, comment=comment
            )
            if comment_post_line:
                line = "# %s" % line

            lines.append("    %s" % line)

        lines.append(")")
        lines.append("")

        if prefix_lines:
            lines = prefix_lines + lines

        return lines

    def from_queryset(self, queryset):
        lines = []
        for instance in queryset:
            lines += self.test_code_for_instance(instance)
            lines.append("#" * 79)

        content = "\n".join(lines)
        return content
