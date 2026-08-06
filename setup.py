from setuptools import setup, find_packages

setup(
    name="alteryx-metrics",
    version="1.0.0",
    description="Alteryx Metrics System - Query metrics from Snowflake",
    author="Alteryx Data Team",
    author_email="insights@alteryx.com",
    url="https://github.com/alteryx/metrics-system",
    packages=find_packages(),
    install_requires=[
        "snowflake-connector-python==3.9.1",
        "snowflake-sqlalchemy==1.6.1",
        "PyYAML==6.0.1",
        "pandas==2.2.0",
        "typer==0.9.0",
        "rich==13.7.0",
        "tabulate==0.9.0",
        "python-dotenv==1.0.0",
        "sqlalchemy==2.0.23",
        "requests==2.31.0",
        "Jinja2==3.1.2",
    ],
    entry_points={
        "console_scripts": [
            "metrics=cli.main:app",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
