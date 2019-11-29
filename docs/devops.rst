Devops
===========

Azure Pipeline
--------------

``blocklib`` is automatically built and tested using Azure Pipeline
in the project `blocklib <https://dev.azure.com/data61/blocklib>`

The current pipeline is available:
  - `Build pipeline <https://dev.azure.com/data61/Anonlink/_build?definitionId=5>`,


Build Pipeline
~~~~~~~~~~~~~~

The build pipeline is described by the script `azurePipeline.yml`.

There is 1 top level stage in the build pipeline:

- *Unit tests and build* - tests the library using ``pytest`` with different versions of ``Python`` and package

The *Build & Test* job does:

  - install the requirements,
  - run tests on Ubuntu 18.04 OS, for ``Python 3.5``, ``Python 3.6``, ``Python 3.7`` and ``Python 3.8``
  - publish the test results,
  - publish the code coverage (on Azure only),
  - package and publish the artifacts.