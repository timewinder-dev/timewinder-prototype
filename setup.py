import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="telltale",
    version="0.1dev0",
    author="Barak Michener",
    author_email="me@barakmich.com",
    description="Temporal logic models for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barakmich/telltale",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[],
    python_requires=">=3.6",
)
