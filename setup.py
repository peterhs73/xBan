#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xBan",
    version="0.3.0",
    author="Peter Sun",
    author_email="peterhs73@outlook.com",
    description="Offline personal kanban work-flow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pterhs73/xBan",
    packages=["xban"],
    license="BSD",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pyyaml>=5.0", "Click", "PySide6"],
    entry_points="""
        [console_scripts]
        xban=xban.xban:cli
    """,
    python_requires=">=3.6",
    include_package_data=True,
)
