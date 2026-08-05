#!/usr/bin/env python3
"""
Setup configuration for Alteryx Metrics CLI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements
requirements_path = Path(__file__).parent / 'requirements.txt'
install_requires = [
    line.strip() for line in requirements_path.read_text().split('\n')
    if line.strip() and not line.startswith('#')
]

setup(
    name="alteryx-metrics-cli",
    version="2.0.0",
    description="Production-grade metrics query system for Alteryx products",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Alteryx Product Team",
    author_email="dhiraj.sahu@alteryx.com",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "optional": [
            "fastapi>=0.100",
            "uvicorn>=0.20",
            "psycopg2-binary>=2.9",
            "pgvector>=0.1",
            "anthropic>=0.7",
        ]
    },
    entry_points={
        "console_scripts": [
            "metrics=metrics_cli.cli.main:app",
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="metrics query cli snowflake alteryx analytics",
    project_urls={
        "Documentation": "https://github.com/alteryx/metrics-cli/docs",
        "Source": "https://github.com/alteryx/metrics-cli",
        "Tracker": "https://github.com/alteryx/metrics-cli/issues",
    },
)
