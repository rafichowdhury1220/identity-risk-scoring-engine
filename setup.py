"""Setup configuration for Identity Risk Scoring Engine."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="identity-risk-scoring-engine",
    version="1.0.0",
    author="Priya Arora",
    author_email="priya@example.com",
    description="Enterprise-grade identity risk assessment and access control system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/identity-risk-scoring-engine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
        ],
        "db": [
            "sqlalchemy>=2.0.0",
            "psycopg2-binary>=2.9.0",
        ],
        "security": [
            "bcrypt>=4.0.0",
            "cryptography>=41.0.0",
            "pyjwt>=2.8.0",
        ],
    },
)
