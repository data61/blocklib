Devops
===========

Azure Pipeline
--------------

``blocklib`` is automatically built and tested using Azure Pipeline
as part of the `Anonlink <https://dev.azure.com/data61/anonlink>`_ project.

The continuous integration pipeline is `here <https://dev.azure.com/data61/Anonlink/_build?definitionId=5>`_,
and the release pipeline is `here <https://dev.azure.com/data61/Anonlink/_release?_a=releases&definitionId=7>`_

Build Pipeline
~~~~~~~~~~~~~~

The build pipeline is defined in the script ``azure-pipelines.yml``.

There are three top level stages in the build pipeline:

- *Static Checks* - run typechecking with mypy.
- *Test and build* - tests the library using ``pytest`` with different versions of ``Python``.
- *Build Wheel Packages* - packages blocklib into wheels and saves the build artifacts.

The *Test and build* job does:

  - install the requirements,
  - run tests on Ubuntu 18.04 OS, for ``Python 3.5``, ``Python 3.6``, ``Python 3.7`` and ``Python 3.8``
  - publish the test results,
  - publish the code coverage (on Azure only),
  - package and publish the artifacts.

Release Pipeline
~~~~~~~~~~~~~~~~

The release pipeline publishes the built wheels and source code to `PyPi <https://pypi.org/project/blocklib/>`_
as ``blocklib``.

.. Note::

   The release pipeline requires manual intervention by a Data61 team member.

