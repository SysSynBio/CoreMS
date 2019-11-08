__author__ = "Yuri E. Corilo"
__date__ = "Oct 29, 2019"

from pandas import DataFrame
import h5py
from threading import Thread

from corems.encapsulation.constant import Labels
from corems.mass_spectrum.input.coremsHDF5 import ReadCoreMSHDF_MassSpectrum
from corems.mass_spectra.factory.LC_Class import LCMSBase

class ReadCoreMSHDF_MassSpectra(ReadCoreMSHDF_MassSpectrum, Thread):
    
    def __init__(self, file_location):
        
        Thread.__init__(self)
        
        ReadCoreMSHDF_MassSpectrum.__init__(self, file_location)
        
        self.lcms = LCMSBase(self.file_location)

        self.list_scans =  sorted([int(i) for i in list(self.h5pydata.keys())])

    def import_mass_spectra(self):
        
        list_rt, list_tic = list(), list()
        
        for scan_number in self.list_scans:
            
            mass_spec = self.get_mass_spectrum(scan_number)

            list_rt.append(mass_spec.rt)

            list_tic.append(mass_spec.tic)
            
            self.lcms.add_mass_spectrum_for_scan(mass_spec)

        self.lcms.set_retention_time_list(list_rt)
        self.lcms.set_tic_list(list_tic)
        self.lcms.set_scans_number_list(self.list_scans)
    
    def run(self):
        '''creates the lcms obj'''

        self.import_mass_spectra()
            
    def get_lcms_obj(self):
        
        if self.lcms:
            return self.lcms
        else:
            raise Exception("returning a empty lcms class")
    