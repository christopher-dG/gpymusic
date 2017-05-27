from setuptools import setup, find_packages

setup(
    name='gpymusic',
    version='0.0.6',
    packages=find_packages(exclude=['bin']),
    scripts=[
        'bin/gpymusic',
        'bin/gpymusic-setup',
        'bin/gpymusic-download-all',
        'bin/gpymusic-get-dev-id',
        'bin/gpymusic-oauth-login'
    ],
    install_requires=['gmusicapi'],
    package_dir={'gpymusic': 'gpymusic'},
    package_data={
        'gpymusic': ['config/*']
    }
)
