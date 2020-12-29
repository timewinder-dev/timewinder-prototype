# Release Instructions

This document guides a contributor through creating a release of telltale.

## Preflight checks

### Ensure all tests pass

Locally you can run `tox` to check that all tests pass, and check that tests
against all supported environments are passing also by checking qsim's
[GitHub actions](https://github.com/barakmich/telltale/actions?query=branch%3Amaster+workflow%3Atests).

#### Verify that `AUTHORS.md` is up-to-date

The following command shows the number of commits per author since the last
annotated tag:
```
t=$(git describe --abbrev=0); echo Commits since $t; git shortlog -s $t..
```

## Make the release

Run

```
git push --tags      # push tagged release to upstream
flit publish         # publish to PyPI
```

## Start work on the next release

???
