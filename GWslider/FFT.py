#from wave_gen import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from constants import *
#from constants import * 


#plt.plot(data_times, data_strains)
plt.ylabel('Time Domain') 

FFT_waveform= np.fft.fft(data_strains)
frequencies= np.fft.fftfreq(len(data_times), d=data_times[1] - data_times[0])
#find out where num are neg and cut them out & cut out same elements from FFT waveform 
index_pos = np.where(frequencies > 0.)
freq_pos = frequencies[index_pos]
FFT_waveform_pos = FFT_waveform[index_pos]
#plt.plot(freq_pos, np.abs(FFT_waveform_pos))

plt.show()


IFFT_waveform= np.fft.ifft(FFT_waveform)
# interpolation !

#put in constants ! 
f_min = 10.
f_max = 1024.
Nf = 2**14 + 1
freqs = np.linspace(0., f_max, Nf)

interp_func= interp1d(frequencies, FFT_waveform)

intrp_waveform= interp_func(freqs)

plt.plot(freqs, intrp_waveform, color= 'green', lw=4)
plt.plot(frequencies, FFT_waveform, color= 'blue')
plt.show()

