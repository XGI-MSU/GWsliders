'''This file stores constants used throughout the slider program.'''

import pickle
import numpy as np
from pycbc.conversions import mchirp_from_mass1_mass2, chi_eff, chi_a


# constants needed for unit conversion
c = 3.0e8  # speed of light
G = 6.67430e-11  # Newton's gravitational constant
Msun = 1.989e30  # mass of the Sun in kg
pc_SI = 3.08567758128e+16  # number of meters in one parsec

# # Simulated Data parameters
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

# reference parameters for real data
# FORMAT -- 'GW name': [GPS event time, [mass1, mass2, spin plus, spin minus]]
signal_ref_params = {'GW150914': [1126259462.4, [38.8, 33.4, -0.01, 0.0]],
                     'GW200129': [1264316116.4, [40.7, 34.2, 0.11, 0.0]],
                     'GW190521': [1242459857.4, [52.5, 40.4, 0.10, 0.0]],
                     'GW200224': [1266618172.4, [52.8, 43.2, 0.10, 0.0]],
                     'GW200311': [1267963151.3, [42.1, 34.1, 0.-0.02, 0.0]],
                     'GW191109': [1257296855.2, [81.25, 58.75, -0.29, 0.0]],
                     'GW190828': [1251009263.7, [44.0, 35.6, 0.15, 0.0]],
                     'GW190519': [1242315362.3, [94.4, 59.2, 0.33, 0.0]],}

# choose domain of parameters
m1_min = m1_inj - 5.
m1_max = m1_inj + 5.
m2_min = m2_inj - 5.
m2_max = m2_inj + 5.
chi1_min = -0.997
chi1_max = 0.997
chi2_min = -0.997
chi2_max = 0.997
ratio_min = 0.
ratio_max = 0.99
spin_plus_min = -0.997
spin_plus_max = 0.997
spin_minus_min = -0.997
spin_minus_max = 0.997
amp_min= 0
amp_max= 150


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
# luminosity distance (in Mega-parsec)
DL = 100.
DL_SI = DL * (1.e6) * pc_SI


# set window size for plotting and generating waveforms
window_min = -0.32
window_max= 0.32

# define frequency bins
f_min = 16.
f_max= 2048.




#load dictionary to pull time domain info 
with open('data/GW150914_data_dict.pkl', 'rb') as f:
    GW150914_data = pickle.load(f)
#choose intial detector 
det= 'H1'
#get time domain info from dictionary
dt = GW150914_data['dt']
fs = GW150914_data['fs']
strain = GW150914_data[det]['strain']
N = len(strain)
Nf = int(N/2 + 1)

#get frequency info
freqs_full = np.linspace(0., f_max, Nf)
freqs_indexes = np.where(freqs_full > f_min)
freqs= np.load('freqs.npy')
#frequencies for full waveform
freqs_for_waveform = freqs[np.where(freqs>f_min)]
#frequencies for creating template
freqs_padded = freqs_full.copy()
freqs_padded[freqs_padded < f_min] = 0.0
df = np.abs(freqs[1] - freqs[0])

# checkbox rectangle for plotting
checkbox_rect = [0.05, 0.75, 0.2, 0.2]
menu_rect= [0.05, 0.5, 0.2, 0.2]



# slider rectangles for plotting
# [left, bottom, width, height]
slider1_rect = [0.15, 0.21, 0.65, 0.03]
slider2_rect = [0.15, 0.17, 0.65, 0.03]
slider3_rect = [0.15, 0.13, 0.65, 0.03]
slider4_rect = [0.15, 0.09, 0.65, 0.03]
slider5_rect= [0.15, 0.05, 0.65, 0.03]
slider6_rect= [0.15, 0.01, 0.65, 0.03]

# slider1_rect = [0.15, 0.27, 0.40, 0.01]
# slider2_rect = [0.15, 0.14, 0.40, 0.01]
# slider3_rect = [0.15, 0.11, 0.40, 0.01]
# slider4_rect = [0.15, 0.8, 0.40, 0.01]
# slider5_rect= [0.15, 0.05, 0.40, 0.01]
# slider6_rect= [0.15, 0.02, 0.40, 0.01]

# button rectangle to go to injected (or MAP) parameters
button_rect = [0.05, 0.7, 0.2, 0.04]
button_signal= [0.05, 0.65, 0.2, 0.04]
button1_signal= [0.05, 0.6, 0.2, 0.04]
button2_signal= [0.05, 0.55, 0.2, 0.04]
button3_signal= [0.05, 0.5, 0.2, 0.04]
button4_signal= [0.05, 0.45, 0.2, 0.04]
button5_signal= [0.05, 0.4, 0.2, 0.04]
button6_signal= [0.05, 0.35, 0.2, 0.04]
button7_signal= [0.05, 0.30, 0.2, 0.04]


# parameter labels
m1_label = r'$m_1\,\,(M_\odot)$'
m2_label = r'$m_2\,\,(M_\odot)$'
chi1_label = r'$\chi_1$'
chi2_label = r'$\chi_2$'
chirp_label = r'$\mathcal{M}\,\,(M_\odot)$'
ratio_label = r'$q$'
spin_plus_label = r'$\chi_+$'
spin_minus_label = r'$\chi_-$'
amp_label= r'amplitude'
phase_label= r'phase'
det_label= r'Livingston Detector'

# m1_label.set_fontsize(4)
# m2_label.set_fontsize(4)
# chi1_label.set_fontsize(4)
# chi2_label.set_fontsize(4)
# amp_label.set_fontsize(4)
# phase_label.set_fontsize(4)
# det_label.set_fontsize(4)