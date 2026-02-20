from setuptools import setup, find_packages

setup(
    name="shared-middlewares",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "structlog>=21.1.0",
        "python-jose[cryptography]>=3.3.0",
        "pydantic>=2.0.0",
    ],
)
