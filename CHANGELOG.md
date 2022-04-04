# Change Log

## new version

## 0.1.8

* use logging instead of the `print` function  #138
* use poetry for dependecy management  #139
* validate blocking schemas with pydantic #140
* move CI from Azure pipelines to GitHub actions #179
* rewrite of `asses_blocks_2party` for better scaling #189

## 0.1.7

* added Python 3.9 support to CI pipeline #116
* fixed division by zero bug in evaluation #107

## 0.1.6

* Improve column name support in blocking schema

## 0.1.5

* Support column names in blocking schema
* Fix inconsistent field names in blocking schema

## 0.1.4

* Convert block key of P-Sig to string type #75
* Make individual strategy statistics available for P-Sig blocking #62
* Add coverage ratio to P-Sig blocking statistics #59
* Remove collision blocks in P-Sig filtered reverse indices #57
* Added ability to display statistics of individual blocking strategies in P-Sig. #62

## 0.1.3

* Urgent bugfix: Setup now requires dependencies correctly. 
* Replace Fuzzy dependency with [Metaphone](https://pypi.org/project/Metaphone/).
* Replace bitarray with `bitarray-hardbyte`

## 0.1.2

Improvements to P-Sig blocking.

* Remove uncommon blocks due to collisions in bloom filter to reduce size of returned filtered reversed indices
* Add feedback on coverage information of P-Sig blocking method i.e. if final blocks cover 100% records or not

## 0.1.1

Correct markdown rendering in Pypi

## 0.1.0

Support two blocking methods that works for multiparty record linkage

* Probabilistic signature
* LSH based λ-fold