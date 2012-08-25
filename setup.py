# -*- coding: utf-8 -*-

import codecs

from setuptools import setup, find_packages

import dynamiq

long_description = codecs.open('README.rst', "r", "utf-8").read()

setup(
    name="dinamyq",
    version=dynamiq.__version__,
    author=dynamiq.__author__,
    author_email=dynamiq.__contact__,
    description=dynamiq.__doc__,
    keywords="django search form dynamic",
    url=dynamiq.__homepage__,
    download_url="https://github.com/liberation/django-dynamiq-search-form/downloads",
    packages=find_packages(),
    include_package_data=True,
    platforms=["any"],
    zip_safe=True,
    long_description=long_description,

    classifiers=[
        "Development Status :: 3 - Alpha",
        #"Environment :: Web Environment",
        "Intended Audience :: Developers",
        #"License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
    ],
)
