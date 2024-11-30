# ECG Analysis & Rhythm Segmentation Tool

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40.2-red.svg)](https://streamlit.io/)
[![WFDB](https://img.shields.io/badge/WFDB-4.1.2-green.svg)](https://physionet.org/content/wfdb-python/latest/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

A  web application for analyzing ECG (Electrocardiogram) signals and detecting cardiac rhythm patterns. This tool is designed for healthcare professionals, researchers, and data scientists working with ECG data, offering automated rhythm segmentation and comprehensive analysis capabilities.

## Key Features

### Signal Processing & Analysis
- **Automated Rhythm Detection**: Identifies and segments different cardiac rhythms
- **Arrhythmia Detection**: Specialized detection of PAC (Premature Atrial Contractions) and PVC (Premature Ventricular Contractions)
- **Customizable Segmentation**: Flexible window sizes and step parameters for detailed analysis
- **Real-time Processing**: Instant analysis of uploaded ECG recordings

### Data Visualization
- **Interactive Plots**: Visual representation of rhythm distributions
- **Statistical Summaries**: Comprehensive statistics for each rhythm type
- **Beat Annotation Display**: Clear visualization of beat annotations and intervals

### Database Integration
- **MIT-BIH Arrhythmia Database**: Access to 48 half-hour recordings
- **Long-Term AF Database**: Support for 84 long-term ECG recordings
- **Custom Upload Support**: Compatible with WFDB format files

## Getting Started

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone [https://github.com/yourusername/ecg-analysis-tool.git](https://github.com/KhaingSuThway/ECG_Analysis-_Rhythm_Segmentation_Tool.git)
cd ecg-analysis-tool
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run streamlitApp.py
```

## Usage Examples

### Analyzing Standard Database Records
1. Select database (MIT-BIH or LTAF)
2. Choose a record number
3. View rhythm statistics and visualizations
4. Export analysis results in JSON format

### Processing Custom ECG Files
1. Upload WFDB format files (.dat, .hea, .atr)
2. Configure analysis parameters
3. Generate rhythm segments and statistics
4. Download results for further analysis

## Technical Details

### Core Components
- **Rhythm Segmentation**: Custom algorithms for detecting rhythm boundaries
- **Beat Segmentation**: Based on custom window size, the signal within specific rhythm boundaries are segmented
- **Statistical Analysis**: Comprehensive metrics for rhythm characterization

### File Structure
```
project_root/
├── src/
│   ├── __init__.py
│   ├── app/
│   │   ├── __init__.py
│   │   └── streamlit_app.py
│   └── processing/
│       ├── __init__.py
│       ├── rhythm_segmentation.py
│       └── read_record.py
├── setup.py
└── requirements.txt
```

## Applications

- Generation of annotated single lead ECG datasets for AI/ML training
- Visualization of data distribution within the original dataset

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions and support, please [open an issue](https://github.com/KhaingSuThway/Descriptive_Analysis_of_ECG_Record/issues)




