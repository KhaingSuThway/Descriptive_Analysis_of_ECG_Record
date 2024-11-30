import os
import wfdb
import numpy as np
import pandas as pd
from collections import Counter

class Record:
    
    """Class representing an ECG record."""
    
    def __init__(self, parent, signal, symbol, aux, sample, label, sf):
        
        """
        Initialize a Record object.

        Args:
            parent (str): The parent of the record.
            signal (np.ndarray): The ECG signal.
            symbol (np.ndarray): Annotation symbols.
            aux (np.ndarray): Auxiliary information.
            sample (np.ndarray): Sample indices of annotations.
            label (str): Label or comment associated with the record.
            sf (int): Sampling frequency of the signal.
        """
        
        self.__parent = parent
        self.__signal = signal
        self.__symbol = symbol
        self.__aux = aux
        self.__sample = sample
        self.__label = label
        self.__sf = sf
        self.__collection = {"signal": self.__signal,
                             "symbol": self.__symbol,
                             "aux": self.__aux,
                             "sample": self.__sample,
                             "label": self.__label,
                             "sampling_frequency": self.__sf,
                             "has_missed_beat": self.has_missed_beat(),
                             "has_unknown_beat": self.has_unknown_beat()}
    
    def __getitem__(self, key):
        return self.__collection[key]
    
    def __str__(self):
        return "Summary\n" + \
               "Size of signal: " + str(len(self.__signal)) + \
               "\nSize of symbol: " + str(len(self.__symbol)) + \
               "\nSize of aux: " + str(len(self.__aux)) + "\n" 
    
    def get_interval(self):
        return (self.__sampfrom, self.__sampto)
    
    def get_indexes_of(self, this=None):
        
        """
        Get indexes of a specific symbol or auxiliary annotation.

        Args:
            this (str): The symbol or annotation to search for.

        Returns:
            np.ndarray: An array of indexes where the symbol or annotation is found.
        """
        
        
        if (len(self.__symbol) > 0) and (len(self.__aux)) > 0:
            if this == "+":
                return np.where(np.asarray(self.__symbol) == "+")[0]
            elif this == "(N":
                return np.where(np.asarray(self.__aux) == '(N')[0]
            
    def get_intersect_of(self, a, b):
        """
        Get the intersection of two arrays.

        Args:
            a (np.ndarray): First array.
            b (np.ndarray): Second array.

        Returns:
            tuple: A tuple containing the intersection of the arrays and their indices.
        """
        return np.intersect1d(a, b, return_indices=True)
    
    def get_rhythm_interval(self):
        rhythm_interval = list()
        plus_indexes = self.get_indexes_of('+')
        N_indexes = self.get_indexes_of("(N")
        if len(plus_indexes) != 0 and len(N_indexes) != 0:
            _, a_indexes, b_indexes = self.get_intersect_of(a=N_indexes, b=plus_indexes)
            for i in range(len(b_indexes)-1):
                interval_start = N_indexes[i]
                interval_end = plus_indexes[b_indexes[i]+1]
                interval = (self.__sample[interval_start], self.__sample[interval_end])
                rhythm_interval.append(interval)
            if plus_indexes[-1] == N_indexes[-1]:
                interval = (self.__sample[N_indexes[-1]], len(self.__signal))
                rhythm_interval.append(interval)
        return rhythm_interval
    
    def get_valid_rhythm_interval(self):
        rhythm_intervals = self.get_rhythm_interval()
        return [itval for itval in rhythm_intervals if self.is_interval_valid(interval=itval,
                                                                           sampling_freq=200,
                                                                           duration=30)]
        
    def is_interval_valid(self, interval, sampling_freq, duration):
        return abs(interval[1] - interval[0]) >= (sampling_freq * duration)
    
    def find_index_of_symbol(self, symbol):
        if symbol in self.__symbol:
            return np.where(np.asarray(self.__symbol) == symbol)[0]
        return -1
    
    def find_q_index(self):
        return self.find_index_of_symbol('Q')
    
    def find_quote_index(self):
        return self.find_index_of_symbol('"')
    
    def has_unknown_beat(self):
        return ("Q" in self.__symbol)
    
    def has_missed_beat(self):
        return ('"' in self.__symbol)    
   
    def move_to_any_q_or_quote(self):
        q_index = self.find_q_index()
        quote_index = self.find_quote_index()
        move_index = q_index + quote_index
        return max(move_index)
    
    def move_to_no_pac(self):
        pac_indexes = self.find_index_of_symbol("A")
        return max(pac_indexes)
    
    def move_to_no_pvc(self):
        pvc_indexes = self.find_index_of_symbol("V")
        return max(pvc_indexes)
    
    def has_pac(self):
        return ("A" in self.__symbol)
    
    def has_pvc(self):
        return ("V" in self.__symbol)
    
    def get_pac_percentage(self):
        pac_count = self.get_pac_counts()
        if len(self.__symbol) > 0:
            return (pac_count / len(self.__symbol)) * 100
        else:
            return 0
    
    def get_pvc_percentage(self):
        pvc_count = self.get_pvc_counts()
        if len(self.__symbol) > 0:
            return (pvc_count / len(self.__symbol)) * 100
        else:
            return 0
    
    def is_positive(self, arr_type):
        if arr_type == "PAC":
            percentage = self.get_pac_percentage()
            return ((19 < percentage) and (self.get_pvc_counts() == 0))
        if arr_type == "PVC":
            percentage = self.get_pvc_percentage()
            return ((19 < percentage) and (self.get_pac_counts() == 0))            
        
    def get_pac_counts(self):
        return Counter(self.__symbol)['A']
    
    def get_pvc_counts(self):
        return Counter(self.__symbol)['V']
    
    def get_label(self):
        return self.__label
    
    def get_sampling_frequency(self):
        return self.__sf
    
    def get_duration(self):
        duration = len(self.__signal) / self.__sf
        return duration 
    
    def which(self):
        return self.__parent
    
class RecordReader:
    """Class for reading ECG records."""
    
    @classmethod
    def read(cls, path, number, channel, sampfrom, sampto):
        
        """
        Read an ECG record.

        This method reads an ECG record from the specified path, extracts the signal,
        annotations, sample indices, comments, and sampling frequency, and returns
        a Record object representing the record.

        Args:
            path (str): The path to the directory containing the record.
            number (str): The name or identifier of the record.
            channel (int): The channel number of the ECG signal to read.
            sampfrom (int): Starting sample index to read.
            sampto (int): Ending sample index to read.

        Returns:
            Record: A Record object representing the ECG record.

        Raises:
            ValueError: If the specified record file cannot be found or read.
            ValueError: If the specified record annotations cannot be found or read.
        """
        
        
        fullpath = os.path.join(path, number)
        signal = wfdb.rdrecord(fullpath,
                               sampfrom=sampfrom,
                               sampto=sampto).p_signal[:, channel]
        
        ann = wfdb.rdann(fullpath, 'atr',
                            shift_samps=True,
                            sampfrom=sampfrom,
                            sampto=sampto)
        
        symbol = ann.symbol
        aux = ann.aux_note
        sample = ann.sample
        comment = wfdb.rdrecord(fullpath).comments[0]
        sf = wfdb.rdrecord(fullpath).fs
        
        return Record(parent=number,
                      signal=signal,
                      symbol=symbol,
                      aux=aux,
                      sample=sample,
                      label=comment,
                      sf=sf)
