# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['werkit',
 'werkit.aws_lambda',
 'werkit.aws_lambda.test_worker',
 'werkit.common',
 'werkit.parallel',
 'werkit.scripts']

package_data = \
{'': ['*']}

extras_require = \
{'aws_lambda_build': ['executor>=21.0'],
 'cli': ['click==8.0.1'],
 'client': ['boto3==1.17.69'],
 'lambda_common': ['harrison>=2.0,<3.0'],
 'parallel': ['redis==3.5.3']}

setup_kwargs = {
    'name': 'werkit',
    'version': '0.19.0',
    'description': 'Toolkit for encapsulating Python-based computation into deployable and distributable tasks',
    'long_description': None,
    'author': 'Paul Melnikow',
    'author_email': 'github@paulmelnikow.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://werkit.readthedocs.io/en/stable/',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
