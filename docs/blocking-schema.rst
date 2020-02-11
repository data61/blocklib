.. _blocking-schema:

Blocking Schema
===============
Each blocking method has its own configuration and parameters to tune with. To make our API as generic
as possible, we designed the blocking schema to specify the configuration of the blocking method including
features to use in generating blocks and hyperparameters etc.

Currently we support two blocking methods:

* "`p-sig`": Probability signature

* "`lambda-fold`": LSH based :math:`\lambda`-fold

which are proposed by the following publications:

* `Scalable Entity Resolution Using Probabilistic Signatures on Parallel Databases <https://arxiv.org/abs/1712.09691>`_
* `An LSH-Based Blocking Approach with a Homomorphic Matching Technique for Privacy-Preserving Record Linkage <https://www.computer.org/csdl/journal/tk/2015/04/06880802/13rRUxASubY>`_

The format of the blocking schema is defined in a separate
`JSON Schema <https://json-schema.org/specification.html>`_ specification document -
`blocking-schema.json <https://github.com/data61/anonlink-client/blob/master/docs/schemas/blocking-schema.json>`_.

Basic Structure
---------------

A blocking schema consists of three parts:

* :ref:`type <blocking-schema/type>`, the blocking method to be used
* :ref:`version <blocking-schema/version>`, the version number of the hashing schema.
* :ref:`config <blocking-schema/config>`, an json configuration of that blocking method that varies with different blocking methods


Example Schema
--------------

::

    {
      "type": "lambda-fold",
      "version": 1,
      "config": {
        "blocking-features": [1, 2],
        "Lambda": 30,
        "bf-len": 2048,
        "num-hash-funcs": 5,
        "K": 20,
        "input-clks": true,
        "random_state": 0
      }
    }

Schema Components
-----------------
.. _blocking-schema/type:

type
~~~~
String value which describes the blocking method.

================= ================================
name              detailed description
================= ================================
"`p-sig`"             Probability Signature blocking method from `Scalable Entity Resolution Using Probabilistic Signatures on Parallel Databases <https://arxiv.org/abs/1712.09691>`_
"`lambda-fold`"       LSH based Lambda Fold Redundant blocking method from `Scalable Entity Resolution Using Probabilistic Signatures on Parallel Databases <https://arxiv.org/abs/1712.09691>`_
================= ================================

.. _blocking-schema/version:

version
~~~~~~~

Integer value that indicates the version of blocking schema. Currently the only supported version is `1`.

.. _blocking-schema/config:

config
~~~~~~

Configuration specific to each blocking method.
Next we will detail the specific configuration for supported blocking methods.

Specific configuration of supported blocking methods can be found here:

- `config of p-sig <blocking-schema/p-sig>`
- `config of lambda-fold <blocking-schema/lambda-fold>`

.. _blocking-schema/p-sig:

Probabilistic Signature Configuration
~~~~~~~~~~~~~~~
===================== ============= ==========================
attribute             type          description
===================== ============= ==========================
blocking-features     list[integer] specify which features u
filter                dictionary    filtering threshold
blocking-filter       dictionary    type of filter to generate blocks
signatureSpecs        list of lists signature strategies where each list is a combination of signature strategies
===================== ============= ==========================

Filter Configuration
''''''''''''''''''''

============= ============ ==================
attribute     type         description
============= ============ ==================
type          string       either "ratio" or "count" that represents proportional or absolute filtering
max           numeric      for ratio, it should be within 0 and 1; for count, it should not exceed the number of records
============= ============ ==================


Blocking-filter Configuration
'''''''''''''''''''''''''''''

===================== ============ ==================
attribute             type         description
===================== ============ ==================
type                  string       currently we only support "bloom filter"
number-hash-functions integer      this specifies how many bits will be flipped for each signature
bf-len                integer      defines the length of blocking filter, for bloom filter usually this is 1024 or 2048
===================== ============ ==================

SignatureSpecs Configurations
'''''''''''''''''''''''''''''


It is better to illustrate this one with an example:

::

    {
      "signatureSpecs": [
        [
         {"type": "characters-at", "config": {"pos": [0]}, "feature-idx": 1},
         {"type": "characters-at", "config": {"pos": [0]}, "feature-idx": 2},
        ],
        [
         {"type": "metaphone", "feature-idx": 1},
         {"type": "metaphone", "feature-idx": 2},
        ]
      ]
    }

here we generate two signatures for each record where each signature is a combination of signatures:
- first signature is the first character of feature at index 1, concatenating with first character of feature at index 2
- second signature is the metaphone transformation of feature at index 1, concatenating with metaphone transformation of feature at index 2

The following specifies the current supported signature strategies:

=============== ===============
strategies      description
=============== ===============
feature-value   exact feature at specified index
characters-at   substring of feature
metaphone       phonetic encoding of feature
=============== ===============

Finally a full example of p-sig blocking schema:

::

   {
    "type": "p-sig",
    "version": 1,
    "config": {
        "blocking_features": [1],
        "filter": {
            "type": "ratio",
            "max": 0.02,
            "min": 0.00,
        },
        "blocking-filter": {
            "type": "bloom filter",
            "number-hash-functions": 4,
            "bf-len": 2048,
        },
        "signatureSpecs": [
            [
                 {"type": "characters-at", "config": {"pos": [0]}, "feature-idx": 1},
                 {"type": "characters-at", "config": {"pos": [0]}, "feature-idx": 2},
            ],
            [
                {"type": "metaphone", "feature-idx": 1},
                {"type": "metaphone", "feature-idx": 2},
            ]
        ]
      }
    }

.. _blocking-schema/lambda-fold:

LSH based :math:`\lambda`-fold Configuration
~~~~~~~~~~~~~~~~~~~~~
===================== ============= ==========================
attribute             type          description
===================== ============= ==========================
blocking-features     list[integer] specify which features to used in blocks generation
Lambda                integer       denotes the degree of redundancy - :math:`H^i`, :math:`i=1,2,...`, :math:`\Lambda` where each :math:`H^i` represents one independent blocking group
bf-len                integer       length of bloom filter
num-hash-funcs        integer       number of hash functions used to map record to Bloom filter
K                     integer       number of bits we will select from Bloom filter for each reocrd
random_state          integer       control random seed
input-clks            boolean       input data is CLKS if true else input data is not CLKS
===================== ============= ==========================


Here is a full example of lambda-fold blocking schema:

::

   {
     "type": "lambda-fold",
     "version": 1,
     "config": {
        "blocking-features": [1, 2],
        "Lambda": 5,
        "bf-len": 2048,
        "num-hash-funcs": 10,
        "K": 40,
        "random_state": 0,
        "input-clks": False
     }
   }