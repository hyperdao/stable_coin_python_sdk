from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
        name='hdao-python-sdk',
        version='1.0.1rc1',
        description='Python3 implemented SDK for HyperDao',
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='realm520',
        author_email='realm520@gmail.com',
        url='https://github.com/hyperdao/stable_coin_python_sdk',
        packages=find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
)