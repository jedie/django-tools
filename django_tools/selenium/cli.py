"""
    To run this CLI, e.g.:

        .../django-tools$ poetry run django_tools_selenium
"""
import argparse
import logging
import sys

from django_tools.selenium.chromedriver import SeleniumChromiumTestCase
from django_tools.selenium.geckodriver import SeleniumFirefoxTestCase


ALL_TEST_CASE_CLASSES = (SeleniumFirefoxTestCase, SeleniumChromiumTestCase)


def setup_logging():
    logger = logging.getLogger('django_tools')
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s %(name)s:%(lineno)d] %(message)s')
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.setLevel(logging.DEBUG)


def info():
    for TestCaseClass in ALL_TEST_CASE_CLASSES:
        print('_' * 100, flush=True)
        print(f'Check if {TestCaseClass.verbose_browser_name!r} is available...')
        available = TestCaseClass.avaiable()
        print('-' * 100)
        print(
            f'\n *** {TestCaseClass.verbose_browser_name} is available: {available} *** \n',
            flush=True,
        )


def setup():
    for TestCaseClass in ALL_TEST_CASE_CLASSES:
        print('_' * 100, flush=True)
        print(f'Setup {TestCaseClass.verbose_browser_name!r} web driver manager...')
        TestCaseClass.get_webdriver()
        print('\n', flush=True)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title='actions', dest='action', description='valid subcommands', help='additional help'
    )
    subparsers.add_parser('info')
    subparsers.add_parser('setup')
    args = parser.parse_args()
    action = args.action

    setup_logging()

    if action == 'info':
        info()
    elif action == 'setup':
        setup()
    else:
        print('\n*** Argument missing! ***\n')
        parser.print_help()
        sys.exit(-1)
