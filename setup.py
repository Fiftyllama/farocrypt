#!/usr/bin/env python3
"""
Setup script for Faro Cipher package

License: WTFPL v2 - Do whatever you want with this code.
SPDX-License-Identifier: WTFPL
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="faro-cipher",
    version="1.0.0",
    author="Faro Cipher Project",
    author_email="",
    description="High-performance file encryption system based on Faro shuffles",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/faro-cipher",
    license="WTFPL",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "performance": [
            "numba>=0.56.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "faro-cipher=faro_cipher.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "faro_cipher": ["*.md"],
    },
    keywords="encryption, cipher, faro, shuffle, cryptography, file-encryption",
    project_urls={
        "Bug Reports": "https://github.com/your-username/faro-cipher/issues",
        "Source": "https://github.com/your-username/faro-cipher",
        "Documentation": "https://github.com/your-username/faro-cipher/blob/main/README.md",
    },
) 