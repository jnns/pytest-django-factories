import codecs
import os.path

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            return line.split('"')[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="pytest-django-factories",
    license="MIT",
    version=get_version("django_factories.py"),
    description="Factories for your Django models that can be used as Pytest fixtures.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jannis Vajen",
    author_email="jvajen@gmail.com",
    url="http://github.com/jnns/pytest-django-factories",
    py_modules=["django_factories"],
    include_package_data=False,
    install_requires=["django"],
    tests_require=["pytest"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
)
