
from django.conf import settings


TEMPLATE_INVALID_PREFIX='***invalid:'


class TemplateInvalidMixin(object):
    """
    https://docs.djangoproject.com/en/1.8/ref/templates/api/#invalid-template-variables
    """
    def setUp(self):
        super(TemplateInvalidMixin, self).setUp()

        settings.TEMPLATES[0]['OPTIONS']['string_if_invalid'] = '%s%%s***' % TEMPLATE_INVALID_PREFIX

    def tearDown(self):
        super(TemplateInvalidMixin, self).tearDown()

        settings.TEMPLATES[0]['OPTIONS']['string_if_invalid'] = ''
