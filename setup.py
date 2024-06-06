from distutils.core import setup
from setuptools import find_packages
import os

setup(
    name="ctfbot",
    packages=find_packages('.'), 
    version='1.0.0',
    license='MIT',
    description='discord bot for managing ctf',
    author='mirasio', 
    install_requires=[],
    classifiers=[],
    entry_points="libctf:main"
)