from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="assistant_mes_droits",
    version="0.1.0",  # Update the version as needed
    packages=find_packages(exclude=["tests.*", "tests"]),
    author="Youness",
    author_email="X@eY.Z",
    description="assistant_mes_droits ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CVxTz/assistant_mes_droits",
    install_requires=open(
        "requirements.txt"
    ).readlines(),  # Reads dependencies from file
    extras_require={"dev": open("requirements-dev.txt").readlines()},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",  # Or your required Python version
    test_suite="tests",  # for running tests via 'python setup.py test'
)
