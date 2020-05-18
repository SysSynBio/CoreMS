import os
import pathlib
import sys
from setuptools import setup, find_packages
# The directory containing this file

# The text of the README file
with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

# This call to setup() does all the work
setup(
    name="CoreMS",
    version="13.5.0.beta",
    description="Mass Spectrometry Framework for Small Molecules Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.pnnl.gov/mass-spectrometry/corems/",
    author="Corilo, Yuri",
    author_email="corilo@pnnl.gov",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 4 - Beta"
    ],

    package_data={'': ['disclaimer.txt'], '': ['lib/*']},
    packages=find_packages(),
    exclude_package_data={'.': ["tests", "*.win_only"]},
    include_package_data=True,
    install_requires=required,
    setup_requires=['pytest-runner', 'wheel'],
    test_suite='pytest',
    tests_require=['pytest'],
)
