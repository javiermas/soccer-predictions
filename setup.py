import io
import os
from setuptools import find_packages, setup

import soccerlearn

# Meta-data
NAME = 'soccerlearn'
DESCRIPTION = 'Repository for soccerlearn'
HERE = os.path.abspath(os.path.dirname(__file__))
REQUIRES_PYTHON = '>=3.8.0, <3.9.0'
try:
    with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
        LONG_DESCRIPTION = '\n' + f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

def list_requirements(fname='requirements.txt'):
    with open(fname) as fd:
        return fd.read().splitlines()

setup(
    name=NAME,
    version=soccerlearn.__version__,
    packages=[
        'soccerlearn'
    ],
    url='https://github.com/javiermas/soccer-predictions/',
    classifiers=(
        'Programming Language :: Python :: 3.6'
    ),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    install_requires=list_requirements(),
    requires_python=REQUIRES_PYTHON,
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
