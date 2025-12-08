"""
Setup configuration for Echo AI Trading Intelligence Platform
"""
from setuptools import setup, find_packages

with open("README_NEW.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="echo-ai-dashboard",
    version="1.0.0",
    author="Echo AI Team",
    author_email="support@echo-ai.com",
    description="AI-powered trading intelligence platform with real-time analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OxainZ/echo-ai-dashboard",
    packages=find_packages(exclude=["tests", "tests.*", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.2",
        "numpy>=1.26",
        "pydantic>=2.8",
        "pyyaml>=6.0",
        "requests>=2.32",
        "python-dateutil>=2.9",
        "yfinance>=0.2.43",
        "streamlit>=1.37",
        "plotly>=5.23",
        "streamlit-autorefresh>=1.0.0",
        "scikit-learn>=1.3.0",
    ],
    extras_require={
        "ml": [
            "tensorflow>=2.15.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "security": [
            "python-dotenv>=1.0.0",
            "cryptography>=41.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "echo-dashboard=UI:main",
        ],
    },
)
