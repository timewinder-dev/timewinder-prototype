![Timewinder Logo](docs/assets/logo-1-textright.png)


![Status](https://img.shields.io/badge/status-alpha-blue)
[![license](https://img.shields.io/github/license/timewinder-dev/timewinder)](https://github.com/timewinder-dev/timewinder/blob/main/LICENSE)
[![tox-test](https://github.com/timewinder-dev/timewinder/actions/workflows/tox-test.yaml/badge.svg)](https://github.com/timewinder-dev/timewinder/actions/workflows/tox-test.yaml)
[![version](https://img.shields.io/pypi/v/timewinder)](https://pypi.org/project/timewinder/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/timewinder)](https://pypi.org/project/timewinder/)

Timewinder is a Python 3 library to build and run temporal logic models. 
The goal of the library is to bring formal methods, specifically Lamport's [Temporal Logic of Actions](https://www.microsoft.com/en-us/research/uploads/prod/1991/12/The-Temporal-Logic-of-Actions-Current.pdf), to a broader audience.
While very much inspired by [TLA+](https://github.com/tlaplus), Timewinder tries to be simpler, if more limited, and more industry-focused.

## Concepts

Timewinder starts with `@timewinder.object`s and `@timewinder.thread`


## Installation

You can simply `pip install timewinder`.

## Developing

### Pre-requisites

You only need `tox` for testing and documentation building:

```
python3 -m pip install tox
```

Or clone the repository:

```
git clone https://github.com/timewinder-dev/timewinder
```

### Running the test suite

You can run the full test suite with:

```
tox
```
