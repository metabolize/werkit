# werkit

[![version](https://img.shields.io/pypi/v/werkit?style=flat-square)][pypi]
[![python versions](https://img.shields.io/pypi/pyversions/werkit?style=flat-square)][pypi]
[![license](https://img.shields.io/pypi/l/werkit?style=flat-square)][pypi]
[![build](https://img.shields.io/circleci/project/github/metabolize/werkit/main?style=flat-square)][build]
[![code style](https://img.shields.io/badge/code%20style-black-black?style=flat-square)][black]

Toolkit for encapsulating Python-based computation into deployable and
distributable tasks.

Provides code that helps package things up:

- Serializing results
- Handling and serializing errors
- Deploying task workers using AWS Lambda

They're particularly useful for providing repsonse consistency across different
revisions of a service or different services.

[pypi]: https://pypi.org/project/werkit/
[build]: https://app.circleci.com/pipelines/github/metabolize/werkit?branch=main
[docs build]: https://werkit.readthedocs.io/en/latest/
[black]: https://black.readthedocs.io/en/stable/

## Installation

```sh
pip install werkit
```

## Usage

```py
from werkit.compute import Manager

# By convention, `schema.json` should define `Input`, `AnyInputMessage`,
# `Output`, and `AnyOutputMessage`.
schema = Schema.load_relative_to_file(__file__, ["path", "to", "schema.json"])

def work():
    result = perform_computation()
    # If needed, convert result to JSON-serializable objects.
    return transform(result)

def myfunc(params, verbose=False, handle_exceptions=True):
    return Manager(
        input_message=params,
        schema=schema,
        handle_exceptions=handle_exceptions,
        verbose=verbose,
    ).work(work, should_send=False, should_return=True)
```

### Parallel computation on AWS lambda

Werkit also implements a parallel map on AWS lambda.

Werkit comes with a default lambda handler, that accepts an event of the form `{"input":[a, b, ...],"extra_args":[c, d, ...]}`. Werkit invokes a lambda function in parallel for every item in `input`, with an event of the form `{"input": a, "extra_args":[c, d, ...]}`.

The werkit default handler is configurable via the following environmnent variables:

- `LAMBDA_WORKER_FUNCTION_NAME`: Name of the lambda worker function to invoke
- `LAMBDA_WORKER_TIMEOUT`: How long to wait in seconds for the lambda worker function to return before returning a TimeoutError

### Building and deploying functions to AWS Lambda

Werkit provides tools for programmatically building and deploying functions
to AWS Lambda. There are two distinct steps: build and deploy.

The build process can run natively using a virtualenv, or in Docker. When
either of the following cases apply, you can use the native virtualenv method:

- The function's dependencies are pure Python (no compiled extensions).
- You are building the function in Linux.

When building a function using compiled dependencies in OS X, the virtualenv
method will try to pack up the OS X dependencies which of course won't work
on Lambda. In that case you must use the Docker method.

#### Building a function natively using a virtualenv

```py
def build_natively(build_dir="build", target_dir="build"):
    import os
    import shutil
    from werkit.aws_lambda.build import (
        collect_zipfile_contents,
        create_venv_with_dependencies,
        create_zipfile_from_dir,
    )

    shutil.rmtree(build_dir, ignore_errors=True)

    venv_dir = os.path.join(build_dir, "venv")
    create_venv_with_dependencies(
        venv_dir=venv_dir,
        # These are the defaults, which you can override if necessary.
        upgrade_pip=True,
        install_wheel=True,
        install_requirements_from=["requirements.txt"],
        # You can pass credentials to `pip install`.
        environment={"DEPLOY_TOKEN": DEPLOY_TOKEN},
    )

    contents_dir = os.path.join(build_dir, "contents")
    collect_zipfile_contents(
        target_dir=contents_dir,
        venv_dir=venv_dir,
        src_dirs=["mypackage", "assets"],
        # Specify additional system files to copy to `lib/` inside the zipfile.
        lib_files=[...],
    )

    os.makedirs(target_dir, exist_ok=True)
    temp_path_to_zipfile = os.path.join(target_dir, "function.zip")
    create_zipfile_from_dir(
        dir_path=contents_dir,
        path_to_zipfile=temp_path_to_zipfile
    )
```

#### Building a function using Docker

Create a `collect_and_zip.py` script which will run in Docker, with `/target`
mounted to a folder on the host system.

```py
from werkit.aws_lambda.build import create_zipfile_from_dir

VERBOSE = False

collect_zipfile_contents(
    target_dir="/build/contents",
    venv_dir="/build/venv",
    src_dirs=["mypackage", "assets"],
    # Specify additional system files to copy to `lib/` inside the zipfile.
    lib_files=[...],
)

# To improve performance, zip into the container and copy to the host
# afterward.
create_zipfile_from_dir(
    dir_path="/build/contents",
    path_to_zipfile="/build/function.zip"
)
shutil.copyfile("/build/function.zip", "/target/function.zip")
```

Create a `Dockerfile`:

```Dockerfile
FROM python:3.7

WORKDIR /src

# Install any system dependencies you want to include in the zipfile.
RUN apt-get install -y --no-install-recommends ...
RUN rm -rf /var/lib/apt/lists/*

# Install werkit, along with any other dependencies needed for
# `collect_and_zip.py`.
RUN python3 -m pip install "werkit==0.10.0"

# Optionally receive credentials from the environment.
ARG DEPLOY_TOKEN

# Create the venv. As is necessary for some Docker base images, upgrade pip and
# install wheel.
RUN python3 -m venv /build/venv
RUN /build/venv/bin/pip install --upgrade pip wheel

# Install Python dependencies.
COPY requirements.txt /src/
RUN DEPLOY_TOKEN=${DEPLOY_TOKEN} /build/venv/bin/pip install -r requirements.txt

COPY mypackage/ /src/mypackage/
COPY assets/ /src/assets/
COPY collect_and_zip.py /src/

# Optionally set PYTHONPATH if `collect_and_zip.py` imports any internal source
# code.
ENV PYTHONPATH /src

CMD python3 collect_and_zip.py
```

Invoke the build:

```py
DEPLOY_TOKEN = "..."

def build_in_docker(build_dir="build", target_dir="build"):
    from executor import execute

    docker_tag = "mypackage-lambda-builder"

    execute(
        "docker",
        "build",
        "-t",
        docker_tag,
        "-f",
        "Dockerfile",
        # Optionally pass credentials for the Docker build process.
        "--build-arg",
        f"DEPLOY_TOKEN={DEPLOY_TOKEN}",
        ".",
    )
    print("Build image created")

    os.makedirs("build/", exist_ok=True)
    execute(
        "docker",
        "run",
        "--volume",
        f"{os.path.abspath("build/")}:/target:Z",
        "-t",
        docker_tag,
    )
    print("Build finished")
```

#### Deploying the function

```py
# A Lambda role is always required.
LAMBDA_ROLE = ...
# When the zipfile is larger than 50 MB, a temporary bucket is required.
S3_CODE_BUCKET = ...

def create():
    from werkit.aws_lambda.deploy import perform_create

    perform_create(
        # Region is required.
        aws_region="us-east-1",
        function_name="myfunction",
        local_path_to_zipfile="build/function.zip",
        # The importable name of your handler function, which should have the
        # signature `def handler(event, context):`.
        handler="mypackage.worker.handler",
        role=LAMBDA_ROLE,
        # Required when the zipfile is larger than 50 MB.
        s3_code_bucket=S3_CODE_BUCKET,
        # Optionally override.
        timeout=TIMEOUT,
        memory_size=WORKER_MEMORY_SIZE,
        runtime="python3.8",
        env_vars={},
    )
```

#### Updating the code for an existing function

```py
LAMBDA_ROLE = ...
S3_CODE_BUCKET = ...

def update_code():
    from werkit.aws_lambda.deploy import perform_update_code

    perform_update_code(
        aws_region="us-east-1",
        function_name="myfunction",
        local_path_to_zipfile="build/function.zip",
        # Required when the zipfile is larger than 50 MB.
        s3_code_bucket=S3_CODE_BUCKET,
    )
```

## Type definitions

[TypeScript types are available][types] for the Werkit job message format.

[![version](https://img.shields.io/npm/v/werkit?style=flat-square)][npm]

[types]: https://github.com/metabolize/werkit/tree/main/types
[npm]: https://www.npmjs.com/package/werkit

## Development

First, [install Poetry][].

After cloning the repo, run `./bootstrap.zsh` to initialize a virtual
environment with the project's dependencies.

Subsequently, run `./dev.py install` to update the dependencies.

[install poetry]: https://python-poetry.org/docs/#installation

## License

The project is licensed under the MIT License.
