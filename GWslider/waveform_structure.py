'''Script defines waveform object and associated methods, e.g. iFFTs, inner products, etc.'''


import numpy as np
from scipy.integrate import trapezoid as integrate
from aLIGO_sensitivity.aLIGO_sensitivity import *
from IMRPhenomD.IMRPhenomD import AmpPhaseFDWaveform, IMRPhenomDGenerateh22FDAmpPhase
import IMRPhenomD.IMRPhenomD_const as imrc
from constants import *



# gravitational waveform class
class Waveform:
    
    def __init__(self, freqs):
        
        # frequency bins to generate frequency-domain waveform
        self.freqs = freqs
        
        # initialize and store frequency-like objects
        self.num_freqs = len(self.freqs)
        self.df = self.freqs[1] - self.freqs[0]
        self.freq_max = self.freqs[-1]
        self.sampling_freq = 2 * self.freq_max

        # cut frequencies below f_min for waveform generation
        self.index_min = np.where(self.freqs > f_min)[0][0]
        self.freqs_cut = self.freqs[self.index_min:]
        self.num_freqs_cut = len(self.freqs_cut)

        # integrate over smaller domain of frequencies
        self.freq_min_integrate = 50
        self.index_min_integrate = np.where(self.freqs_cut > self.freq_min_integrate)[0][0]
        self.freqs_cut_integrate = self.freqs_cut[self.index_min_integrate:]

        # hyperbolic tangent window for iFFT, centered near f_min
        self.tanh_window = np.tanh(self.freqs - np.array([self.freqs_cut[0]] * self.num_freqs))

        # initialize and store noise spectral density
        self.sqrtSs = np.array([sqrtS(f) for f in self.freqs_cut])
        self.Ss = self.sqrtSs**2  #PSD 
        self.sqrtSs_integrate = np.array([sqrtS(f) for f in self.freqs_cut_integrate])
        self.Ss = self.sqrtSs_integrate**2
    
    
    # reference frequency for waveform generation
    MfRef_in = 0.  # ref. freq. at peak amplitude in freq-domain
    
    # get (frequency-domain) h22 object for given parameters
    # h22 includes amplitude and phase as array
    def get_h22(self, params, phic):
                
        # mass in solar masses
        m1, m2, chi1, chi2 = params
        
        # masses in kg
        m1_SI =  m1*imrc.MSUN_SI
        m2_SI =  m2*imrc.MSUN_SI
        
        # distance in meters
        distance = DL_SI

        # initialize amplitudes and times
        amp_imr = np.zeros(self.num_freqs_cut)
        phase_imr = np.zeros(self.num_freqs_cut)
        time_imr = np.zeros(self.num_freqs_cut)
        timep_imr = np.zeros(self.num_freqs_cut)

        #the first evaluation of the amplitudes and phase will always be much slower, because it must compile everything
        h22 = AmpPhaseFDWaveform(self.num_freqs_cut,self.freqs_cut,amp_imr,phase_imr,time_imr,timep_imr,0.,0.)
        h22 = IMRPhenomDGenerateh22FDAmpPhase(h22,self.freqs_cut,phic,Waveform.MfRef_in,m1_SI,m2_SI,chi1,chi2,distance)

        return h22
    
    
    # get frequency-domain signal over frequencies starting near f_min
    def get_FD_waveform(self, params, phic):
        h22 = self.get_h22(params, phic)
        return h22.amp * np.exp(1.j * h22.phase) / A0
    

    # get frequency-domain signal over frequencies starting from f=0
    def get_full_FD_waveform(self, params, phic):
        # get frequency-domain waveform
        waveform_FD = np.zeros(self.num_freqs, dtype='complex')
        waveform_FD[self.index_min:] = self.get_FD_waveform(params, phic)
        # apply hyperbolic tangent window
        waveform_FD *= self.tanh_window
        return waveform_FD


    # define inner product between waveforms in frequency-domain
    # uses scipy's rhombus numerical integration
    def inner(self, a, b):
       #a=a[:1024]
        #b=b[:1024]
        #PSD= self.sqrtSs[:1024]
        integrand = ((np.real(a)*np.real(b) + np.imag(a)*np.imag(b)) / self.sqrtSs)
        inner_prod = integrate(integrand, dx=self.df)
        return inner_prod * 4.
    

    # make full spectrum signal in frequency-domain
    def full_spectrum(self, FD_signal):
        n = 2 * len(FD_signal)
        full_spectrum = np.zeros(n, dtype=complex)
        full_spectrum[:n//2] = FD_signal
        full_spectrum[n//2 + 1:] = np.conjugate(FD_signal[1:][::-1])
        return full_spectrum


    # inverse FFT waveform to go into time-domain
    def iFFT_waveform(self, waveform_FD, roll_amt=None, whiten=True):
        if whiten:
            waveform_FD[self.index_min:] /= self.sqrtSs
        n = 2 * len(waveform_FD)
        full_spectrum = np.zeros(n, dtype=complex)
        full_spectrum[:n//2] = waveform_FD
        full_spectrum[n//2 + 1:] = np.conjugate(waveform_FD[1:][::-1])
        # inverse Fourier transform
        waveform_TD = np.real(np.fft.ifft(full_spectrum)[::-1])
        if roll_amt is None:
            waveform_TD = np.roll(waveform_TD, round(5/6 * len(waveform_TD)))
        else:
            waveform_TD = np.roll(waveform_TD, roll_amt)
        # get time axis
        sampling_freq = 2 * self.freq_max
        times = np.arange(0, len(waveform_TD)/sampling_freq, 1/sampling_freq)
        # set merger to t = 0

        merger_time = times[np.where(waveform_TD == max(waveform_TD))]

        print("merger_time:", merger_time)
        times -= merger_time
        # splice to fit in window
        indx_keep = np.where(np.bitwise_and(times > window_min, times < window_max))
        times = times[indx_keep]
        waveform_TD = waveform_TD[indx_keep] * A0
        return [times, waveform_TD]
    

    # get signal in time-domain with inverse fast Fourier transform
    def get_TD_waveform(self, params, phic):
        waveform_FD = self.get_full_FD_waveform(params, phic)
        # waveform_FD[self.index_min:] /= self.sqrtSs
        return self.iFFT_waveform(waveform_FD)


# instantiate waveform class for frequency bins (defined in constants.py)
waveform = Waveform(freqs)

