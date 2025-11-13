import numpy as np
from pycbc.conversions import mchirp_from_mass1_mass2, spin1z_from_mass1_mass2_chi_eff_chi_a, spin2z_from_mass1_mass2_chi_eff_chi_a
from constants import *
import pickle
from signal_processing import *


class GWSignals:

    def __init__(self, ref_params, dictionary, t_min, t_max, simulated=False):
        # dictionary which contains data for event
        self.dictionary = dictionary
        self.t_min = t_min
        self.t_max = t_max
        # reference parameters
        self.mass1, self.mass2, self.chiPlus, self.chiMinus = ref_params
        self.chirp = mchirp_from_mass1_mass2(self.mass1, self.mass2)
        self.ratio = self.mass2 / self.mass1
        self.chi1 = spin1z_from_mass1_mass2_chi_eff_chi_a(self.mass1, self.mass2, self.chiPlus, self.chiMinus)
        self.chi2 = spin2z_from_mass1_mass2_chi_eff_chi_a(self.mass1, self.mass2, self.chiPlus, self.chiMinus)  
        self.comp_params = np.array([self.mass1, self.mass2, self.chi1, self.chi2])
        # simulated parameters
        self.simulated = simulated

        # minimum / maximum mass parameters for sliders
        self.min_mass1 = self.mass1 - 5.0
        self.min_mass2 = self.mass2 - 5.0
        self.max_mass1 = self.mass1 + 5.0
        self.max_mass2 = self.mass2 + 5.0
        self.min_chirp = mchirp_from_mass1_mass2(self.min_mass1, self.min_mass2)
        self.max_chirp = mchirp_from_mass1_mass2(self.max_mass1, self.max_mass2)
       



# load data 
with open('data/GW150914_data_dict.pkl', 'rb') as f:
    GW150914_data = pickle.load(f)

with open('data/GW190521_data_dict.pkl', 'rb') as f:
    GW190521_data = pickle.load(f)

with open('data/GW200129_data_dict.pkl', 'rb') as f:
    GW200129_data = pickle.load(f)

with open('data/GW200224_data_dict.pkl', 'rb') as f:
    GW200224_data = pickle.load(f)

with open('data/GW200311_data_dict.pkl', 'rb') as f:
    GW200311_data = pickle.load(f)

with open('data/GW191109_data_dict.pkl', 'rb') as f:
    GW191109_data= pickle.load(f)

with open('data/GW190828_data_dict.pkl', 'rb') as f:
    GW190828_data= pickle.load(f)

with open('data/GW190519_data_dict.pkl', 'rb') as f:
    GW190519_data= pickle.load(f)

with open('data/simulated_GW.pkl', 'rb') as f:
    simulated_data = pickle.load(f)

# class instantiation for real GW events
GW150914 = GWSignals(signal_ref_params['GW150914'][1], GW150914_data, 2.4, 2.5)
GW190521 = GWSignals(signal_ref_params['GW190521'][1], GW190521_data, 2.0, 2.1)
GW200129 = GWSignals(signal_ref_params['GW200129'][1], GW200129_data, 2.0, 2.1)
GW200224 = GWSignals(signal_ref_params['GW200224'][1], GW200224_data, 1.95, 2.1)
GW200311 = GWSignals(signal_ref_params['GW200311'][1], GW200311_data, 2.0, 2.2)
GW191109 = GWSignals(signal_ref_params['GW191109'][1], GW191109_data, 1.95, 2.1)
GW190828= GWSignals(signal_ref_params['GW190828'][1], GW190828_data, 2.0, 2.1)
GW190519= GWSignals(signal_ref_params['GW190519'][1], GW190519_data, 2.0, 2.2)


# class instantiation for simulated data
GW_simulated = GWSignals(signal_ref_params['GW150914'][1], simulated_data, 2.4, 2.5, simulated=True)



