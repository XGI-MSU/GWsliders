'''Download LIGO data.'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import readligo as rl
from signal_processing import tukey, whiten, bandpass
from scipy.interpolate import interp1d
import h5py
import wget
import pickle


def get_full_psds(large_data_filename, time_center):
    """Obtains full 1024 second psds for all the events specified. Uses the Welch
    average technique, along with other less accurate techniques if
    specified. Can also plot the psd obtained.

    Args:
        eventnames (list): list of events to get psds for
        large_datafilenames (dict): dictionary whose keys are the eventnames
            and whose values are the filenames of the large amounts of strain
            data used, without the added 'H-<det>_'
        make_plots (bool, optional): if set to True, plot psd data
        plot_others (bool, optional): if set to True, also obtain psd data
            without averaging as well as with no window

    Returns:
        dict: A dictionary containing psds for each detector for each event
            specified in eventnames.
    """

    large_data_psds = {'H1': [], 'L1': []}

    # get filename
    fn_H1 = 'H-H1_' + large_data_filename
    fn_L1 = 'L-L1_' + large_data_filename

    # get sample rate from the H1 data file
    with h5py.File(fn_H1, 'r') as hdf_file:
        dt = hdf_file['strain/Strain'].attrs['Xspacing']
    fs = int(1.0/dt)

    # get strain data
    strain_H1, time_H1, chan_dict_H1 = rl.loaddata(fn_H1, 'H1')
    strain_L1, time_L1, chan_dict_L1 = rl.loaddata(fn_L1, 'L1')

    # both H1 and L1 will have the same time vector, so:
    time = time_H1

    indxt_around = np.where((time >= time_center - 512) & (
        time < time_center + 512))

    # number of sample for the fast fourier transform:
    NFFT = int( 4 * fs)           # Use 4 seconds of data for each fourier transform
    NOVL = int( 1 * NFFT / 2)     # The number of points of overlap between segments used in Welch averaging
    psd_window = tukey(NFFT, alpha=1./4)

    Pxx_H1, freqs = mlab.psd(strain_H1[indxt_around], Fs=fs, NFFT=NFFT,
                                window=psd_window, noverlap=NOVL)
    Pxx_L1, freqs= mlab.psd(strain_L1[indxt_around], Fs=fs, NFFT=NFFT,
                            window=psd_window, noverlap=NOVL)

    # We will use interpolations of the PSDs computed above for whitening:
    psd_H1 = interp1d(freqs, Pxx_H1)
    psd_L1 = interp1d(freqs, Pxx_L1)

    large_data_psds['H1'] = psd_H1
    large_data_psds['L1'] = psd_L1

    return large_data_psds, dt, fs


def get_strain_whitenbp_data(fn_H1, fn_L1, fband, large_data_filename, time_center):

    # get strain data
    strain_H1, time_H1, chan_dict_H1 = rl.loaddata(fn_H1, 'H1')
    strain_L1, time_L1, chan_dict_L1 = rl.loaddata(fn_L1, 'L1')

    # both H1 and L1 will have the same time vector, so:
    time = time_H1

    large_data_psds, dt, fs = get_full_psds(large_data_filename, time_center)

    # whiten, bandpass the data
    strain_H1_whiten = whiten(strain_H1, large_data_psds['H1'], dt)
    strain_L1_whiten = whiten(strain_L1, large_data_psds['L1'], dt)

    strain_H1_whitenbp = (strain_H1_whiten, fband, fs)
    strain_L1_whitenbp = bandpass(strain_L1_whiten, fband, fs)

    # return results as a dictionary for more intuitive access
    total_data = {'H1': {'strain': strain_H1, 'strain_whiten': strain_H1_whiten,
                         'strain_whitenbp': strain_H1_whitenbp},
                  'L1': {'strain': strain_L1, 'strain_whiten': strain_L1_whiten,
                         'strain_whitenbp': strain_L1_whitenbp},
                  'time': time, 'time_center': time_center, 'dt': dt, 'fs': fs,
                  'large_data_psds': large_data_psds}

    return total_data


#example for saving signal data


#  save total data for GW150914
# GW150914_data_dict = get_strain_whitenbp_data('H-H1_LOSC_4_V2-1126259446-32.hdf5',
#                                               'L-L1_LOSC_4_V2-1126259446-32.hdf5',
#                                               [35., 350.],
#                                               'LOSC_4_V2-1126257414-4096.hdf5',
#                                               1126259462)

# with open('data/GW150914_data_dict.pkl', 'wb') as f:
#     pickle.dump(GW150914_data_dict, f)




