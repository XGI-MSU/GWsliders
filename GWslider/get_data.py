'''This script fetches open LIGO data and stores as .dat in data folder.'''



import numpy as np
import matplotlib.pyplot as plt
from gwpy.timeseries import TimeSeries
import requests, os
from constants import *
from gwosc.locate import get_urls


# download data and write to .hdf5 file
url = get_urls('H1', GPS_event_time, GPS_event_time)[-1]
print('Downloading: ' , url)
fn = f'data/{os.path.basename(url)}'
with open(fn,'wb') as strainfile:                 
    straindata = requests.get(url)
    strainfile.write(straindata.content)

# read strain data
strain = TimeSeries.read(fn,format='hdf5.gwosc')
center = int(GPS_event_time)
strain = strain.crop(center-16, center+16)
fig1 = strain.plot()
plt.show()

# plot ASD
fig2 = strain.asd(fftlength=8).plot()
plt.xlim(10,2000)
plt.ylim(1e-24, 1e-19)
plt.show()

# whiten and bandpass data
white_data = strain.whiten()
bp_data = white_data.bandpass(30, 400)
fig3 = bp_data.plot()
plt.xlim(GPS_event_time-0.2, GPS_event_time+0.1)
plt.show()

# splice sample times and strains around GW event
data_times = np.array(bp_data.times)
data_strains = np.array(bp_data)
merger_time = data_times[np.argmax(data_strains)]
lower_time_bound = merger_time + window_min
upper_time_bound = merger_time + window_max
keep_indices = np.where(np.bitwise_and(data_times > lower_time_bound, data_times < upper_time_bound))
data_times_cut = data_times[keep_indices] - merger_time
data_strains_cut = data_strains[keep_indices]

# save data
np.savetxt('data/GW150914.dat', np.array([data_times_cut, data_strains_cut]).T)

