from setuptools import setup, find_packages

setup(
    name='tilehuria',
    version='0.1.1',
    author='Ivan Gayton, Ramani Huria, HOT-OSM, and collaborators',
    author_email='ivangayton@gmail.com',
    packages=find_packages(),
    package_data={
    },
    url='http://pypi.python.org/pypi/tilehuria/',
    description='A Python package to create MBTiles from Slippy Map tileservers.',
    long_description=open('README.md', 'rt').read(),
    install_requires=[
        GDAL
        Pillow
    ],
    entry_points={
        'console_scripts': [
            'polygon2mbtiles=tilehuria.polygon2mbtiles:polygon2mbtiles',
        ],
    },
)
