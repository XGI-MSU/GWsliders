from GW_class import *
from template import waveform
import constants as c
import numpy as np
from scipy.signal.windows import tukey
from template import *

# matched filter function
def matched_filter(template, data, GWsignal, det, simulated=False):

    # spacing between frequency bins
    df = c.freqs[1] - c.freqs[0]

    # get psd values from data dictionary
    psd_func = GWsignal['large_data_psds'][det]
    psd = psd_func(c.freqs)

    # calculate inner product for normalization
    integrand = np.real(template * template.conjugate()) / psd
    inner_product = 4 * np.sum(integrand) * df

    # normalized template
    p_normalization_factor = np.sqrt(inner_product)
    p = template / p_normalization_factor

    # for taking the fft of our template and data
    if simulated:
        data_FD = GWsignal[det]['data_FD']
    else:
        # window real data to reduce spectral leakage
        dwindow= tukey(data.size, alpha= 1./4)
        # fft real data
        data_FD = np.fft.rfft(data*dwindow) * c.dt
    
    # do Fourier transform
    integrand = (data_FD * p.conjugate() / psd)
    z = 4 * np.fft.ifft(integrand) * (len(integrand) * df)

    # get optimal time-shift, phase, and amplitude
    opt_ndx = np.argmax(np.abs(z))
    opt_time_shift = (np.arange(c.freqs.shape[0]) / (c.freqs.shape[0] * df))[opt_ndx]
    opt_amplitude = np.abs(z)[opt_ndx]
    opt_phase = np.angle(z[opt_ndx])
    SNRmax = np.abs(z)[opt_ndx]
    
    return SNRmax, opt_time_shift, opt_amplitude, opt_phase, p

# apply matched filter
def opt_template(template, GWsignal, det, simulated=False):
    
    # import GWsignal dictionary
    time = GWsignal['time']
    time_center = GWsignal['time_center']
    fs = GWsignal['fs']
    
    # amount of data we want to calculate matched filter SNR over- up to 32s
    data_time_window = time[len(time) - 1] - time[0] - (32 - 4)

    time_filter_window = np.where((time <= time_center + data_time_window * .5) & 
                                (time >= time_center - data_time_window * .5))
    time_filtered = time[time_filter_window]
    
    # get data 
    strain = GWsignal[det]['strain'][time_filter_window]
    if simulated:
        strain_whitenbp = GWsignal[det]['strain_whiten'][time_filter_window]
    else:
        strain_whitenbp = GWsignal[det]['strain_whitenbp'][time_filter_window]

    # do matched filter
    SNRmax, opt_time_shift, opt_amplitude, opt_phase, p = matched_filter(template, strain, GWsignal, det, simulated)

    # get psd values from data dictionary
    psd_func = GWsignal['large_data_psds'][det]
    psd = psd_func(c.freqs)

    # optimal template in frequency-domain
    # scale by optimal frequency
    opt_template_FD = opt_amplitude *p
    # optimal time shift
    opt_template_FD *= np.exp(-2. * np.pi * 1.j * c.freqs * opt_time_shift)
    # add phase shift
    opt_template_FD *= np.exp(1.j * opt_phase)

    # whiten template
    opt_template_FD_whitened = opt_template_FD / np.sqrt(psd)

    # get whitened template in TD 
    opt_template_TD = np.fft.irfft(opt_template_FD_whitened, waveform.times_full.shape[0]) *4*np.sqrt(fs)

    opt_TD_template_unwhitened= np.fft.irfft(opt_template_FD, waveform.times_full.shape[0]) *4*np.sqrt(fs)
    
    # ampltitude
    temp_max = np.max(np.abs(opt_TD_template_unwhitened))
    

    return  opt_template_TD, strain_whitenbp, time_filtered - time_center, SNRmax, temp_max, opt_phase



# wrapper function for matched filter
def wrapped_matched_filter(params, GW_signal, det):
    return opt_template(get_template(params, GW_signal.dictionary), GW_signal.dictionary, det, GW_signal.simulated)
