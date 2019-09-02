#!/usr/bin/env python3

from setuptools import setup
from sys import version_info

if version_info < (3, 5, 2):
    # 3.5.2 is when __aiter__ became a synchronous function
    raise SystemExit('Sorry! asks requires python 3.5.2 or later.')

setup(
    name='asks',
    description='asks - async http',
    long_description='asks is an async http lib for curio, trio and asyncio',
    license='MIT',
    version='2.3.5',
    author='Mark Jameson - aka theelous3',
    url='https://github.com/theelous3/asks',
    packages=['asks'],
    install_requires=['h11', 'async_generator', 'anyio'],
    tests_require=['pytest', 'curio', 'overly'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Trio',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
