#!/usr/bin/env -S poetry run python

import os
import click
from dotenv import load_dotenv
import sh

load_dotenv()


def python_source_files():
    import glob

    return (
        glob.glob("*.py")
        + glob.glob("werkit/*.py")
        + glob.glob("werkit/**/*.py")
        + glob.glob("werkit/**/**/*.py")
    )


@click.group()
def cli():
    pass


@cli.command()
def install():
    sh.poetry(
        "install",
        "--sync",
        "--extras",
        "aws_lambda_build",
        "--extras",
        "client",
        "--extras",
        "lambda_common",
        "--extras",
        "rds_graphile_worker",
        "--extras",
        "compute_graph",
        _fg=True,
    )


@cli.command()
@click.option("--slow/--not-slow", default=True)
def test(slow):
    args = ["-m", "pytest"]
    if not slow:
        args += ["-m", "not slow"]
    sh.python3(*args, _fg=True)


@cli.command()
@click.option("--slow/--not-slow", default=True)
def coverage(slow):
    args = ["-m", "pytest", "--cov=werkit"]
    if not slow:
        args += ["-m", "not slow"]
    sh.python3(*args, _fg=True)


@cli.command()
def coverage_report():
    sh.coverage("html", _fg=True)
    sh.open("htmlcov/index.html", _fg=True)


@cli.command()
def check_types():
    sh.mypy(
        "--package",
        "werkit",
        "--show-error-codes",
        "--enable-incomplete-feature=Unpack",
        _fg=True,
    )


@cli.command()
def lint():
    sh.flake8(*python_source_files(), _fg=True)


@cli.command()
def black():
    sh.black(*python_source_files(), _fg=True)


@cli.command()
def black_check():
    sh.black("--check", *python_source_files(), _fg=True)


@cli.command()
def publish():
    sh.rm("-rf", "dist/", _fg=True)
    sh.poetry("build", _fg=True)
    sh.twine("upload", "dist/*", _fg=True)


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    cli()
