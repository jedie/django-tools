# coding: utf-8

import os
import warnings
import subprocess


__version__ = (0, 10, 0)


VERSION_STRING = '.'.join(str(part) for part in __version__)

#VERBOSE = True
VERBOSE = False

def get_git_hash(path=None):
    if path is None:
        path = os.path.abspath(os.path.dirname(__file__))

    try:
        process = subprocess.Popen(
           ["/usr/bin/git", "log", "--format=%h", "-1", "HEAD"],
           shell=False, cwd=path,
           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except Exception, err:
        if VERBOSE:
            warnings.warn("Can't get git hash: %s" % err)
    else:
        process.wait()
        returncode = process.returncode
        if returncode == 0:
            output = process.stdout.readline().strip()
            if len(output) == 7:
                return ".git-%s" % output
            elif VERBOSE:
                warnings.warn("Can't get git hash, output was: %r" % output)
        elif VERBOSE:
            warnings.warn(
                "Can't get git hash, returncode was: %r"
                " - git stdout: %r"
                " - git stderr: %r"
                % (returncode, process.stdout.readline(), process.stderr.readline())
            )
    return ""

VERSION_STRING += get_git_hash()

if __name__ == "__main__":
    print VERSION_STRING
