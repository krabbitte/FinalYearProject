from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='xentinuator',
    version='0.0.1',
    description='Music Generation System',
    long_description=readme,
    author='krabbitte',
    author_email='email@email.com',
    url='https://github.com/krabbitte/xentinuator',
    packages=find_packages(exclude='tests')
)