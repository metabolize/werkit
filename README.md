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
- Deploying task workers using [Redis][], [RQ][] and the [Fargate CLI][]

[redis]: https://redis.io/
[rq]: https://python-rq.org/
[fargate cli]: https://somanymachines.com/fargate/

They're particularly useful for providing repsonse consistency across different
revisions of a service or different services.

[pypi]: https://pypi.org/project/werkit/
[coverage]: https://coveralls.io/github/metabolize/werkit
[build]: https://app.circleci.com/pipelines/github/metabolize/werkit?branch=main
[docs build]: https://werkit.readthedocs.io/en/latest/
[black]: https://black.readthedocs.io/en/stable/

## Installation

```sh
pip install werkit
```

## Usage

```py
from werkit import Manager

def myfunc(param, verbose=False, handle_exceptions=True):
    with Manager(handle_exceptions=handle_exceptions, verbose=verbose) as manager:
        manager.result = do_some_computation()
    return manager.serialized_result
```

## Parallel computation

Werkit supports parallel computation using Redis and RQ.

You must install the dependencies separately:

```sh
pip install redis rq
```

### Requesting work

```py
from mylib import myfunc
from werkit.parallel import invoke_for_each


items = {'a': ..., 'b': ...}
job_ids = invoke_for_each(myfunc, items, connection=Redis.from_url(...))
```

### Performing work

```sh
pip install redis rq
rq worker --burst werkit-default --url rediss://...
```

Note: `mylib.myfunc` must be importable.

### Using CloudManager

In place of the low-level API you can make your calls using CloudManager:

```py
#!/usr/bin/env python


import click
from werkit.parallel import Config, CloudManager, invoke_for_each

manager = CloudManager(
    config=Config(
        local_repository="my-project",
        ecr_repository="123456789012.dkr.ecr.us-east-1.amazonaws.com/my-project",
        ecs_task_name="my-project",
        task_args=[
            "--cpu",
            "1024",
            "--memory",
            "2048",
            "--task-role",
            "arn:aws:iam::123456789012:role/...",
            "--security-group-id",
            "sg-...",
            "--subnet-id",
            "subnet-...",
        ],
        default_task_count=5,
    )
)


@click.group()
def cli():
    pass


@cli.command()
def login():
    manager.login()


@cli.command()
@click.argument("tag")
def build_and_push(tag):
    manager.build_and_push()


@cli.command()
def enqueue():
    from myproject import myfunc

    items = {"key1": "value1", "key2": "value2"}

    invoke_for_each(
        measure_body,
        items,
        clean=True,
        connection=manager.redis_connection,
    )


@cli.command()
@click.option(
    "--count",
    default=manager.config.default_task_count,
    type=int,
    help="Number of tasks to run",
)
@click.argument("tag")
def run(count, tag):
    manager.run(tag=tag, count=count)


@cli.command()
def dashboard():
    manager.dashboard()


@cli.command()
def ps():
    manager.ps()


@cli.command()
def get_results():
    print(manager.get_results())


@cli.command()
def clean():
    manager.clean()


if __name__ == "__main__":
    cli()
```

### Getting results

```py
from redis import Redis
from werkit.parallel import get_results


get_results(wait_until_done=True, connection=Redis.from_url(...))
```

### Monitoring

You can monitor your queues using [RQ Dashboard][] or one of the
[other methods outlined here][monitoring].

[rq dashboard]: https://github.com/eoranged/rq-dashboard
[monitoring]: https://python-rq.org/docs/monitoring/


### Parallel computation on AWS lambda

Werkit also implements a parallel map on AWS lambda.

Werkit comes with a default lambda handler, that accepts an event of the form `{"input":[a, b, ...],"extra_args":[c, d, ...]}`. Werkit invokes a lambda function in parallel for every item in `input`, with an event of the form `{"input": a, "extra_args":[c, d, ...]}`.

The werkit default handler is configurable via the following environmnent variables:

* `LAMBDA_WORKER_FUNCTION_NAME`: Name of the lambda worker function to invoke 
* `LAMBDA_WORKER_TIMEOUT`: How long to wait in seconds for the lambda worker function to return before returning a TimeoutError


## Contribute

- Issue Tracker: https://github.com/metabolize/werkit/issues
- Source Code: https://github.com/metabolize/werkit

Pull requests welcome!


## Support

If you are having issues, please let us know.


## License

The project is licensed under the MIT License.
