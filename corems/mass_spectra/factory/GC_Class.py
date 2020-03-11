__author__ = "Yuri E. Corilo"
__date__ = "Feb 13, 2020"


from collections.abc import Mapping
from pathlib import Path

from numpy import array

from corems.mass_spectra.calc.GC_Calc import GC_Calculations
from corems.chromatogram_peak.factory.ChromaPeakClasses import GCPeak
from corems import timeit

class GCMSBase(Mapping, GC_Calculations):
    """
    classdocs
    """

    def __init__(self, file_location, analyzer='Unknown', instrument_label='Unknown', sample_name=None):
        
        """
        Constructor
        file_location: text or pathlib.Path() 
            Path object from pathlib containing the file location
        """
        
        file_location = Path(file_location)
        
        if not file_location.exists():
        
            raise FileExistsError("File does not exist: " + file_location)
        
        self.file_location = file_location
        
        if sample_name: self.sample_name = sample_name
        
        #uses filename
        else: self.sample_name = file_location.stem
        
        self.analyzer = analyzer
        self.instrument_label = instrument_label
        
        self._retention_time_list = []
        self._scans_number_list = []
        self._tic_list = []

        #all scans
        self._ms = {}
        
        #after peak detection
        self._processed_tic = []
        self.gcpeaks = {}
        
        """
        key is scan number; value is MassSpectrum Class
        """
        
    def __len__(self):
        
        return len(self.gcpeaks)
        
    def __getitem__(self, scan_number):
        
        return self.gcpeaks.get(scan_number)

    def __iter__(self):

         return iter(self.gcpeaks.values())

    def process_chromatogram(self,):

        tic = self.tic + self.baseline_detector(self.tic)

        self._processed_tic = self.smooth_tic(tic)

        for index, tic in enumerate(self._processed_tic):

            self._ms[index]._processed_tic = tic

        peaks_index = self.peaks_detector(self._processed_tic)
        
        for i in peaks_index: 
            
            apex_index = i[1]

            self.gcpeaks[self.scans_number[apex_index]] = GCPeak( self._ms[apex_index], i )

    def add_mass_spectrum(self, mass_spec):
        
        self._ms[mass_spec.scan_number] = mass_spec

    def set_tic_list_from_data(self):

        self.tic = [self._ms.get(i).tic for i in self.scans_number]
        
        # self.set_tic_list([self._ms.get(i).get_sumed_signal_to_noise() for i in self.get_scans_number()])

    def set_retention_time_from_data(self):

        retention_time_list = []

        for key_ms in sorted(self._ms.keys()):

            retention_time_list.append(self._ms.get(key_ms).rt)

        self.retention_time = retention_time_list 

        # self.set_retention_time_list(sorted(self._ms.keys()))

    def set_scans_number_from_data(self):
        
        self.scans_number = sorted(self._ms.keys())

    @property
    def scans_number(self):

        return self._scans_number_list

    @property
    def retention_time(self):

        return self._retention_time_list
    
    @property
    def processed_tic(self):

        return self._processed_tic

    @property
    def tic(self):

        return self._tic_list

    @retention_time.setter
    def retention_time(self, l):
        # self._retention_time_list = linspace(0, 80, num=len(self._scans_number_list))
        self._retention_time_list = l

    @scans_number.setter
    def scans_number(self, l):

        self._scans_number_list = l

    @tic.setter
    def tic(self, l):

        self._tic_list = array(l)    

    def plot_gc_peaks(self, ax=None, color="red"): #pragma: no cover
        
        import matplotlib.pyplot as plt

        if ax is None:
            ax = plt.gca()
        
        max_rts = [gc_peak.mass_spectrum.rt for gc_peak in self]
        max_tics = [gc_peak.mass_spectrum.tic for gc_peak in self]

        min_rts = [self._ms[gc_peak.start_index].rt for gc_peak in self] + [self._ms[gc_peak.final_index].rt for gc_peak in self]
        min_tics = [self._ms[gc_peak.start_index].tic for gc_peak in self] + [self._ms[gc_peak.final_index].tic for gc_peak in self]
        
        ax.plot(max_rts, max_tics, color=color, linewidth=0, marker='v')

        ax.plot(min_rts, min_tics, color='yellow', linewidth=0, marker='v')
        
        ax.set(xlabel='Retention Time (s)', ylabel='Total Ion Chromatogram')
        
        return ax

    def plot_chromatogram(self, ax=None, color="blue"): #pragma: no cover
        
        import matplotlib.pyplot as plt

        if ax is None:
            ax = plt.gca()
        
        ax.plot(self.retention_time, self.tic, color=color)
        ax.set(xlabel='Retention Time (s)', ylabel='Total Ion Chromatogram')
        
        return ax

    def plot_smoothed_chromatogram(self, ax=None, color="green"): #pragma: no cover
        
        import matplotlib.pyplot as plt

        if ax is None:

            ax = plt.gca()
        
        ax.plot(self.retention_time, self.smooth_tic(self.tic), color=color)

        ax.set(xlabel='Retention Time (s)', ylabel='Total Ion Chromatogram')
        
        return ax

    def plot_detected_baseline(self, ax=None, color="blue"): #pragma: no cover
        
        import matplotlib.pyplot as plt

        if ax is None:

            ax = plt.gca()
        
        ax.plot(self.retention_time, self.baseline_detector(self.tic), color=color)

        ax.set(xlabel='Retention Time (s)', ylabel='Total Ion Chromatogram')
        
        return ax

    def plot_baseline_subtraction(self, ax=None, color="black"): #pragma: no cover
        
        import matplotlib.pyplot as plt

        if ax is None:

            ax = plt.gca()
        
        x = self.tic + self.baseline_detector(self.tic)

        ax.plot(self.retention_time, x, color=color)

        ax.set(xlabel='Retention Time (s)', ylabel='Total Ion Chromatogram')
        
        return ax

    def plot_processed_chromatogram(self, ax=None, color="black"):
        
        import matplotlib.pyplot as plt

        if ax is None:

            ax = plt.gca()
        
        ax.plot(self.retention_time, self.processed_tic, color=color)

        ax.set(xlabel='Retention Time (s)', ylabel='Total Ion Chromatogram')
        
        return ax