#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="refparse",  # Replace with your own username
    version="0.1.0",
    author="Peter Sun",
    author_email="peterhs73@outlook.com",
    description="Convert yaml file into KanBan work flow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pterhs73/xBan",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pyyaml>=5.0", "Click>=7.0", "PySide2==5.12.1"],
    entry_points={"console_scripts": ["xban=xban.xban:cli"]},
    python_requires=">=3.6",
)
