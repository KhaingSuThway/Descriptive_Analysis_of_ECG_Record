from setuptools import setup, find_packages

# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ecg-analysis-tool",
    version="0.1.0",
    author="Khaing",
    author_email="",
    description="A web application for ECG signal analysis and rhythm segmentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KhaingSuThway/ECG_Analysis_Rhythm_Segmentation_Tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.11",
    install_requires=[
        "streamlit>=1.40.2",
        "wfdb>=4.1.2",
        "numpy>=1.24.0",
        "polars>=0.20.0",
        "matplotlib>=3.7.0",
        "neurokit2>=0.2.0"
    ],
    entry_points={
        "console_scripts": [
            "ecg-analysis=streamlitApp:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/KhaingSuThway/ECG_Analysis_Rhythm_Segmentation_Tool",
        "Source": "https://github.com/KhaingSuThway/ECG_Analysis_Rhythm_Segmentation_Tool",
        "Documentation": "https://github.com/KhaingSuThway/ECG_Analysis_Rhythm_Segmentation_Tool#readme",
    },
)
