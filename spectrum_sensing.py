import adi
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
import math
import h5py
import sys

def psd_value(rx_samples):
    rx_samples = rx_samples * np.hamming(len(rx_samples))  # Hamming window
    fft_result = np.fft.fft(rx_samples)
    psd = np.abs(np.fft.fftshift(fft_result))**2
    return psd

# This function returns the index of the element in array that contains
# the value which is closer to the given number
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def spectrum_sensing(sdr, start, end, sample_rate, filepath_data, filepath_spect, bandwidth):
    # Configuration for PlutoSDR
    num_samples = 100000
    
    sdr.gain_control_mode_chan0 = 'manual'
    if start < 4e9:
        sdr.rx_hardwaregain_chan0 = 64.0
    else:
        sdr.rx_hardwaregain_chan0 = 50.0
    sdr.rx_lo = int(start - sample_rate)
    sdr.sample_rate = int(sample_rate)
    sdr.rx_rf_bandwidth = int(sample_rate)
    sdr.rx_buffer_size = num_samples

    # Value outside the spectrum
    value = start - 10e6
    sdr.rx_lo = int(value)
    rx_samples = sdr.rx()
    
    # Threshold value of psd
    threshold = np.mean(psd_value(rx_samples))
    threshold_dB = 10*np.log10(threshold)
    print("Threshold: ", threshold_dB)
    
    # Number of center frequencies
    num = int((sample_rate/100e3) + 1)
    
    # Array of frequencies
    freqs = np.linspace(-sample_rate/2, sample_rate/2, num)
    
    # Array of frequency values of each FFT bin
    fft_freq = np.fft.fftshift(np.fft.fftfreq(len(rx_samples), d=1/sample_rate))

    
    # Frequency dictionary 
    frequency_dict = {}
    
    
    for i in range(num):
        if (i == 0):
            stop_index = find_nearest(fft_freq, value=(freqs[i] + bandwidth/2))
            frequency_dict[i] = list()
            frequency_dict[i].append(stop_index)
        elif (i == num - 1):
            start_index = find_nearest(fft_freq, value=(freqs[i] - bandwidth/2)) 
            frequency_dict[0].insert(0, start_index)
        else:
            start_index = find_nearest(fft_freq, value=(freqs[i] - bandwidth/2))
            stop_index = find_nearest(fft_freq, value=(freqs[i] + bandwidth/2))
            frequency_dict[i] = list()
            frequency_dict[i].append(start_index)
            frequency_dict[i].append(stop_index)

    temp_freq = 0
    counter = 0
    end_value = 0
    rx_lo_change = []
    list_of_freqs = []
    freqs_trans = []
    spectrum = []
    next_value = start
    
    # Output file that saves the results of spectrum sensing
    output_file = filepath_data
    #Output file for the spectrogram
    spect_file = filepath_spect

    	
    while next_value <= end:
        rx_lo_change.append(start + counter)
        rcv_time = time.time()

        iter = 0
        fl = datetime.datetime.now()
        # 50 samples of received signal
        while iter < 50:
            rx_samples = sdr.rx()
            iter += 1
            
                
        psd_shifted = psd_value(rx_samples)
        
        psd_dB = 10*np.log10(psd_shifted)
        f_axis = np.linspace(next_value-bandwidth/2,next_value+bandwidth/2, len(psd_shifted))
        
        print(next_value-bandwidth/2,next_value+bandwidth/2)
        spectrogram = []
        time_axis = []
        
        spectrogram.append(psd_dB)
        time_axis.append(time.time())
        

        with h5py.File(output_file, 'a') as f:  
        	f.create_dataset(f'psd_dB_{next_value}', data=psd_dB)  
        	f.create_dataset(f'f_{next_value}', data=f_axis)  
        
        with h5py.File(spect_file,'a') as fi:
        	fi.create_dataset(f'spect_{next_value}', data=spectrogram)
        	fi.create_dataset(f'time_{next_value}', data=np.array(time_axis))
 

        counter += int(1e6/1e6)
        next_value = start + counter*1e6
        
        print(int(next_value))
        sdr.rx_lo = int(next_value)

if __name__ == '__main__':
    sdr = adi.Pluto('ip:192.168.4.1')
    if(int(sys.argv[1]) == 2):
    	sdr2 = adi.Pluto('ip:192.168.2.1')

    print("Input spectrum start frequency and the range of the spectrum!")
    start = float(input("Give start of the spectrum(>70MHz): "))
    diff_freq = float(input("Give range of the spectrum: "))
    bandwidth = float(input("Give bandwidth value (<60MHz): "))
    # If pass 60MHz default value
    if(bandwidth > 60000000):
    	bandwidth = 1000000
    sample_rate = int(input("Give sample_rate (1Msps or 10Msps): "))
    if(sample_rate != 1e6 or sample_rate != 10e6):
    	sample_rate = 1e6
    
    end = start + diff_freq
    
    
    filepath_data = sys.argv[2]
    filepath_spect = sys.argv[3]
    
    spectrum_sensing(sdr, start, end, sample_rate, "sdr1" + filepath_data, "sdr1" + filepath_spect, bandwidth)
    if(int(sys.argv[1]) == 2):
    	spectrum_sensing(sdr2, start, end, sample_rate, "sdr2" + filepath_data, "sdr2" + filepath_spect, bandwidth)

