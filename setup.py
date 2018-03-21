#!/usr/bin/env python
# -*- coding: latin-1 -*-
"""
Setup file for the delaware 2018 lasershoot thing

@author: Jens Timmerman (Ghent University)
"""
from setuptools import setup
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '%s'))
sys.path.insert(0, 'test')


def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('test', pattern='*')
    return test_suite

setup(
    name='lasershoot',
    version="0.1",
    install_requires=[
        'guizero',
        'mysqlclient',
        'flask',
        'RPi.GPIO',
    ],
    tests_require=[
        'prospector',
    ],
    test_suite='setup.my_test_suite'
)

