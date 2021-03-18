.. blocklib documentation master file, created by
   sphinx-quickstart on Tue Feb 11 16:22:16 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Blocklib
====================================

`blocklib` is a python implementation of record linkage blocking techniques. Blocking is a technique that makes
record linkage scalable. It is achieved by partitioning datasets into groups, called blocks and only comparing
records in corresponding blocks. This can reduce the number of comparisons that need to be conducted to find which
pairs of records should be linked.

Note that it is part of the anonlink system which includes libraries for encoding, command line tools and Rest API:

* `clkhash <https://github.com/data61/clkhash>`_
* `anonlink-client <https://github.com/data61/anonlink-client>`_
* `anonlink <https://github.com/data61/anonlink>`_
* `anonlink-entity-service <https://github.com/data61/anonlink-entity-service>`_

Blocklib is Apache 2.0 licensed, supports Python version 3.6+ and run on Windows, OSX and Linux.

Install with pip::

    pip install blocklib


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   tutorial/index
   blocking-schema
   python-api
   development
   devops
   references

External Links
--------------

* `blocklib on Github <https://github.com/data61/blocklib/>`_
* `blocklib on Pypi <https://pypi.org/project/blocklib/>`_