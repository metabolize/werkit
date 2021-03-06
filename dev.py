#!/usr/bin/env python3

import os
import click
from executor import execute


def python_source_files():
    import glob

    return (
        glob.glob("*.py")
        + glob.glob("werkit/*.py")
        + glob.glob("werkit/**/*.py")
        + glob.glob("tests/**/*.py")
    )  # + ["doc/"]


@click.group()
def cli():
    pass


@cli.command()
def init():
    execute("pip3 install --upgrade -r requirements_dev.txt")


@cli.command()
@click.option("--slow/--not-slow", default=True)
def test(slow):
    args = ["python3", "-m", "pytest"]
    if not slow:
        args += ["-m", "not slow"]
    execute(*args)


@cli.command()
@click.option("--slow/--not-slow", default=True)
def coverage(slow):
    args = ["python3", "-m", "pytest", "--cov=werkit"]
    if not slow:
        args += ["-m", "not slow"]
    execute(*args)


@cli.command()
def coverage_report():
    execute("coverage html")
    execute("open htmlcov/index.html")


@cli.command()
def lint():
    execute("flake8", *python_source_files())


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
    execute("python3 setup.py sdist bdist_wheel")
    execute("twine upload dist/*")


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    cli()
