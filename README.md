# timewinder

[![license](https://img.shields.io/github/license/barakmich/timewinder)](https://github.com/barakmich/timewinder/blob/master/LICENSE)
[![tests](https://github.com/barakmich/timewinder/workflows/tests/badge.svg)](https://github.com/barakmich/timewinder/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/barakmich/timewinder)](https://codecov.io/gh/barakmich/timewinder)
[![docs](https://img.shields.io/readthedocs/timewinder)](https://timewinder.readthedocs.io)
[![version](https://img.shields.io/pypi/v/timewinder)](https://pypi.org/project/timewinder/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/timewinder)](https://pypi.org/project/timewinder/)

Temporal logic models for Python

## Installation

You can simply `pip install timewinder`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/barakmich/timewinder
```

### Running the test suite

You can run the full test suite with:

```
tox
```

### Building the documentation

You can build the HTML documentation with:

```
tox -e docs
```

The built documentation is available at `docs/_build/index.html.
