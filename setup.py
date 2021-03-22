import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="timewinder",
    version="0.1dev1",
    author="Barak Michener",
    author_email="me@barakmich.com",
    description="Temporal logic models for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barakmich/timewinder",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        "dataclasses",
        "msgpack",
        "varname",
    ],
    python_requires=">=3.8",
)
