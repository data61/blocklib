Development
===========

Testing
-------

Make sure you have all the required dependencies before running the tests::


    $ poetry install


Now run the unit tests and print out code coverage with `pytest`::

    $ poetry run pytest --cov=blocklib


Type Checking
-------------


``blocklib`` uses static typechecking with ``mypy``. To run the type checker as configured to run in the CI::

    $ poetry run mypy blocklib --ignore-missing-imports --strict-optional --no-implicit-optional --disallow-untyped-calls

