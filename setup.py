import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="puzzles",
    version="0.0.1",
    author="Daniel Semler",
    author_email="47rooks@gmail.com",
    description="Word puzzles library routines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/47rooks/puzzles",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
