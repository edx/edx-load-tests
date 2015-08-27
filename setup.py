"""
Setup script for the Open edX load test suite.
"""

from setuptools import setup, find_packages

setup(
    name="edx-load-tests",
    version="0.1",
    install_requires=["setuptools"],
    requires=[],
    packages=find_packages(),
)
