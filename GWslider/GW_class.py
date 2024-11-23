import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import trapezoid as integrate
from aLIGO_sensitivity.aLIGO_sensitivity import *
from constants import *
from wave_gen import times, waveform_inj, waveform_inj_FD


class GW_signal:

    def __init__(self, times, freqs, waveformTD, waveformFD):

        self.times= times
        self.freqs= freqs
        self.waveformTD= waveformTD
        self.waveformFD= waveformFD
        self.sqrtS = np.array([sqrtS(f) for f in self.freqs])
        self.df= self.freqs[1]-self.freqs[0]

    def plotTD(self):
        plt.plot(self.times, self.waveformTD)
        plt.show()
    
    def plotFD(self):
        plt.plot(self.freqs, self.waveformFD)
        plt.show()
    
    def PSD_LIGO(self):
         plt.loglog(self.freqs, self.sqrtS)
         plt.show()
    
    #innr product in the frequency domain
    def innerProduct(self,a):
        integrand = ((np.real(a)*np.real(self.waveformFD) + np.imag(a)*np.imag(self.waveformFD)))
        inner_prod = integrate(integrand, dx=self.df)
        return inner_prod * 4.
    



GW150914= GW_signal(data_times, freqs, data_strains, intrp_waveform)
simulatedGW= GW_signal(times, freqs_cut, waveform_inj, waveform_inj_FD ) 
'''GW150914.plotFD()
GW150914.plotTD()'''
simulatedGW.plotTD()
simulatedGW.plotFD()

