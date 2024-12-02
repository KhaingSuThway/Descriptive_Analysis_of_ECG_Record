import os
import math
import wfdb
import numpy as np
import polars as pl
import streamlit as st
import matplotlib.pyplot as plt
def find_rhythm_interval(record_name, database_path=None):
    """
    Find rhythm intervals based on rhythm annotations and their corresponding indices.

    Parameters:
    - record_name: The name of the record file (without extension) or full path for local files
    - database_path: Path to the database directory or empty string for local files

    Returns:
    - A Polars DataFrame containing the start, end, rhythm information, and associated signals and annotations.
    """
    try:
        if database_path:
            # Using database path
            record = wfdb.rdrecord(record_name=record_name, pn_dir=database_path)
            record_annotations = wfdb.rdann(record_name=record_name, pn_dir=database_path, extension='atr')
        else:
            # Using local files with full path
            record = wfdb.rdrecord(record_name)
            record_annotations = wfdb.rdann(record_name, extension='atr')
    except Exception as e:
        raise Exception(f"Error reading WFDB files: {str(e)}")

    rd_signal = record.p_signal[:,0]
    rd_fs = record.fs
    rd_name = record.record_name

    rd_beat_annotations = record_annotations.symbol
    rd_rhythm_annotations = record_annotations.aux_note
    rd_annotated_indices = record_annotations.sample
        # First, find the location and the rhythm by removing the empty strings
    location = []
    rhythm = []
    for index, annotation in enumerate(rd_rhythm_annotations):
        if annotation != '':
            location.append(index)
            rhythm.append(annotation)
            
    #Then, find the start and end indices of the rhythm
    rhythm_start=[]
    rhythm_end=[]
    for i in range(len(location)):
        start_index = rd_annotated_indices[location[i]]
        if i<len(location)-1:
            end_index = rd_annotated_indices[location[i+1]]-1
        else:
            end_index = len(rd_signal)-1
        rhythm_start.append(start_index)
        rhythm_end.append(end_index)
    
    #Finally, create a table with the start, end, and rhythm information
    rhythm_table = pl.DataFrame({'Start': rhythm_start, 'End': rhythm_end, 'rhythm': rhythm})
    
    interval_duration = []
    IntervalSignal=[]
    IntervalAnnotatedIndices=[]
    IntervalBeatAnnotations=[]
    IntervalRhythmAnnotations=[]
    NoOfPAC=[]
    NoOfPVC=[]
    
    for row in range(len(rhythm_table)):
        
        sampfrom = rhythm_table['Start'][row]
        sampto = rhythm_table['End'][row]
        interval_signal = rd_signal[sampfrom:sampto]
        interval_duration.append(round(len(interval_signal)/rd_fs,2))
        IntervalSignal.append(interval_signal)
        # Find indices where the annotated indices fall within the specified range
        annotation_samp = np.intersect1d(np.where(sampfrom <= rd_annotated_indices), np.where(sampto >= rd_annotated_indices))
            
        # Calculate interval samples
        interval_sample = rd_annotated_indices[annotation_samp] - sampfrom
        IntervalAnnotatedIndices.append(interval_sample)
        
        # append beat annotations
        interval_beat_annotations = [rd_beat_annotations[annotation_samp[i]] for i in range(len(annotation_samp))]
        IntervalBeatAnnotations.append(interval_beat_annotations)
        # append rhythm annotations
        interval_rhythm_annotations = [rd_rhythm_annotations[annotation_samp[i]] for i in range(len(annotation_samp))]
        IntervalRhythmAnnotations.append(interval_rhythm_annotations)
        
        NoOfPAC.append(interval_beat_annotations.count('A'))
        NoOfPVC.append(interval_beat_annotations.count('V'))
        
    rhythm_table = rhythm_table.with_columns([
    pl.Series("IntervalDuration", interval_duration),
    pl.Series("IntervalSignal", IntervalSignal),
    pl.Series("IntervalAnnotatedIndices", IntervalAnnotatedIndices),
    pl.Series("IntervalBeatAnnotations", IntervalBeatAnnotations),
    pl.Series("IntervalRhythmAnnotations", IntervalRhythmAnnotations),
    pl.Series("NoOfPAC", NoOfPAC),
    pl.Series("NoOfPVC", NoOfPVC)
    ])
    
    rhythm_table = rhythm_table.with_columns([
    pl.Series("RecordName", [rd_name for _ in range(len(rhythm_table))]),  
    pl.Series("RecordFs", [rd_fs for _ in range(len(rhythm_table))]) 
    ])
    # Rearranging the columns of the rhythm_table
    rhythm_table = rhythm_table.select([
        "RecordName",
        "RecordFs",
        "rhythm",
        "Start",
        "End",
        "IntervalDuration",
        "IntervalSignal",
        "IntervalBeatAnnotations",
        "IntervalAnnotatedIndices",
        "IntervalRhythmAnnotations",
        "NoOfPAC",
        "NoOfPVC"
    ])
    # Clean the 'rhythm' column by removing the opening parenthesis '('
    rhythm_table = rhythm_table.with_columns(pl.col("rhythm").str.replace("(", "", literal=True))
    return rhythm_table

def rhythm_summary(record_rhythm_table):
    """
    Create a summary of rhythm statistics from the record rhythm table.
    
    Parameters:
    - record_rhythm_table: Polars DataFrame containing rhythm data
    
    Returns:
    - Polars DataFrame with rhythm statistics
    """
    # Calculate frequency of rhythms and rename the column
    frequency_of_rhythms = record_rhythm_table['rhythm'].value_counts().rename({"count": "frequency"})

    # Initialize lists for statistics
    min_duration = []
    max_duration = []
    mean_duration = []
    std_duration = []
    total_duration = []
    pac_count = []
    pvc_count = []
    
    # Process each rhythm
    for rhythm in frequency_of_rhythms['rhythm']:
        # Filter data for current rhythm
        rhythm_data = record_rhythm_table.filter(pl.col("rhythm") == rhythm)
        
        # Calculate duration statistics
        durations = rhythm_data['IntervalDuration'].to_list()
        min_duration.append(min(durations))
        max_duration.append(max(durations))
        mean_duration.append(np.mean(durations))
        std_duration.append(np.std(durations))
        total_duration.append(sum(durations))
        # Flatten beat annotations and count arrhythmias
        beat_annotations = [item for sublist in rhythm_data['IntervalBeatAnnotations'].to_list() for item in sublist]
        pac_count.append(beat_annotations.count('A'))
        pvc_count.append(beat_annotations.count('V'))
    
    # Add statistics to the frequency table
    summary_table = frequency_of_rhythms.with_columns([
        pl.Series("min(sec)", min_duration),
        pl.Series("max(sec)", max_duration),
        pl.Series("mean(sec)", mean_duration),
        pl.Series("std(sec)", std_duration),
        pl.Series("total(sec)", total_duration),
        pl.Series("PAC", pac_count),
        pl.Series("PVC", pvc_count)
    ])
    
    return summary_table

def create_segments(record_rhythm_table, window_size, window_step, progress_callback=None):
    """
    Create segments from rhythm table.
    
    Args:
        record_rhythm_table: Input rhythm table
        window_size: Size of each segment window in seconds
        window_step: Step size between windows in seconds
        progress_callback: Optional callback function to report progress
    """
    window_size = window_size  # seconds
    window_step = window_step  # seconds
    parent_record_name = []
    segmented_intervalNo = []
    segmented_intervalFs = []
    segmented_signal = []
    segmented_beat_annotations = []
    segmented_rhythm_annotations = []
    segmented_annotated_indices = [] 
    
    for row in range(len(record_rhythm_table)):     
        
        signal = record_rhythm_table['IntervalSignal'][row]
        beat_annotations = record_rhythm_table['IntervalBeatAnnotations'][row]
        annotated_indices = record_rhythm_table['IntervalAnnotatedIndices'][row]
        rd_name = record_rhythm_table['RecordName'][row]
        rhythm = record_rhythm_table['rhythm'][row]
        signal_fs = record_rhythm_table['RecordFs'][row]
        signal_duration = record_rhythm_table['IntervalDuration'][row]
        # Convert durations to samples
        window_size_samples = int(window_size * signal_fs)
        window_step_samples = int(window_step * signal_fs)
        
        if signal_duration < window_size:
            if progress_callback:
                progress_callback(f"Skipping interval {row} of {rd_name} (duration: {signal_duration}s)")
            continue    
    
        if signal_duration >= window_size:
            if progress_callback:
                progress_callback(f"Processing interval {row} of {rd_name} (duration: {signal_duration}s)")
            
                     
            no_of_segments = int((len(signal) - window_size_samples) / window_step_samples) + 1            
            
            intervalNo = []
            intervalFs = []
            intervalParent = []

            segmentSignal = []
            segmentBeatAnnotations = []
            segmentRhythmAnnotations = []
            segmentAnnotatedIndices = []
            
            left_index = 0
            right_index = left_index + window_size_samples
            while (left_index < (len(signal) - window_size_samples)) and (right_index <= len(signal)):
                intervalNo.append(row)
                intervalFs.append(signal_fs)
                intervalParent.append(rd_name)
                segmentRhythmAnnotations.append(rhythm)                
                
                # Extract segment signal
                interval_signal = signal[left_index:right_index]        
                segmentSignal.append(interval_signal)

                # Find indices where the annotations fall within the range
                annotation_samp = np.where((annotated_indices >= left_index) & (annotated_indices < right_index))[0]
                    
                # Calculate interval samples
                interval_sample = annotated_indices[annotation_samp] - left_index
                segmentAnnotatedIndices.append(interval_sample)
                
                # Append beat annotations
                interval_beat_annotations = beat_annotations[annotation_samp]
                segmentBeatAnnotations.append(interval_beat_annotations)
                
                # Update indices
                left_index += window_step_samples
                right_index = left_index + window_size_samples
                
            if progress_callback:
                progress_callback(f"Created {no_of_segments} segments")
        parent_record_name.append(intervalParent)
        segmented_intervalNo.append(intervalNo)
        segmented_intervalFs.append(intervalFs)
        segmented_signal.append(segmentSignal)
        segmented_beat_annotations.append(segmentBeatAnnotations)
        segmented_rhythm_annotations.append(segmentRhythmAnnotations)
        segmented_annotated_indices.append(segmentAnnotatedIndices)
    segmented_table=pl.DataFrame({
    'RecordName':[parent_record_name[i][j] for i in range(len(parent_record_name)) for j in range(len(parent_record_name[i]))],
    'intervalNo':[segmented_intervalNo[i][j] for i in range(len(segmented_intervalNo)) for j in range(len(segmented_intervalNo[i]))],
    'signals':[segmented_signal[i][j] for i in range(len(segmented_signal)) for j in range(len(segmented_signal[i]))],
    'annotations':[segmented_beat_annotations[i][j] for i in range(len(segmented_beat_annotations)) for j in range(len(segmented_beat_annotations[i]))],
    'indices':[segmented_annotated_indices[i][j] for i in range(len(segmented_annotated_indices)) for j in range(len(segmented_annotated_indices[i]))],
    'rhythm_type':[segmented_rhythm_annotations[i][j] for i in range(len(segmented_rhythm_annotations)) for j in range(len(segmented_rhythm_annotations[i]))]
    })
    
    return segmented_table


def plot_rhythm_summary(rhythm_summary):
    # Create figure
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 20))
    plt.rcParams['font.sans-serif'] = ['Arial']

    # Get data from Polars DataFrame
    rhythms = rhythm_summary['rhythm'].to_list()
    frequencies = rhythm_summary['frequency'].to_list()
    means = rhythm_summary['mean(sec)'].to_list()
    stds = rhythm_summary['std(sec)'].to_list()
    durations = rhythm_summary['total(sec)'].to_list()

    # Plot frequency
    ax1.bar(rhythms, frequencies)
    ax1.set_title('Frequency of Rhythms')
    ax1.set_xlabel('Rhythm Type')
    ax1.set_ylabel('Frequency')
    ax1.tick_params(axis='x', rotation=45)

    # Plot mean duration
    ax2.bar(rhythms, means)
    ax2.set_title('Mean Duration of Rhythms')
    ax2.set_xlabel('Rhythm Type')
    ax2.set_ylabel('Mean Duration (seconds)')
    ax2.tick_params(axis='x', rotation=45)

    # Plot standard deviation
    ax3.bar(rhythms, stds)
    ax3.set_title('Standard Deviation of Rhythm Durations')
    ax3.set_xlabel('Rhythm Type')
    ax3.set_ylabel('Standard Deviation (seconds)')
    ax3.tick_params(axis='x', rotation=45)

    # Plot total duration
    ax4.bar(rhythms, durations)
    ax4.set_title('Total Duration of Rhythms')
    ax4.set_xlabel('Rhythm Type')
    ax4.set_ylabel('Total Duration (seconds)')
    ax4.tick_params(axis='x', rotation=45)

    # Adjust layout
    plt.tight_layout()
    
    # Display plot in Streamlit
    st.pyplot(fig)

    # Optional: Add text summary
    st.write("### Summary Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        max_frequency_rhythm = rhythm_summary.sort('frequency', descending=True).limit(1)['rhythm'].item()
        frequency = rhythm_summary.filter(pl.col('rhythm') == max_frequency_rhythm)['frequency'].item()
        st.write(f"Most frequent rhythm: **{max_frequency_rhythm}** ({frequency} occurrences)")
    
    with col2:
        max_duration_rhythm = rhythm_summary.sort('total(sec)', descending=True).limit(1)['rhythm'].item()
        max_rhythm_duration = rhythm_summary.filter(pl.col('rhythm') == max_duration_rhythm)['total(sec)'].item()
        st.write(f"Longest duration rhythm: **{max_duration_rhythm}** ({round(max_rhythm_duration, 2)} seconds)")