#!/usr/bin/env python

import os
import click
from executor import execute


def python_source_files():
    import glob

    return glob.glob("*.py") + glob.glob("werkit/**/*.py")  # + ["doc/"]


@click.group()
def cli():
    pass


@cli.command()
def init():
    execute("pip2 install --upgrade -r requirements_dev_py2.txt")
    execute("pip3 install --upgrade -r requirements_dev_py3.txt")


@cli.command()
def test():
    execute("pytest")


@cli.command()
def coverage():
    execute("pytest --cov=werkit")


@cli.command()
def coverage_report():
    execute("coverage html")
    execute("open htmlcov/index.html")


@cli.command()
def test_both():
    execute("python2 -m pytest")
    execute("python3 -m pytest")


@cli.command()
def lint():
    execute("pyflakes", *python_source_files())


@cli.command()
def black():
    execute("black", *python_source_files())


@cli.command()
def black_check():
    execute("black", "--check", *python_source_files())


@cli.command()
def doc():
    execute("rm -rf build/ doc/build/ doc/api/")
    execute("sphinx-build -b singlehtml doc doc/build")


@cli.command()
def doc_open():
    execute("open doc/build/index.html")


@cli.command()
def publish():
    execute("rm -rf dist/")
    execute("python setup.py sdist")
    execute("twine upload dist/*")


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    cli()
