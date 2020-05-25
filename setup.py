from os import path
from setuptools import setup, find_packages
from io import open

here = path.abspath(path.dirname(__file__))

# Get long_description from README.md file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='SSH/SCP Remote Client',
    version='1.0.0',
    description='Script to handle tasks on a remote machine through SSH/SCP using Paramiko',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jaza-k/sshclient',
    author='Jaza K.',
    author_email='jaza-k@protonmail.com',
    keywords='Paramiko SCP SSH Remote Automation',
    packages=find_packages(),
    install_requires=['Paramiko', 'SCP', 'Loguru']
)