from setuptools import setup

version = "0.5.9"

setup(
    name="PyConfigure",
    version=version,
    description="configuration toolkit based on YAML",
    author="Andrey Popp",
    author_email="8mayday@gmail.com",
    url='https://github.com/alfred82santa/configure',
    py_modules=["configure"],
    test_suite="tests",
    install_requires=["pyyaml"],
    zip_safe=False)
