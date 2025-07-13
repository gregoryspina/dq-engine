# setup.py
from setuptools import setup, find_packages

setup(
    name="dq-engine",
    version="0.1.0",
    description="Portable Data Quality Engine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "duckdb>=0.9.2",
        "pandas>=2.1.4",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "jinja2>=3.1.2",
        "python-multipart>=0.0.6",
        "click>=8.1.7",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "dq-engine=dq_engine.main:cli",
        ],
    },
    python_requires=">=3.8",
)
