#!/usr/bin/env python3
"""
Setup script for DICOM Maker
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dicom-maker",
    version="0.1.0",
    author="Christopher Gentle",
    author_email="",
    description="A native Python CLI application for creating synthetic DICOM data and sending it to PACS systems",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/christophergentle/dicom-maker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "dicom-maker=dicom_maker.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
