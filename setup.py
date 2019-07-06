import os
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

# list of (destination, source_file) tuples
DATA_FILES = [('~/.local/bin', ['m7i96/mesaflash64', 'm7i96/mesaflash32',])]
data_files = [(os.path.expanduser(dest), src_list) for dest, src_list in DATA_FILES]

setup(
    name="7i96",
    version="0.1.2",
    author="John Thornton",
    author_email="<jt@gnipsel.com>",
    description="Mill G code Generator for LinuxCNC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jethornton/mill-gcode",
    download_url="https://github.com/jethornton/mct7i96/tarball/master",
    python_requires='>=2',
    packages=find_packages(),
    data_files=data_files,
    include_package_data=True,
    entry_points={
        'gui_scripts': ['mill-gcode=mill-gcode.mgc:main',],
    },
)

