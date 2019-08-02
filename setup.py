try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import soccerlearn

SHORT = 'soccerlearn'

setup(
    name='soccerlearn',
    version=soccerlearn.__version__,
    packages=[
        'soccerlearn'
    ],
    url='https://github.com/javiermas/soccer-predictions/',
    classifiers=(
        'Programming Language :: Python :: 3.6'
    ),
    description=SHORT,
    long_description=SHORT,
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)
