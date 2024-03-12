### Custom ECG Analysis Module

Overview
This repo ECG analysis module provides enhanced functionality for reading and analyzing ECG records in the WFDB format. With this module, users can perform descriptive analysis, visualize ECG signals, and extract key features from the data.

From [read_record.py](read_record.py) module,

The read_record.py file contains the implementation of the Record and RecordReader classes. These classes facilitate reading ECG records, extracting signal data, annotations, sample indices, comments, and sampling frequency, and providing various analysis functionalities.

*Record Class*

The Record class represents an ECG record and encapsulates its properties and functionalities. It includes methods for descriptive analysis, extracting intervals, finding specific symbols, and analyzing rhythm intervals.

*RecordReader Class*

The RecordReader class provides a method read() for reading ECG records from the specified path. It extracts signal data, annotations, sample indices, comments, and sampling frequency, and returns a Record object representing the record.

In the [Notebook](descriptive_analysis.ipynb),

The custom module read_record.py to read and analyze a sample ECG record is utilized. The module provides functionality to extract essential information such as signal data, annotations, sample indices, comments, and sampling frequency from the ECG record,etc. 

To gain a deeper understanding, the presence of irregular beats using a donut graph is plotted. This visualization helps visualize the distribution of beat types and identify irregularities in the ECG signal. Furthermore, some functions available in the module by printing out key details about the ECG record is showcased.



