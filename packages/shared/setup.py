from setuptools import setup, find_packages

setup(
    name="truthnet-contracts",
    version="0.1.0",
    description="Shared agent contracts for TruthNet",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.5.0",
    ],
    python_requires=">=3.10",
)
