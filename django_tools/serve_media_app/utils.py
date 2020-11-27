import secrets
from pathlib import Path

from django.utils.text import slugify


def get_random_string(length, only_lower=True):
    """
    >>> x = get_random_string(length=10)
    >>> len(x)
    10
    """
    # Note: nbytes is not the length of the final String!
    random_string = secrets.token_urlsafe(nbytes=length + 10)
    random_string = random_string[:length]
    if only_lower:
        random_string = random_string.lower()
    return random_string


def clean_filename(filename):
    """
    Convert filename to ASCII only via slugify, e.g.:

    >>> clean_filename('bar.py')
    'bar.py'
    >>> clean_filename('No-Extension!')
    'no_extension'
    >>> clean_filename('testäöüß!.exe')
    'testaou.exe'
    >>> clean_filename('nameäöü.extäöü')
    'nameaou.extaou'
    """
    def convert(txt):
        txt = slugify(txt, allow_unicode=False)
        return txt.replace('-', '_')

    suffix = Path(filename).suffix
    if suffix:
        filename = filename[:-len(suffix)]
        suffix = f'.{convert(suffix)}'
    filename = convert(filename)
    return f'{filename}{suffix}'
