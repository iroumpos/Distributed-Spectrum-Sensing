import h5py
import numpy as np
import matplotlib.pyplot as plt
import sys

def spectrum_results(filepath):
	# Open the HDF5 file
	with h5py.File(filepath, 'r') as f:
	    frequencies = []
	    psd_values = []
	    for key in f.keys():
	    	if key.startswith('f_'):
	    		frequencies.append(f[key][:])
	    	elif key.startswith('psd_dB'):
	    		psd_values.append(f[key][:])

	# Concatenate the arrays
	all_frequencies = np.concatenate(frequencies)
	all_psd_values = np.concatenate(psd_values)


	print(all_frequencies)
	# Plot the spectrum
	plt.plot(all_frequencies, all_psd_values)
	plt.xlabel("Frequency")
	plt.ylabel("PSD (dB)")
	plt.title("Complete Spectrum")
	plt.show()
	
def spectrogram(filepath,sample_rate,start,end):
	# Open the HDF5 file
	with h5py.File(filepath, 'r') as f:
	    spectrogram = []
	    time_axis = []
	    for key in f.keys():
	    	if key.startswith('spect'):
	    		spectrogram.append(f[key][:])
	    	elif key.startswith('time'):
	    		time_axis.append(f[key][:])

	# Concatenate the arrays
	all_spectrogram = np.concatenate(spectrogram)
	all_time_axis = np.concatenate(time_axis)
	
	plt.imshow(np.array(all_spectrogram).T, aspect='auto', extent=[0, len(all_time_axis) * 0.01, start - sample_rate / 2, end + sample_rate / 2])
	plt.xlabel('Time')
	plt.ylabel('Frequency (Hz)')
	plt.title('Spectrogram')
	plt.colorbar(label='PSD (dB)')
	plt.show()
 
 
filepath = sys.argv[1]
option = int(sys.argv[2])

if(option == 1):
	spectrum_results(filepath)
elif (option == 2):
	sample_rate = float(input("Enter the sample rate: "))
	start = float(input("Enter the start of the spectrum: "))
	df = float(input("Enter the spectrums range: "))
	spectrogram(filepath,sample_rate,start,start+df)	
	
