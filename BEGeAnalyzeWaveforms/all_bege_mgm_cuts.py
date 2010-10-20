import ROOT
import SoudanDB.databases.bege_jc
from SoudanDB.management.soudan_database import SoudanServer
import cPickle as pickle

class MGMBegeAnalysisSelector():
    def __init__(self, percentage=90):
        ROOT.gROOT.cd()
        self.microphonics_list = ROOT.TEventList("microphonics_list", "microphonics_list")
        self.risetime_list = ROOT.TEventList("risetime_list", "risetime_list")
        self.LN_cut_list = ROOT.TEventList("LN_cut_list", "LN_cut_list")
        self.odd_pulse_cut_list = ROOT.TEventList("odd_pulse_cut_list", "odd_pulse_cut_list")
        self.LN_cut_on_list = ROOT.TEventList("LN_cut_on_list", "LN_cut_on_list")
        self.combination_list = ROOT.TEventList("combination_list", "combination_list")
       
        # The risetime cut is a dump from the results of the rise-time fit. 
        server = SoudanServer()
       
        # Grab the trigger efficiency 
        trigger_doc = server.get_trigger_efficiency_doc()
        self.erfc_function = trigger_doc.trigger_efficiency['standard'].efficiency_function
       
        # Grab the microphonics cuts
        microdoc = server.get_microphonics_cut_doc( )
        temp = microdoc.all_micro_cuts[99]
        self.lower_cut, self.upper_cut, self.microphonics_efficiency = \
              temp.lower_cut, temp.upper_cut, temp.efficiency_function
       
        # Grab the risetime cuts
        risedoc = server.get_rise_time_cut_doc() 
        temp = risedoc.all_rise_cuts[percentage] 
        self.risetime_cut, self.upper_risetime_cut, self.risetime_efficiency = \
              temp.low_energy_function, temp.high_energy_function, temp.efficiency_function
       
        self.cuts_list = [self.get_risetime_cut_list,
                          self.get_microphonics_cuts_list,
                          self.get_LN_fill_cut_list,
                          self.get_odd_pulse_cut_list]
        self.eff_list =  [self.risetime_efficiency,
                          self.microphonics_efficiency,
                          self.erfc_function]
        self.odd_pulse_cut = server.get_pulse_cut_doc().pulse_cut

    @classmethod
    def get_available_rise_cuts(cls):
        server = SoudanServer()
        risedoc = server.get_rise_time_cut_doc() 
        return risedoc.all_rise_cuts.keys()

    def get_trigger_efficiency(self): return self.erfc_function
    def get_risetime_efficiency(self): return self.risetime_efficiency
    def get_microphonics_efficiency(self): return self.microphonics_efficiency


    def get_risetime_cut_graph(self): return self.risetime_cut
    def get_upper_risetime_cut_graph(self): return self.upper_risetime_cut
    def get_upper_cut(self): return self.upper_cut
    def get_lower_cut(self): return self.lower_cut
    def get_odd_pulse_cut(self): return self.odd_pulse_cut

    def get_odd_pulse_cut_list(self, tree):
        self.odd_pulse_cut_list.Reset()
        for i in range(tree.GetEntries()):
            tree.GetEntry(i)
            achan = tree.risetime_info.GetChannel(1)
            nextchan = tree.channel_info.GetChannel(1)
            energy = nextchan.averagepeak - nextchan.baseline
            diff = achan.maximum - achan.minimum
            ratio = diff#/energy
            if energy > 0.01 or ratio < 140 + (60./0.01)*energy:#self.odd_pulse_cut.Eval(energy): 
                self.odd_pulse_cut_list.Enter(i)
        return self.odd_pulse_cut_list

    def get_risetime_cut_list(self, tree):
        self.risetime_list.Reset()
        for i in range(tree.GetEntries()):
            tree.GetEntry(i)
            energy = tree.channel_info.GetChannel(1).averagepeak -\
                     tree.channel_info.GetChannel(1).baseline
            eval = None
            risetime = 0
            if energy >= 0.05: # use the upper
                energy = tree.channel_info.GetChannel(2).averagepeak -\
                         tree.channel_info.GetChannel(2).baseline
                risetime = tree.risetime_info.GetChannel(1).risetime*1e-3
                eval = self.upper_risetime_cut
            elif energy <= 0.05 and energy >= 0.045:
                # Try both
                energytwo = tree.channel_info.GetChannel(2).averagepeak -\
                         tree.channel_info.GetChannel(2).baseline
                risetimetwo = tree.risetime_info.GetChannel(1).risetime*1e-3
                risetime = tree.risetime_info.GetChannel(0).risetime*1e-3

                if (risetimetwo <= self.upper_risetime_cut.Eval(energytwo) and
                    risetime <= self.risetime_cut.Eval(energy)):
                    # Take the better cut
                    self.risetime_list.Enter(i) 
                    continue
            else:
                risetime = tree.risetime_info.GetChannel(0).risetime*1e-3
                eval = self.risetime_cut
            if ((eval and risetime <= eval.Eval(energy))): 
                self.risetime_list.Enter(i) 
        self.risetime_list.Sort()
        return self.risetime_list

    def get_LN_fill_on_cut_list(self, tree):
        self.LN_cut_on_list.Reset()
        for i in range(tree.GetEntries()):
            tree.GetEntry(i)
            pulser_on = tree.pulser_on
            if pulser_on == 1: self.LN_cut_on_list.Enter(i)
        return self.LN_cut_on_list


    def get_LN_fill_cut_list(self, tree):
        self.LN_cut_list.Reset()
        for i in range(tree.GetEntries()):
            tree.GetEntry(i)
            pulser_on = tree.pulser_on
            if pulser_on != 1: self.LN_cut_list.Enter(i)
        return self.LN_cut_list

    def get_all_cuts_list(self, tree):
        els = [func(tree) for func in self.cuts_list]
        self.combination_list = ROOT.TEventList(els[0])
        [self.combination_list.Intersect(els[i]) for i in range(1, len(els))]
        return self.combination_list

    def get_all_cuts_efficiency(self):
        # Now the efficiency
        ROOT.gROOT.cd()
        temp_str = self.eff_list[0].GetName()
        for i in range(1, len(self.eff_list)):
            temp_str += "*%s" % self.eff_list[i].GetName()
        efficiency_total = ROOT.TF1("efficiency_total", temp_str)
        return efficiency_total
        

    def get_microphonics_cuts_list(self, tree):
        self.microphonics_list.Reset()
        for i in range(tree.GetEntries()):
            tree.GetEntry(i)
            if tree.channel_info.GetChannel(1).baseline > -0.008: continue
            energy = tree.channel_info.GetChannel(1).averagepeak - \
                     tree.channel_info.GetChannel(1).baseline
            ratio = (tree.channel_info.GetChannel(0).averagepeak - \
                     tree.channel_info.GetChannel(0).baseline)/energy
            minimum = tree.channel_info.GetChannel(1).minimum
            chan = tree.channel_info.GetChannel(4)
            pulser_on = tree.pulser_on
            if minimum <= -0.02: continue
            if pulser_on != 1:
                #if (chan.maximum - chan.minimum) > (0.036 + (0.104 - 0.038)/0.05*energy) and energy < 0.05: continue 
                if (energy > 0.05): self.microphonics_list.Enter(i) 
                elif ((ratio <= self.upper_cut.Eval(energy) and 
                     ratio >= self.lower_cut.Eval(energy))): self.microphonics_list.Enter(i) 
            #else: print ratio, energy, minimum
        self.microphonics_list.Sort()
        return self.microphonics_list

