from setuptools import setup, find_packages

# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ecg_analysis_tool",
    version="0.1.0",
    author="Your Name",
    description="ECG Analysis & Rhythm Segmentation Tool",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.40.2",
        "wfdb>=4.1.2",
        "numpy>=1.24.0",
        "polars>=0.20.0",
        "matplotlib>=3.7.0",
        "neurokit2>=0.2.0"
    ],
)
