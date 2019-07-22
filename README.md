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

They're particularly useful for providing repsonse consistency 

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


## Contribute

- Issue Tracker: https://github.com/metabolize/werkit/issues
- Source Code: https://github.com/metabolize/werkit

Pull requests welcome!


## Support

If you are having issues, please let us know.


## License

The project is licensed under the MIT License.
