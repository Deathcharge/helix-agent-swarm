"""
Setup configuration for helix-agent-swarm package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="helix-agent-swarm",
    version="1.0.0",
    description="Production-ready multi-agent orchestration framework for autonomous AI systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Andrew John Ward",
    author_email="contact@helixcollective.ai",
    url="https://github.com/Deathcharge/helix-agent-swarm",
    license="MIT",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0",
        "python-dotenv>=0.19.0",
        "aiohttp>=3.8.0",
        "asyncio-contextmanager>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "ruff>=0.1.0",
            "mypy>=1.0",
        ],
        "llm": [
            "openai>=1.0",
            "anthropic>=0.7",
        ],
        "storage": [
            "redis>=4.0",
            "sqlalchemy>=2.0",
        ],
        "tools": [
            "requests>=2.28",
            "beautifulsoup4>=4.11",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="agents orchestration multi-agent ai automation helix collective",
    project_urls={
        "Bug Tracker": "https://github.com/Deathcharge/helix-agent-swarm/issues",
        "Documentation": "https://github.com/Deathcharge/helix-agent-swarm/tree/main/docs",
        "Source Code": "https://github.com/Deathcharge/helix-agent-swarm",
    },
)
