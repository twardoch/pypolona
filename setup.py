#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import re

readme_file = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'README.md')
with open(readme_file) as f:
    readme = f.read()


def get_version(*args):
    ver = "undefined"
    import pypolona.__init__
    try:
        ver = pypolona.__init__.__version__
    except AttributeError:
        verstrline = open("pypolona/__init__.py", "rt").read()
        VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
        mo = re.search(VSRE, verstrline, re.M)
        if mo:
            ver = mo.group(1)
    return ver

def get_requirements(*args):
    """Get requirements from pip requirement files."""
    requirements = set()
    with open(get_absolute_path(*args)) as handle:
        for line in handle:
            # Strip comments.
            line = re.sub(r'^#.*|\s#.*', '', line)
            # Add git handles
            line = re.sub(r'git\+(.*?)@(.*?)#egg=([^\-]+)($|([\-]?.*))', r'\3 @ git+\1@\2#egg=\3\4', line)
            # Ignore empty lines
            if line and not line.isspace():
                requirements.add(re.sub(r'\s+', '', line))
    print(requirements)
    return sorted(requirements)


def get_absolute_path(*args):
    """Transform relative pathnames into absolute pathnames."""
    directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory, *args)


setup(
    name='pypolona',
    author='Adam Twardoch',
    author_email='adam+github@twardoch.com',
    url='https://twardoch.github.io/pypolona/',
    project_urls={
        'Source': "https://github.com/twardoch/pypolona"
    },
    version=get_version(),
    license="MIT",
    description="Image downloader for the polona.pl website of the Polish National Library",
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
    install_requires=get_requirements('requirements.txt'),
    extras_require={
        'dev': [
            'twine>=3.2.0',
            'pyinstaller>=4.0',
            'dmgbuild>=1.3.3; sys_platform == "darwin"'
        ]
    },
    packages=find_packages(),
    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='polona jpeg downloader cli',
    entry_points='''
        [console_scripts]
        ppolona=pypolona.__main__:main
    '''
)
