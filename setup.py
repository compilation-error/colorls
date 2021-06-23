import os
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="colorls",
    version="0.1.1",
    author="Romeet Chhabra",
    author_email="romeetc@gmail.com",
    description="Pure Python implementation of subset of ls command with colors and icons",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/compilation-error/colorls",
    project_urls={
        "Bug Tracker": "https://gitlab.com/compilation-error/colorls/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "colorls=colorls.colorls",
        ],
    },
    data_files=[(os.path.expanduser('~/.colorls.ini'), ['config/colorls.ini']),
    ],
)