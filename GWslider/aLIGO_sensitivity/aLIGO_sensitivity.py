import numpy as np



# import sensitivity curve from aLIGO
#aLIGO = np.loadtxt('aLIGO_sensitivity/aLIGODesign.txt')
aLIGO = np.loadtxt('aLIGO_sensitivity/BWpsd.dat')
#aLIGO= np.loadtxt('aLIGO_sensitvity/BWpsd.dat')
aLIGO_fs = aLIGO[:,0]
aLIGO_strain = np.sqrt(aLIGO[:,1])



# function that gets spectral strain sensitivity at arbitrary frequency
# (not only frequencies in the frequency list)
# uses linear interpolation

def sqrtS(freq):

    # get indices of frequencies adjacent to desired frequency
    counter = 0
    while aLIGO_fs[counter] < freq:
        counter += 1
    
    lower_index = counter - 1
    upper_index = counter

    # linear interpolation between points
    slope = (aLIGO_strain[upper_index] - aLIGO_strain[lower_index]) / (aLIGO_fs[upper_index] - aLIGO_fs[lower_index])
    sensitivity = aLIGO_strain[lower_index] + slope * (freq - aLIGO_fs[lower_index])
    
    return sensitivity

