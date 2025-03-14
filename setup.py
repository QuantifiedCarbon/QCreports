"""Makes installable package."""

from setuptools import find_packages, setup
import pip

pip.main(["install"])  # call pip to install them

setup(
    name="QCreports",
    version="0.0",
    author="QuantifiedCarbon",
    description="Package for reporting results",
    url="https://github.com/QuantifiedCarbon/QCreports",
    packages=find_packages(),
    install_requires=["pandas"],
    include_package_data=True,  # This ensures that the files in MANIFEST.in are included
)
