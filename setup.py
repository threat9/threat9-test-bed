import codecs
from pathlib import Path

from setuptools import find_packages, setup

HERE = Path.cwd()


with codecs.open(str(HERE / "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='threat9-test-bed',
    use_scm_version=True,
    url='http://threat9.com',
    author='Mariusz Kupidura',
    author_email='f4wkes@gmail.com',
    description="Threat9 Test Bed",
    long_description=long_description,
    packages=find_packages(where=str(HERE)),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "test-bed = threat9_test_bed.cli:cli",
        ],
    },
    install_requires=[
        "click",
        "flask",
        "pyopenssl",
        "setuptools_scm",
    ],
    extras_require={},
    classifiers=[
        "Operating System :: POSIX",
        "Intended Audience :: Developers",

        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
    ],
)
