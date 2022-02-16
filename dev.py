#!/usr/bin/env -S poetry run python

import os
import click
from dotenv import load_dotenv
from executor import execute

load_dotenv()


def python_source_files():
    import glob

    return (
        glob.glob("*.py") + glob.glob("werkit/*.py") + glob.glob("werkit/**/*.py")
    )  # + ["doc/"]


@click.group()
def cli():
    pass


@cli.command()
def install():
    execute(
        "poetry",
        "install",
        "--remove-untracked",
        "--extras",
        "aws_lambda_build",
        "--extras",
        "client",
        "--extras",
        "lambda_common",
        "--extras",
        "parallel",
        "--extras",
        "rds_graphile_worker",
        "--extras",
        "compute_graph",
    )


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
def publish():
    execute("rm -rf dist/")
    execute("poetry build")
    execute("twine upload dist/*")


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    cli()
