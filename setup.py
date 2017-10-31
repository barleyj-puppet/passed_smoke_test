#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click==6.7',
    'GitPython==2.1.5',
    'python-jenkins==0.4.15',
    'Logbook==1.1.0',
    'jira==1.0.10',
    'PyGithub==1.35',

]

setup_requirements = [
    'pytest-runner',
    # TODO(barleyj-puppet): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='passed_smoke_test',
    version='0.1.0',
    description="Python utility that checks to see if a commit has made it through smoke testing.",
    long_description=readme + '\n\n' + history,
    author="Jayson Barley",
    author_email='jayson.barley@puppet.com',
    url='https://github.com/barleyj-puppet/passed_smoke_test',
    py_modules=['passed_smoke_test'],
    packages=find_packages(include=['passed_smoke_test', 'passed_smoke_test.*']),
    entry_points={
        'console_scripts': [
            'passed_smoke_test=passed_smoke_test.passed_smoke_test:cli'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='passed_smoke_test',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
