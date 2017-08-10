from setuptools import setup, find_packages

import sys


if sys.version_info < (3, 4):
    print('gpymusic requires python>=3.4.')
    exit(1)

setup(
    name='gpymusic',
    version='1.1.0',
    description='A simple TUI client for Google Play Music',
    url='https://github.com/christopher-dG/gpymusic',
    author='Chris de Graaf',
    author_email='chrisadegraaf@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console :: Curses',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: Unix',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='terminal music streaming',
    packages=find_packages(exclude=['bin']),
    install_requires=['gmusicapi'],
    package_dir={'gpymusic': 'gpymusic'},
    package_data={'gpymusic': ['config/*']},
    scripts=[
        'bin/gpymusic',
        'bin/gpymusic-setup',
        'bin/gpymusic-download-all',
        'bin/gpymusic-get-dev-id',
        'bin/gpymusic-oauth-login'
    ],
)
