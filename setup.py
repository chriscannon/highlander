#!/usr/bin/env python
from setuptools import setup

__version__ = '0.1.1'

setup(
    name='highlander-one',
    version=__version__,
    author='Christopher T. Cannon',
    author_email='christophertcannon@gmail.com',
    description='A simple decorator to ensure that your '
                'program is only running once on a system.',
    url='https://github.com/chriscannon/highlander',
    install_requires=[
        'funcy>=1.4',
        'psutil>=2.2.1'
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    download_url='https://github.com/chriscannon/highlander/tarball/{0}'.format(__version__),
    packages=['highlander'],
    test_suite='tests.highlander_tests.get_suite',
)
