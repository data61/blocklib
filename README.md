
[![codecov](https://codecov.io/gh/data61/blocklib/branch/master/graph/badge.svg)](https://codecov.io/gh/data61/blocklib)
[![Documentation Status](https://readthedocs.org/projects/blocklib/badge/?version=latest)](http://blocklib.readthedocs.io/en/latest/?badge=latest)
[![Typechecking](https://github.com/data61/blocklib/actions/workflows/typechecking.yml/badge.svg)](https://github.com/data61/blocklib/actions/workflows/typechecking.yml)
[![Testing](https://github.com/data61/blocklib/actions/workflows/python-test.yml/badge.svg)](https://github.com/data61/blocklib/actions/workflows/python-test.yml)
[![Downloads](https://pepy.tech/badge/blocklib)](https://pepy.tech/project/blocklib)


# Blocklib


Python implementations of record linkage blocking techniques. Blocking is a technique that makes
record linkage scalable. It is achieved by partitioning datasets into groups, called blocks and only
comparing records in corresponding blocks. This can reduce the number of comparisons that need to be
conducted to find which pairs of records should be linked.

`blocklib` is part of the **Anonlink** project for privacy preserving record linkage.


### Installation

Install with pip:

    pip install blocklib

### Documents

You can find comprehensive documentation and tutorials in [readthedocs](http://blocklib.readthedocs.io/en/latest)

### Tests

Run unit tests with `pytest`::

    $ pytest


### Discussion

If you run into bugs, you can file them in our [issue tracker](https://github.com/data61/blocklib/issues)
on GitHub.

There is also an [anonlink mailing list](https://groups.google.com/forum/#!forum/anonlink)
for development discussion and release announcements.

Wherever we interact, we strive to follow the [Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/)


### License and Copyright

`blocklib` is copyright (c) Commonwealth Scientific and Industrial Research Organisation (CSIRO).

Licensed under the Apache License, Version 2.0 (the "License"). You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
