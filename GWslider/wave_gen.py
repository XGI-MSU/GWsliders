'''Script to generate waveforms.'''


import numpy as np
from constants import *
from waveform_structure import *


# get injected waveform in frequency-domain
waveform_inj_FD = waveform.get_FD_waveform(params_inj, 0.)

# get injected waveform in time-domain
times, waveform_inj = waveform.get_TD_waveform(params_inj, 0.)
num_times = len(times)
dt= times[1]-times[0]

# load real LIGO data
data_times, data_strains = np.loadtxt('data/GW150914.dat').T

FFT_waveform= np.fft.fft(data_strains)


#interpolated strains
intrp_func_strains= interp1d(data_times, data_strains)
intrp_strain= intrp_func_strains(times)


# function to get amplitude and phase which minimizes chi-squared
def get_amp_phase_min(waveform_FD_0_cut, waveform_FD_pi4_cut, waveform_to_fit_FD):
    # compute necessary inner producs
    beta_c = waveform.inner(waveform_to_fit_FD, waveform_FD_0_cut)
    beta_s = waveform.inner(waveform_to_fit_FD, waveform_FD_pi4_cut)
    gamma_cc = waveform.inner(waveform_FD_0_cut, waveform_FD_0_cut)
    
    # get amplitude that minimizes chi-squared
    amp_min = np.sqrt(beta_c**2 + beta_s**2) / gamma_cc
    
    # get coalescence phase that minimizes chi-squared
    phic_min = -np.arctan2(beta_s, beta_c)
    
    return amp_min, phic_min


# function to get waveform in the time-domain given parameters with amplitude and phase to minimize chi-squared with data
def get_amp_phase_minimized_waveform(params, waveform_to_fit_FD, whiten=True):

    # get in-phase and quadrature-phase waveforms in frequency-domain
    waveform_FD_0 = waveform.get_full_FD_waveform(params, 0.)
    waveform_FD_pi4 = waveform.get_full_FD_waveform(params, np.pi/4.)
    waveform_FD_0_cut = waveform_FD_0[waveform.index_min:]
    waveform_FD_pi4_cut = waveform_FD_pi4[waveform.index_min:]

    amp_min, phase_min = get_amp_phase_min(waveform_FD_0_cut, waveform_FD_pi4_cut, waveform_to_fit_FD)
    FD_signal = waveform.get_full_FD_waveform(params, phase_min/2.)
    FD_signal_cut = FD_signal[waveform.index_min:]

    # compute SNR series over time shifts
    time_shifts = np.linspace(-0.05, 0.05, 50)
    SNR_series = np.array([waveform.inner(waveform_to_fit_FD, FD_signal_cut * np.exp(2*np.pi*1.j*waveform.freqs_cut*t)) 
                    for t in time_shifts])

    # get time shift which maximizes SNR
    time_shift_max = time_shifts[np.argmax(SNR_series)]

    TD_signal = waveform.iFFT_waveform(FD_signal * np.exp(2. * np.pi * 1.j * waveform.freqs * time_shift_max), 
                                       whiten=whiten)[1]
    TD_signal -= np.mean(TD_signal)

    return TD_signal

#chi-squared function
# function to compute the normalized chi-squared between two waveforms
def normalized_chi_sq(waveform1, waveform2):
    SNR1sq = integrate(waveform1**2, dx=dt)
    SNR2sq = integrate(waveform2**2, dx=dt)
    norm_chi_sq = integrate((waveform1 - waveform2)**2, dx=dt)
    return norm_chi_sq




