# !/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='camundacmd',
    version='0.0.1',
    author='Felipe Rayel',
    description='A simple camunda framework.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/frayel/python-camunda',
    packages=setuptools.find_packages(),
    zip_safe=False,
    keywords='camunda',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=['requests>=2.0.0'],
)