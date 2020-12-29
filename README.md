# telltale

[![license](https://img.shields.io/github/license/barakmich/telltale)](https://github.com/barakmich/telltale/blob/master/LICENSE)
[![tests](https://github.com/barakmich/telltale/workflows/tests/badge.svg)](https://github.com/barakmich/telltale/actions?query=workflow%3Atests)
[![codecov](https://img.shields.io/codecov/c/github/barakmich/telltale)](https://codecov.io/gh/barakmich/telltale)
[![docs](https://img.shields.io/readthedocs/telltale)](https://telltale.readthedocs.io)
[![version](https://img.shields.io/pypi/v/telltale)](https://pypi.org/project/telltale/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/telltale)](https://pypi.org/project/telltale/)

Temporal logic models for Python

## Installation

You can simply `pip install telltale`.

## Developing

### Pre-requesites

You will need to install `flit` (for building the package) and `tox` (for orchestrating testing and documentation building):

```
python3 -m pip install flit tox
```

Clone the repository:

```
git clone https://github.com/barakmich/telltale
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
