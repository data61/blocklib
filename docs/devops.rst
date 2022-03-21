Devops
===========

GitHub Actions
--------------

``blocklib`` is automatically built and tested using `GitHub actions <https://github.com/data61/blocklib/actions>`_.

There are currently three workflows:

Testing
~~~~~~~~~~~~~~

The testing workflow is defined in the script ``.github/workflows/python-test.yml``.

It consists of two jobs

- *Unit tests* - tests the library using ``pytest`` with different combinations of python versions and operating systems.
- *Notebook tests* - tests the tutorial notebooks using ``pytest``.

Type Checking
~~~~~~~~~~~~~~

The type checking workflow is defined in the script ``.github/workflows/typechecking.yml``.
It runs typechecking with mypy.

Build and Publish
~~~~~~~~~~~~~~~~~~

The build and publish workflow is defined in the script ``.github/workflows/build_publish.yml``.

It consists of two jobs:

- *Build distribution Packages* - packages blocklib into wheels and saves the build artifacts.
- *Publish to PyPI* - uploads the built artifacts to PyPI.

.. Note::
   The *Publish to PyPI* job is only triggered on a GitHub release.

