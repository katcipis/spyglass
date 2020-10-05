from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="spyglass",
    version="0.0.1",
    author="Tiago Cesar Katcipis",
    author_email="tiagokatcipis@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/katcipis/spyglass",
    packages=find_packages(),
    python_requires='>=3.8',
)
