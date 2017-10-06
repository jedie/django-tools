# coding: utf-8

"""
    Mockups
    ~~~~~~~
"""

from __future__ import print_function, unicode_literals

import tempfile
import warnings

from django.core.files import File as DjangoFile

from filer.models import Image as FilerImage
from PIL import Image, ImageDraw, ImageFont

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


def create_filer_image(pil_image, user):
    """
    Create from a PIL image a filer.models.Image() instance
    """
    file_obj = DjangoFile(pil_image, name=pil_image.name)
    image = FilerImage.objects.create(
        owner=user,
        original_filename=pil_image.name,
        file=file_obj,
        folder=None
    )
    return image


class ImageDummy:
    new_image_color="black"
    text_color="#ffffff"
    text_align="center"
    temp_prefix="dummy_"
    format="png"

    def __init__(self, width, height):
        self.width=width
        self.height=height

    def fill_image(self, image):
        """
        Fill a PIL image with a colorful gradient.

        Overwrite with e.g.:
            self.draw_centered_text(
                image,
                text="(dummy picture)",
                font_size_factor=16,
                truetype_font="DejaVuSansMono.ttf"
            )
        """
        pixel_map = image.load()
        for i in range(self.width):
            for j in range(self.height):
                pixel_map[i,j] = (i, j, 1)

    def draw_centered_text(self, image, text, color="#000000", size_factor=16, truetype=None):
        """
        Draw the given >text< centered on the given >image<
        Maybe useful for self.fill_image()

        FIXME: Why in hell is it so complicated to draw a centered text with pillow?!?

        :param image: PIL instance, e.g.: Image.new()
        :param text: The text to draw
        :param color: Text color (font fill color)
        :param size_factor: used to calc the font size by image size
        :param truetype: for ImageFont.truetype.font, e.g.: "DejaVuSansMono.ttf"
        :return: None
        """
        draw = ImageDraw.Draw(image)

        font_size=min([self.width, self.height])
        font_size=int(font_size / size_factor)

        if truetype is not None:
            font = ImageFont.truetype(
                font=truetype,
                size=font_size
            )
            split_character = "\n" if isinstance(text, str) else b"\n"
            lines = text.split(split_character)
            max_width=0
            widths=[]
            for line in lines:
                line_width, line_height = font.getsize(line)
                widths.append(line_width)
                max_width = max(max_width, line_width)

            line_width, line_height = font.getsize(text)
            left=int((self.width-max_width)/2)
            top=int((self.height-line_height)/2)
        else:
            font = None
            left=int((self.width)/2)
            top=int((self.height)/2)

        draw.multiline_text(
            xy=(left, top),
            text=text,
            fill=color,
            font=font,
            align="center"
        )

    def create_pil_image(self):
        """
        return a 'filled' PIL image
        """
        image = Image.new('RGB', (self.width, self.height), self.new_image_color)
        self.fill_image(image)
        return image

    def create_info_image(self, text):
        """
        return a 'filled' PIL image with >text<
        """
        image = self.create_pil_image()
        draw = ImageDraw.Draw(image)
        draw.multiline_text((10, 10), text, fill=self.text_color, align=self.text_align)
        return image

    def create_temp_filer_info_image(self, text, user):
        """
        Fill a PIL image with a colorful gradient,
        draw the given >text< on it
        and return a filer.models.Image() instance.
        """
        f = tempfile.NamedTemporaryFile(prefix=self.temp_prefix, suffix=".%s" % self.format)
        image = self.create_info_image(text)
        image.save(f, format=self.format)
        filer_image = create_filer_image(f, user)
        return filer_image


def create_pil_image(width, height):
    warnings.warn(
        "This is a old API, please use django_tools.unittest_utils.mockup.ImageDummy",
        category=DeprecationWarning
    )
    return ImageDummy(width, height).create_pil_image()


def create_info_image(width, height, text, fill='#ffffff', align='center'):
    warnings.warn(
        "This is a old API, please use django_tools.unittest_utils.mockup.ImageDummy",
        category=DeprecationWarning
    )
    image_dummy=ImageDummy(width, height)
    image_dummy.text_color=fill
    image_dummy.text_align=align
    return image_dummy.create_info_image(text)


def create_temp_filer_info_image(width, height, text, user):
    warnings.warn(
        "This is a old API, please use django_tools.unittest_utils.mockup.ImageDummy",
        category=DeprecationWarning
    )
    return ImageDummy(width, height).create_temp_filer_info_image(text, user)
