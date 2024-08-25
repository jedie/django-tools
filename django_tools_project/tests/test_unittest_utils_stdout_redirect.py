import sys

from django.test import SimpleTestCase

from django_tools.unittest_utils.stdout_redirect import DenyStdWrite, StdoutStderrBuffer


class StdoutRedirectTestCase(SimpleTestCase):
    def test_DenyStdWrite(self):
        with DenyStdWrite(name='foo'):
            pass

        with self.assertRaisesMessage(AssertionError, 'foo writes to stdout:\nbar'):
            with DenyStdWrite(name='foo'):
                print('bar')

        with self.assertRaisesMessage(AssertionError, 'bar writes to stderr:\nfoo'):
            with DenyStdWrite(name='bar'):
                print('foo', file=sys.stderr)

        # DenyStdWrite cleanup ok?

        with StdoutStderrBuffer() as buffer:
            sys.stdout.write('One')
            sys.stderr.write('Two')
        assert buffer.get_output() == 'OneTwo'
