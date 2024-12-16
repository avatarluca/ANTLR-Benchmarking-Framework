# ANTLR Benchmarking Framework
A small benchmarking framework for meassuring ANTLR grammar performance

In order to evaluate the performance of the ANTLR-based parser implementation and potential optimisations of the grammar, the creation of a benchmarking framework is essential. This framework makes it possible to measure and compare the efficiency of the current and the optimised parser. The aim is to make quantitative statements about the parsing speed and to compare the optimisations. The resource load is neglected in the process. In addition, special care is taken to ensure that the correctness of the parsed results is not impaired.

## Features
1. parse time measurement of test cases/test functions
2. outlier detection and handling
3. create and compare snapshot
4. multi-benchmarking
5. ATN analysis
6. Parser rebuild
7. Diagnosis mode