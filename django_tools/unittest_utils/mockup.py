# coding: utf-8

"""
    Mockups
    ~~~~~~~
"""

from __future__ import unicode_literals, print_function

import tempfile

from PIL import Image, ImageDraw

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File as DjangoFile

#==============================================================================
# TODO: Remove after django-filer v1.2.6 is released!
# Problem: AttributeError: 'Manager' object has no attribute '_inherited'
# with Django v1.10 and django-filer v1.2.5
# see also:
# https://github.com/divio/django-filer/issues/899

from pip._vendor.packaging.version import parse as _parse_version
from filer import __version__ as _filer_version
from django import __version__ as _django_version

_filer_version=_parse_version(_filer_version)
_django_version=_parse_version(_django_version)

if _django_version < _parse_version("1.10") or _filer_version >= _parse_version("1.2.6"):
    NOT_SUPPORTED = False
    from filer.models import Image as FilerImage
else:
    NOT_SUPPORTED = True

#==============================================================================



DUMMY_TEXT = """Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula
eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient
montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque
eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo,
fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut,
imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium.

Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate
eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac,
enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus
viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam
ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui.

Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper
libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel,
luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt
tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam
sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit
amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum
sodales, augue velit cursus nunc"""


def create_pil_image(width, height):
    img = Image.new('RGB', (width, height), 'black') # create a new black image
    pixels = img.load() # create the pixel map

    # Fill image
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[i,j] = (i, j, 1)

    return img


def create_info_image(width, height, text, fill='#ffffff', align='center'):
    im = create_pil_image(width, height)
    draw = ImageDraw.Draw(im)
    draw.multiline_text((10, 10), text, fill=fill, align=align)
    return im


def create_filer_image(pil_image, user):
    file_obj = DjangoFile(pil_image, name=pil_image.name)
    image = FilerImage.objects.create(
        owner=user,
        original_filename=pil_image.name,
        file=file_obj,
        folder=None
    )
    return image


def create_temp_filer_info_image(width, height, text, user):
    if NOT_SUPPORTED:
        raise RuntimeError("Combination Django v1.10 and django-filer v1.2.5 is not supported")

    f = tempfile.NamedTemporaryFile(prefix='dummy_', suffix='.png')
    im = create_info_image(width, height, text)
    im.save(f, format='png')
    filer_image = create_filer_image(f, user)
    return filer_image

