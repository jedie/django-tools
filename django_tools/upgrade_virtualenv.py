#!/usr/bin/env python
# coding: utf-8

"""
    upgrade packages in virtualenv
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    A simple commandline script for call "pip install ---upgrade XY" for every
    package thats installed in a virtualenv.
    
    Simply copy/symlink it into the root directory of your virtualenv and
    start it.
    
    You can select witch package type should be upgrade:
        * both: package + editables
        * only packages
        * only editables
        
    This will be obsolete, if pip has a own upgrade command, see: 
        https://github.com/pypa/pip/issues/59
    
    :copyleft: 2011 by the django-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys
import subprocess

import pkg_resources

from pip import locations
from pip.util import get_installed_distributions, get_terminal_size
import pip


class ColorOut(object):
    """
    Borrowed from Django:
    http://code.djangoproject.com/browser/django/trunk/django/utils/termcolors.py
    
    >>> c = ColorOut()
    >>> c.supports_colors()
    True
    >>> c.color_support = True
    >>> c.colorize('no color')
    'no color'
    >>> c.colorize('bold', opts=("bold",))
    '\\x1b[1mbold\\x1b[0m'
    >>> c.colorize("colors!", foreground="red", background="blue", opts=("bold", "blink"))
    '\\x1b[31;44;1;5mcolors!\\x1b[0m'
    """
    color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
    foreground_colors = dict([(color_names[x], '3%s' % x) for x in range(8)])
    background_colors = dict([(color_names[x], '4%s' % x) for x in range(8)])
    opt_dict = {'bold': '1', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}

    def __init__(self):
        self.color_support = self.supports_colors()

    def supports_colors(self):
        if sys.platform in ('win32', 'Pocket PC'):
            return False

        # isatty is not always implemented!
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            return True
        else:
            return False

    def colorize(self, text, foreground=None, background=None, opts=()):
        """
        Returns your text, enclosed in ANSI graphics codes.
        """
        if not self.color_support:
            return text

        code_list = []

        if foreground:
            code_list.append(self.foreground_colors[foreground])
        if background:
            code_list.append(self.background_colors[background])

        for option in opts:
            code_list.append(self.opt_dict[option])

        if not code_list:
            return text

        return "\x1b[%sm%s\x1b[0m" % (';'.join(code_list), text)
c = ColorOut()


def get_upgradeable():
    dependency_links = []
    for dist in pkg_resources.working_set:
        if dist.has_metadata('dependency_links.txt'):
            dependency_links.extend(dist.get_metadata_lines('dependency_links.txt'))

    print("dependency_links: %r" % dependency_links)

    packages = []
    editables = []
    for dist in get_installed_distributions(local_only=True):
        req = pip.FrozenRequirement.from_dist(dist, dependency_links=dependency_links)

        if not req.editable:
            packages.append(req.name)
        else:
            # FIXME: How can we get this needes information easier?
            raw_cmd = str(req)
            full_url = raw_cmd.split()[1]
            url, full_version = full_url.rsplit("@", 1)
            rev = full_version.rsplit("-", 1)[1]

            if rev != "dev":
                pip_url = "%s@%s#egg=%s" % (url, rev, req.name)
            else:
                pip_url = "%s#egg=%s" % (url, req.name)

            editables.append(pip_url)


    print(c.colorize("Found theses local packages:", foreground="yellow"))
    for package in packages:
        print("\t %s" % package)

    print(c.colorize("Found theses local editables:", foreground="yellow"))
    for editable in editables:
        print("\t %s" % editable)

    return packages, editables


def activate_virtualenv():
    if "VIRTUALENV_FILE" in os.environ:
        virtualenv_file = os.environ["VIRTUALENV_FILE"]
    else:
        virtualenv_file = "bin/activate_this.py"

    if not os.path.exists(virtualenv_file):
        print("")
        print(c.colorize(
            "Error: Can't find virtualenv activate file: %r" % virtualenv_file
        , foreground="red"))
        print("")
        print(
            "Put the absolute path to activate_this.py into environment"
            " variable VIRTUALENV_FILE"
        )
        print("")
        print("or")
        print("")
        print(
            "Copy this file into you virtualenv root directory"
            " and call it from there, e.g.:"
        )
        print("\t~/myvirtualenv$ ./upgrade_env.py")
        print("")
        sys.exit(-1)

    execfile(virtualenv_file, dict(__file__=virtualenv_file))


def check_activation():
    if not hasattr(sys, 'real_prefix'):
        print("")
        print(c.colorize("Error:", foreground="red"), "Seems that we are not running in a activated virtualenv!")
        print("")
        sys.exit(-1)
    print("")
    print("sys.real_prefix: %s" % c.colorize(sys.real_prefix, foreground="blue", opts=("bold",)))
    print("")


def call_pip(*args):
    pip_executeable = os.path.join(locations.bin_py, "pip")
    cmd = [pip_executeable, "install", "--upgrade"]
    cmd += args
    print("-"*get_terminal_size()[0])
    print("run '%s':" % c.colorize(" ".join(cmd), foreground="blue"))
    subprocess.call(cmd)


def main():
    activate_virtualenv()
    check_activation()
    packages, editables = get_upgradeable()

    print("")
    print("Witch local virtualenv packages would you like to upgrade?")
    print("")
    print("(1) both: package + editables")
    print("(2) only packages")
    print("(3) only editables")
    choice = raw_input("\nPlease select (1/2/3):")
    if choice not in ("1", "2", "3"):
        print(c.colorize("Abort, ok.", foreground="blue"))
        sys.exit()

    if choice in ("1", "2"):
        for package in packages:
            call_pip(package)

    if choice in ("1", "3"):
        for editable in editables:
            call_pip("--editable", editable)

    print("-"*get_terminal_size()[0])

    print("")
    if choice == "1":
        print(c.colorize("Done, all packages + editables are updated.", foreground="blue"))
    elif choice == "2":
        print(c.colorize("Done, Packages, but not the editables are updated.", foreground="blue"))
    elif choice == "3":
        print(c.colorize("Done, editables, but not normal packages are updated.", foreground="blue"))
    print("")


if __name__ == "__main__":
    main()


