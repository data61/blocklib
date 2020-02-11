Development
===========

Testing
-------

Make sure you have all the required modules before running the tests
(modules that are only needed for tests are not included during
installation)::


    $ pip install -r requirements.txt


Now run the unit tests and print out code coverage with `py.test`::

    $ python -m pytest --cov=blocklib


Type Checking
-------------


``anonlink-client`` uses static typechecking with ``mypy``. To run the type checker (in Python 3.5 or later)::

    $ pip install mypy
    $ mypy blocklib --ignore-missing-imports --strict-optional --no-implicit-optional --disallow-untyped-calls

