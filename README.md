# ECG Analysis & Rhythm Segmentation Tool

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40.2-red.svg)](https://streamlit.io/)
[![WFDB](https://img.shields.io/badge/WFDB-4.1.2-green.svg)](https://physionet.org/content/wfdb-python/latest/)

A comprehensive web application for analyzing ECG signals and detecting cardiac rhythm patterns. This tool provides automated rhythm segmentation and analysis capabilities for both standard databases and custom ECG recordings.

### Features

- **Database Integration**: Direct access to standard ECG databases
  - MIT-BIH Arrhythmia Database (48 records)
  - Long Term AF Database (84 records)

- **Signal Processing**:
  - Automated rhythm interval detection
  - Customizable signal segmentation
  - Beat annotation analysis
  - PAC/PVC detection

- **Data Export**:
  - JSON format export for further analysis
  - Detailed rhythm tables
  - Segmented signal data

- **Custom Upload Support**:
  - Support for WFDB format files
  - Handles custom ECG recordings
  - Real-time processing

To run locally, please follow the instructions below:

```bash
git clone https://github.com/yourusername/ecg-analysis-tool.git
cd ecg-analysis-tool
pip install -r requirements.txt
streamlit run streamlitApp.py   
```
To run the app on the streamlit community cloud, please click the link below:

[ECG Analysis & Rhythm Segmentation Tool](https://ecg-analysis-tool-streamlit.streamlit.app/)








