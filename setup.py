#coding: utf-8

import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='aws-sa',  
    version='1.2.1',
    scripts=['aws-sa'] ,
    author="João Paulo de Melo",
    author_email="jpmdik@gmail.com",
    description="A aws script automation deploy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jpdik/aws-script-automation",
    packages=setuptools.find_packages(),
    install_requires=[
        'awscli',
        'ruamel.yaml'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )