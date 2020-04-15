try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name="document-your-code",
    version="0.2.3",
    author="Mohammad Albakri",
    author_email="mohammad.albakri93@gmail.com",
    packages=find_packages(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zarad1993/dyc",
    install_requires=[
        "click==7.0",
        "pyyaml>=4.2b1",
        "gitpython>=2.1.11",
        "gitdb2;python_version>'3.4'",
        "watchdog==0.9.0",
        "pre-commit==1.18.1",
    ],
    entry_points={"console_scripts": ["dyc=dyc.dyc:main"]},
    package_data={'': ['*.yaml']},
)
