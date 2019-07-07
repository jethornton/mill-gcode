import os
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="Mill G code",
    version="0.1.2",
    author="John Thornton",
    author_email="<jt@gnipsel.com>",
    description="Mill G code Generator for LinuxCNC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jethornton/mill-gcode",
    download_url="https://github.com/jethornton/mill-gcode/archive/master.zip",
    python_requires='>=2',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'gui_scripts': ['mgcode=mgcode.py:main',],
    },
)

