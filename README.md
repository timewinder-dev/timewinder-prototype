![Timewinder Logo](docs/assets/logo-1-textright.png)


![Status](https://img.shields.io/badge/status-alpha-blue)
[![license](https://img.shields.io/github/license/timewinder-dev/timewinder)](https://github.com/timewinder-dev/timewinder/blob/main/LICENSE)
[![tox-test](https://github.com/timewinder-dev/timewinder/actions/workflows/tox-test.yaml/badge.svg)](https://github.com/timewinder-dev/timewinder/actions/workflows/tox-test.yaml)
[![version](https://img.shields.io/pypi/v/timewinder)](https://pypi.org/project/timewinder/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/timewinder)](https://pypi.org/project/timewinder/)

Timewinder is a Python 3 library to build and run temporal logic models. 
The goal of the library is to bring formal methods, specifically Lamport's [Temporal Logic of Actions](https://www.microsoft.com/en-us/research/uploads/prod/1991/12/The-Temporal-Logic-of-Actions-Current.pdf), to a broader audience.
While very much inspired by [TLA+](https://github.com/tlaplus), Timewinder tries to be simpler, more readable, and more industry-focused.
That said, TLA+ is an impressive tool and Timewinder is not trying to cover the full spectrum of what TLA+ can do.

The project intends to work toward the following goals:
* Introduce more developers into modeling and formal methods
* Increase the number of people working with temporal logic
* Improve design docs, with testable example models that non-experts can also read
* Make running models easy and automatable, [even from the command line](https://medium.com/software-safety/introduction-to-tla-model-checking-in-the-command-line-c6871700a6a2).

## Project Status

This project is still alpha, so the API may change. 
Please join in on the [Github Discussions](https://github.com/timewinder-dev/timewinder/discussions) to talk about models, examples, and direction.
Help is definitely wanted and appreciated!

## Examples

* [Account Transfers](examples/practical_tlaplus_chap1.py) from [Practical TLA+, Chapter 1](https://www.apress.com/gp/book/9781484238288)
* [Blocking Queue](examples/blocking_queue.py) from [Weeks of Debugging Can Save You Hours of TLA+](https://www.youtube.com/watch?v=wjsI0lTSjIo)

## High-level Usage

Timewinder starts with the `@timewinder.object` and `@timewinder.process` decorators.
`object` wraps classes and registers them as a Timewinder data structures.
`process` wraps functions that we intend to check. Inside `process` functions, Python's `yield` keyword represents an atomicity boundary -- that is, at every yield point, the evaluator saves the state and is free to run any other available process in any order. 
A function with no yield keyword always runs to completion in one step.

Finally, there are predicates, which are properties about the objects to be checked at every stage.

These are all combined in the `Evaluator`, where Timewinder will exhaustively generate (up to a limit number of steps) all the potential program states resulting from running the processes in any order.

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
