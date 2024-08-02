# my_heat_simulation/setup.py

from setuptools import setup, find_packages

setup(
    name='HexLatticePlot',
    version='1.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
    ],
    author='shenshuqiu',
    description='A package for Hex Lattice Ploting',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/shenshuqiu/HexLatticePlot',
    python_requires='>=3.10',
)
