# Change Log

## new version

* added ability to display statistics of individual blocking strategies in P-Sig. #62

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