# werkit

[![version](https://img.shields.io/pypi/v/werkit.svg?style=flat-square)][pypi]
[![python versions](https://img.shields.io/pypi/pyversions/werkit.svg?style=flat-square)][pypi]
[![license](https://img.shields.io/pypi/l/werkit.svg?style=flat-square)][pypi]
[![build](https://img.shields.io/circleci/project/github/metabolize/werkit/master.svg?style=flat-square)][build]
[![code style](https://img.shields.io/badge/code%20style-black-black.svg?style=flat-square)][black]

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
[build]: https://circleci.com/gh/lace/werkit/tree/master
[docs build]: https://werkit.readthedocs.io/en/latest/
[black]: https://black.readthedocs.io/en/stable/

## Installation

```sh
pip install werkit
```

## Usage

```py
from werkit import ...
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
job_ids = invoke_for_each(myfunc, items, connection=Redis(url=...))
```

### Performing work

```sh
pip install redis rq
rq worker --burst werkit-default --url rediss://...
```

Note: `mylib.myfunc` must be importable.

### Getting results

```py
from redis import Redis
from werkit.parallel import get_results


get_results(wait_until_done=True, connection=Redis(url=...))
```

### Monitoring

You can monitor your queues using [RQ Dashboard][] or one of the
[other methods outlined here][monitoring].

[rq dashboard]: https://github.com/eoranged/rq-dashboard
[monitoring]: https://python-rq.org/docs/monitoring/


## Contribute

- Issue Tracker: https://github.com/metabolize/werkit/issues
- Source Code: https://github.com/metabolize/werkit

Pull requests welcome!


## Support

If you are having issues, please let us know.


## License

The project is licensed under the MIT License.
