from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(
    name='ckanext-dataset_comments',
    version=version,
    description="dataset comments",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='janosfarkas',
    author_email='farkas48@uniba.sk',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.dataset_comments'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        # Add plugins here, e.g.
        dataset_comments=ckanext.dataset_comments.plugin:DatasetCommentsPlugin
    ''',
)
