try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name="document-your-code",
    version="0.0.9",
    author="Mohammad Albakri",
    author_email="mohammad.albakri93@gmail.com",
    packages=find_packages(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zarad1993/dyc",
    install_requires=[
        "click==7.0",
        "pyyaml>=4.2b1",
        "gitpython==2.1.11"
        ],
    entry_points = {
        "console_scripts": ["dyc=dyc.dyc:main"],
    },
    package_data={
        '': ['*.yaml'],
    },
)