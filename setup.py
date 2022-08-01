import setuptools
from backup.__init__ import VERSION

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name="BackUp",
    version=VERSION,
    author="PaddeCraft",
    description="PaddeCraft's backup tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/paddecraft/BackUpUtility",
    install_requires=requirements,
    # project_urls={
    #     "Bug Tracker": "https://github.com/paddecraft/BackUpUtility/issues",
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=["backup"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "backup = backup.__main__:app",
        ],
    },
)
