import os
from setuptools import find_packages, setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-kdv',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='django framwork for a bank of trust',
    long_description='README.md',
    url='https://github.com/Xiphoseer/django-kdv',
    author='Daniel Schweighöfer',
    author_email='dschweighoefer@d120.de',
    install_requires=[
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
