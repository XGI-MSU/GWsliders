'''This file stores constants used throughout the slider program.'''


import numpy as np
import random
from pycbc.conversions import *
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

#load in data 
data_times, data_strains = np.loadtxt('data/GW150914.dat').T
#make FFT waveform wiht data 

#replace frequencies with freqs 
#FFT_waveform becomes new_sine wherever it (FFT_waveform) is called in code 
FFT_waveform= np.fft.fft(data_strains)

frequencies= np.fft.fftfreq(len(data_times), d=data_times[1] - data_times[0])
#find out where num are neg and cut them out & cut out same elements from FFT waveform 
#index_pos = np.where(frequencies > 0.)
#freq_pos = frequencies[index_pos]
#FFT_waveform_pos = FFT_waveform[index_pos]


# constants needed for unit conversion
c = 3.0e8  # speed of light
G = 6.67430e-11  # Newton's gravitational constant
Msun = 1.989e30  # mass of the Sun in kg
pc_SI = 3.08567758128e+16  # number of meters in one parsec


# define injected (true) parameters
# masses in solar masses
m1_inj = 50.
m2_inj = 30.
chi1_inj = 0.3
chi2_inj = -0.4
chirp_inj = mchirp_from_mass1_mass2(m1_inj, m2_inj)
ratio_inj = m2_inj / m1_inj
spin_plus_inj = chi_eff(m1_inj, m2_inj, chi1_inj, chi2_inj)
spin_minus_inj = chi_a(m1_inj, m2_inj, chi1_inj, chi2_inj)
params_inj = np.array([m1_inj, m2_inj, chi1_inj, chi2_inj])
num_params = len(params_inj)


# choose domain of parameters
m1_min = m1_inj - 5.
m1_max = m1_inj + 5.
m2_min = m2_inj - 5.
m2_max = m2_inj + 5.
chi1_min = -0.997
chi1_max = 0.997
chi2_min = -0.997
chi2_max = 0.997
chirp_min = mchirp_from_mass1_mass2(m1_min, m2_min)
chirp_max = mchirp_from_mass1_mass2(m1_max, m2_max)
ratio_min = 0.
ratio_max = 1.
spin_plus_min = -0.997
spin_plus_max = 0.997
spin_minus_min = -0.997
spin_minus_max = 0.997


# random parameters to initialize sliders
m1_random = np.random.uniform(m1_min, m1_max)
m2_random = np.random.uniform(m2_min, m2_max)
chi1_random = np.random.uniform(chi1_min, chi1_max)
chi2_random = np.random.uniform(chi2_min, chi2_max)
chirp_random = mchirp_from_mass1_mass2(m1_random, m2_random)
ratio_random = m2_random / m1_random
spin_plus_random = chi_eff(m1_random, m2_random, chi1_random, chi2_random)
spin_minus_random = chi_a(m1_random, m2_random, chi1_random, chi2_random)
params_random = np.array([m1_random, m2_random, chi1_random, chi2_random])


# define other physical parameters
# component masses
m1_SI = m1_inj * Msun
m2_SI = m2_inj * Msun
# total mass
M_SI = m1_SI + m2_SI
M_sec = M_SI * G / c**3
# chirp mass
chirp_SI = (m1_SI * m2_SI)**(3/5) / (m1_SI + m2_SI)**(1/5)
chirp_sec = chirp_SI * G / c**3
# reference frequence
f0 = 0.01 / M_sec
# luminosity distance (in Mega-parsec)
DL = 100.
DL_SI = DL * (1.e6) * pc_SI 
DL_sec = DL_SI / c
# reference amplitude
A0 = 2 * chirp_sec**(5/3) * (np.pi * f0)**(2/3) / DL_sec


# set window size for plotting and generating waveforms
window_min = -0.2  # plot beginning 0.2 sec before merger
window_max = 0.05  # plot ending 0.05 sec after merger

# define frequency bins
f_min = 16.
f_max = 1024.
Nf = 2**14 + 1
freqs = np.linspace(0., f_max, Nf)
index_min = np.where(freqs > f_min)[0][0]
freqs_cut = freqs[index_min:]

#interpolated data 
interp_func= interp1d(frequencies, FFT_waveform)

intrp_waveform= interp_func(freqs_cut)


# GW150914 GPS time to get data
GPS_event_time = 1126259462.4


# checkbox rectangle for plotting
checkbox_rect = [0.05, 0.5, 0.2, 0.2]


# slider rectangles for plotting
slider1_rect = [0.15, 0.2, 0.65, 0.03]
slider2_rect = [0.15, 0.15, 0.65, 0.03]
slider3_rect = [0.15, 0.1, 0.65, 0.03]
slider4_rect = [0.15, 0.05, 0.65, 0.03]


# button rectangle to go to injected (or MAP) parameters
button_rect = [0.05, 0.4, 0.2, 0.04]


# parameter labels
m1_label = r'$m_1\,\,(M_\odot)$'
m2_label = r'$m_2\,\,(M_\odot)$'
chi1_label = r'$\chi_1$'
chi2_label = r'$\chi_2$'
chirp_label = r'$\mathcal{M}\,\,(M_\odot)$'
ratio_label = r'$q$'
spin_plus_label = r'$\chi_+$'
spin_minus_label = r'$\chi_-$'


