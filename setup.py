"""
Setup script for Web Summarizer Agent
"""

from setuptools import setup, find_packages

setup(
    name="web-summarizer-agent",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
)
