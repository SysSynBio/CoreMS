

__author__ = "Yuri E. Corilo"
__date__ = "Jun 12, 2019"

from corems.encapsulation.settings.processingSetting import MassSpecPeakSetting
from corems.encapsulation.settings.processingSetting import MolecularSearchSettings

from corems.ms_peak.calc.MSPeakCalc import MSPeakCalculation

class _MSPeak(MSPeakCalculation):
    '''
    classdocs
    '''
    def __init__(self, ion_charge, mz_exp, abundance, resolving_power, signal_to_noise, massspec_index, index, exp_freq=None):

        # needed to create the object
        self.ion_charge = int(ion_charge)
        self._mz_exp = float(mz_exp)
        self.mass = float(mz_exp) / float(ion_charge)
        self.abundance = float(abundance)
        self.resolving_power = float(resolving_power)
        self.signal_to_noise = float(signal_to_noise)
        self.mass_spec_index = int(massspec_index)
        self.index = int(index)
        'updated after calibration'
        self.mz_cal = None
        'updated individual calculation'
        self.baseline_noise = None
        
        if exp_freq:
            self.freq_exp = float(exp_freq)

        kendrick_dict_base = MassSpecPeakSetting.kendrick_base
        self._kdm, self._kendrick_mass, self._nominal_km = self._calc_kdm(
            kendrick_dict_base)
 
        'updated after molecular formula ID'

        self.molecular_formulas = []
        self._confidence_score = None

        self.isotopologue_indexes = []
        self.found_isotopologues = {}

    def __len__(self):
        
        return len(self.molecular_formulas)
        
    def __setitem__(self, position, molecular_formula_obj):
        
        self.molecular_formulas[position] = molecular_formula_obj

    def __getitem__(self, position):
        
        return self.molecular_formulas[position]

    def change_kendrick_base(self, kendrick_dict_base):
        '''kendrick_dict_base = {"C": 1, "H": 2}'''
        self._kdm, self._kendrick_mass, self._nominal_km = self._calc_kdm(
            kendrick_dict_base)

    def add_molecular_formula(self, molecular_formula_obj):
       
        self.molecular_formulas.append(molecular_formula_obj)
    
    def clear_molecular_formulas(self):
        
        self.molecular_formulas= []
    
    @property
    def mz_exp(self):
        if self.mz_cal:
            return self.mz_cal
        else:
            return self._mz_exp
    
    @mz_exp.setter
    def mz_exp(self, mz_exp):
        self._mz_exp = mz_exp

    @property
    def nominal_mz_exp(self): return int(self.mz_exp)

    @property
    def kmd(self): return self._kdm

    @property
    def kendrick_mass(self): return self._kendrick_mass

    @property
    def knm(self): return self._nominal_km
    
    @property
    def is_assigned(self):

        return bool(self.molecular_formulas)
    
    @property
    def number_possible_assignments(self,):
        
        return len(self.molecular_formulas)
    
    def molecular_formula_lowest_error(self):
       
       return min(self.molecular_formulas, key=lambda m: abs(m._calc_assignment_mass_error(self.mz_exp)))

    def molecular_formula_earth_filter(self, lowest_error=True):
        
        candidates = list(filter(lambda mf: mf.get("O") > 0 and mf.get("N") <=3 and mf.get("P") <= 2 and (3 * mf.get("P")) <= mf.get("O"), self.molecular_formulas))

        if lowest_error:
            return min(candidates, key=lambda m: abs(m._calc_assignment_mass_error(self.mz_exp)))
        else:
            return candidates
    
    def molecular_formula_water_filter(self, lowest_error=True):
       
        candidates = list(filter(lambda mf: mf.get("O") > 0 and mf.get("N") <=3 and mf.get("S") <=2 and  mf.get("P") <= 2, self.molecular_formulas))

        if lowest_error:
            return min(candidates, key=lambda m: abs(m._calc_assignment_mass_error(self.mz_exp)))
        else:
            return candidates
    
    def molecular_formula_air_filter(self, lowest_error=True):
       
        candidates = list(filter(lambda mf: mf.get("O") > 0 and mf.get("N") <=2 and mf.get("S") <=1 and  mf.get("P") == 0 and 3* (mf.get("S") + mf.get("N")) <= mf.get("O"), self.molecular_formulas))
        
        if lowest_error:
            return min(candidates, key=lambda m: abs(m._calc_assignment_mass_error(self.mz_exp)))
        else:
            return candidates

    @property
    def best_molecular_formula_candidate(self):
        
        if MolecularSearchSettings.score_method == "N_S_P_lowest_error":
            return self.cia_score_N_S_P_error()
        
        elif MolecularSearchSettings.score_method == "S_P_lowest_error":
            return self.cia_score_S_P_error()

        elif MolecularSearchSettings.score_method == "lowest_error":
            return self.molecular_formula_lowest_error()    
        
        elif MolecularSearchSettings.score_method == "air_filter_error":
            return self.molecular_formula_air_filter()    

        elif MolecularSearchSettings.score_method == "water_filter_error":
            return self.molecular_formula_water_filter()    

        elif MolecularSearchSettings.score_method == "earth_filter_error":
            return self.molecular_formula_earth_filter()   

        elif MolecularSearchSettings.score_method == "prop_score":
            #TODO
            raise NotImplementedError
        else:
            
            raise TypeError("Unknown score method selected: % s, \
                            Please check score_method at \
                            encapsulation.settings.molecular_id.MolecularIDSettings.MolecularSearchSettings", 
                            MolecularSearchSettings.score_method)    

    def cia_score_S_P_error(self):
        #case EFormulaScore.HAcap:

        lowest_S_P_mf = min(self.molecular_formulas, key=lambda mf: mf.get('S') + mf.get('P'))
        lowest_S_P_count = lowest_S_P_mf.get("S") + lowest_S_P_mf.get("P")
        
        list_same_s_p = list(filter(lambda mf: mf.get('S') + mf.get('P') == lowest_S_P_count, self.molecular_formulas))

        #check if list is not empty
        if list_same_s_p:
        
            return min(list_same_s_p, key=lambda m: abs(m._calc_assignment_mass_error(self.mz_exp)))
        
        else:
        
            return lowest_S_P_mf
    
    def cia_score_N_S_P_error(self):
        #case EFormulaScore.HAcap:
        if self.molecular_formulas:

            lowest_N_S_P_mf = min(self.molecular_formulas, key=lambda mf: mf.get('N') + mf.get('S') + mf.get('P'))
            lowest_N_S_P_count = lowest_N_S_P_mf.get("N") + lowest_N_S_P_mf.get("S") + lowest_N_S_P_mf.get("P")

            list_same_N_S_P = list(filter(lambda mf: mf.get('N') + mf.get('S') + mf.get('P') == lowest_N_S_P_count, self.molecular_formulas))

            if list_same_N_S_P:

                SP_filtered_list =  list(filter(lambda mf: (mf.get("S") <= 3 ) and  (mf.get("P")  <= 1 ), list_same_N_S_P))
                
                if SP_filtered_list:
                    
                    return min(SP_filtered_list, key=lambda m: abs(m._calc_assignment_mass_error(self.mz_exp))) 
                
                else:    
                    
                    return min(list_same_N_S_P, key=lambda m: abs(m._calc_assignment_mass_error(self.mz_exp)))            
            
            else:
                
                return lowest_N_S_P_mf 
        else:
            raise Exception("No molecular formula associated with the mass spectrum peak at m/z: %.6f" % self.mz_exp)

class ICRMassPeak(_MSPeak):

    def __init__(self, *args, exp_freq=None):

        super().__init__(*args,exp_freq=exp_freq)

    def resolving_power_calc(self, B, T):
        
        '''
        low pressure limits, 
        T: float 
            transient time
        B: float
            Magnetic Filed Strength (Tesla)    
        
        reference
        Marshall et al. (Mass Spectrom Rev. 1998 Jan-Feb;17(1):1-35.)
        DOI: 10.1002/(SICI)1098-2787(1998)17:1<1::AID-MAS1>3.0.CO;2-K
        '''
        return (1.274e7 * self.ion_charge * B * T)/ (self.mz_exp*self.ion_charge)

    def set_theoretical_resolving_power(self, B, T):

        self.resolving_power = self.resolving_power_calc(B, T) 
        
class TOFMassPeak(_MSPeak):

    def __init__(self, *args, exp_freq=None):

        super().__init__(*args,exp_freq=exp_freq)

    def set_theoretical_resolving_power(self):
        return 0

class OrbiMassPeak(_MSPeak):

    def __init__(self, *args, exp_freq=None):

        super().__init__(*args,exp_freq=exp_freq)

    def set_theoretical_resolving_power(self):
        return 0       
