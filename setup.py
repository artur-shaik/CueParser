from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='CueParser',
    version='1.1.2',

    description='Simple cue file parser.',
    long_description=long_description,

    url='https://github.com/artur-shaik/CueParser',

    author='Artur Shaik',
    author_email='ashaihullin@gmail.com',

    py_modules = ['cueparser', 'cuegen'],
    include_package_data = True,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages = find_packages(),
    keywords='cue parser cdtool audio generator',
    entry_points={
        'console_scripts': [
            'cueparser=cueparser:main',
            'cuegen=cuegen:main',
        ],
    },
)
