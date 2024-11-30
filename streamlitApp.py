import streamlit as st
import polars as pl
import os
from pathlib import Path
from tempfile import mkdtemp

from rhythm_segmentation import (
    find_rhythm_interval,
    create_segments,
    rhythm_summary,
    plot_rhythm_summary
)

def save_uploadedfiles(record_file, annotation_file, data_file):
    """Save uploaded files to a temporary directory and return the paths"""
    # Create a temporary directory with absolute path
    temp_dir = os.path.abspath(mkdtemp())
    
    # Get record name without extension
    record_name = os.path.splitext(record_file.name)[0]
    
    # Save all files with the same base name but different extensions
    record_path = os.path.join(temp_dir, f"{record_name}.hea")
    data_path = os.path.join(temp_dir, f"{record_name}.dat")
    annotation_path = os.path.join(temp_dir, f"{record_name}.atr")
    
    with open(record_path, 'wb') as f:
        f.write(record_file.getvalue())
    with open(data_path, 'wb') as f:
        f.write(data_file.getvalue())
    with open(annotation_path, 'wb') as f:
        f.write(annotation_file.getvalue())
    
    return temp_dir, record_name

st.title("ECG Rhythm Analysis & Segmentation Tool")

st.markdown("""
### A Comprehensive Tool for ECG Signal Processing and Analysis

**Features:**
-  Process ECG records from standard databases (MIT-BIH, LTAF)
-  Support for custom WFDB format files
-  Automatic rhythm interval detection
-  Customizable signal segmentation
-  Export results in JSON format

**Supported Databases:**
- MIT-BIH Arrhythmia Database (48 records, ~30 min each)
- Long Term AF Database (84 records, ~48 hours each)
""")

# Add a separator for better visual organization
st.markdown("---")

# File upload or database selection
upload_files = st.checkbox("Upload my own record files")

if upload_files:
    st.info("""
    Please upload all required files for your record:
    - Header file (.hea)
    - Data file (.dat)
    - Annotation file (.atr)
    
    Note: All files must have the same base name and be in WFDB format.
    """)
    
    record_file = st.file_uploader("Upload header file (.hea)", type="hea")
    data_file = st.file_uploader("Upload data file (.dat)", type="dat")
    annotation_file = st.file_uploader("Upload annotation file (.atr)", type="atr")
    
    if record_file and data_file and annotation_file:
        try:
            # Verify files have the same base name
            base_names = {os.path.splitext(f.name)[0] for f in [record_file, data_file, annotation_file]}
            if len(base_names) > 1:
                st.error("All files must have the same base name!")
                st.stop()
            
            # Save files to temporary directory
            temp_dir, record_name = save_uploadedfiles(record_file, annotation_file, data_file)
            
            try:
                # Force wfdb to use local files by using absolute path
                rhythm_table = find_rhythm_interval(
                    record_name=os.path.join(temp_dir, record_name), 
                    database_path=""  # Empty string to force local file reading
                )
                st.write(rhythm_table)
                record_id = record_name
            finally:
                # Clean up temporary directory
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            
        except Exception as e:
            st.error(f"Error processing uploaded files: {str(e)}")
            st.stop()
    else:
        st.warning("Please upload all required files")
        st.stop()

else:
    database_selection = st.selectbox(
        "Select a database",
        ["MIT-BIH Arrhythmia Database", "Long Term Atrial Fibrilation Database"]
    )
    
    if database_selection == "MIT-BIH Arrhythmia Database":
        db_path = "mitdb"
        record_options = ["100","101","102","103","104","105","106","107","108","109","111","112","113","114","115","116","117","118","119","121","122","123","124","200","201","202","203","204","205","206","207","208","209","210","211","212","213","214","215","216","217","218","219"]
    else:
        db_path = "ltafdb"
        record_options = ["00","01","03","05","06","07","08","10","11","12","13","15","16","17","18","19","20","21","22","23","24","25","26","28","30","32","33","34","35","37","38","39","42","43","44","45","47","48","49","51","53","54","55","56","58","60","62","64","65","68","69","70","71","72","74","75","100","101","102","103","104","105","110","111","112","113","114","115","116","117","118","119","120","121","122","200","201","202","203","204","205","206","207","208"]
    
    record_selection = st.selectbox("Select a record", record_options)
    record_id = record_selection
    st.write(f"Your selected record: {record_id} is now fetching from the physionet database...")
    
    try:
        rhythm_table = find_rhythm_interval(record_name=record_selection, database_path=db_path)
        st.write(rhythm_table)
    except Exception as e:
        st.error(f"Error loading record: {str(e)}")
        st.stop()

# Only show the rest if we have a rhythm table
if 'rhythm_table' in locals():
    # Download button for rhythm table
    json_str_rhythm = rhythm_table.write_json(None)
    st.download_button(
        label="Download rhythm table",
        data=json_str_rhythm,
        file_name=f"rhythm_table_{record_id}.json",
        mime="application/json"
    )
    
    # Show summary of the rhythm table
    summary_table = rhythm_summary(rhythm_table)
    st.subheader("Summary of Rhythm Statistics in the Record")
    st.write(summary_table)
             
    if st.button("Visualize Rhythm Summary"):                
        # Plot rhythm summary
        st.subheader("Visualization of Rhythm Statistics in the Record")  
        plot_rhythm_summary(summary_table)
        
     
            

    # Text input box 
    col1, col2 = st.columns(2)
    with col1:
        window_width = st.number_input("Window width (seconds)", min_value=1, value=30)
    with col2:
        window_step = st.number_input("Window step (seconds)", min_value=1, value=5)

    try:
        # Create a status container
        status_container = st.empty()
        
        def update_status(message):
            status_container.info(message)
        
        segments_table = create_segments(
            rhythm_table, 
            window_size=window_width, 
            window_step=window_step,
            progress_callback=update_status
        )
        
        # Clear the status messages when done
        status_container.empty()
        st.subheader("Created Segments of the Record")
        st.write(segments_table)
        
        # Download button for segments
        json_str_segments = segments_table.write_json(None)
        st.download_button(
            label="Download segments",
            data=json_str_segments,
            file_name=f"segments_{record_id}_w{window_width}_s{window_step}.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"Error creating segments: {str(e)}")

st.markdown("""
---
If you found any issues or have suggestions, please issue a ticket on the GitHub repository.
Any feedback is welcome.
""")
