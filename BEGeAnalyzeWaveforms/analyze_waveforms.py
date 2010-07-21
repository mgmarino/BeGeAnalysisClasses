#!/usr/local/bin/python
import ROOT
import array
from ctypes import c_ulonglong
import sys
import pywt
import math
import numpy
def get_threshold_list():
      return [ 0.0413365741474,
               0.0334049964465,
               0.0265735119519,
               0.020878122779,
               0.0177156746346,
               0.00835124911162 ]


def iswt(coefficients, wavelet):
    """
      Input parameters: 

        coefficients
          approx and detail coefficients, arranged in level value 
          exactly as output from swt:
          e.g. [(cA1, cD1), (cA2, cD2), ..., (cAn, cDn)]

        wavelet
          Either the name of a wavelet or a Wavelet object

    """
    output = coefficients[0][0].copy() # Avoid modification of input data

    #num_levels, equivalent to the decomposition level, n
    num_levels = len(coefficients)
    for j in range(num_levels,0,-1): 
        step_size = int(math.pow(2, j-1))
        last_index = step_size
        _, cD = coefficients[num_levels - j]
        for first in range(last_index): # 0 to last_index - 1

            # Getting the indices that we will transform 
            indices = numpy.arange(first, len(cD), step_size)

            # select the even indices
            even_indices = indices[0::2] 
            # select the odd indices
            odd_indices = indices[1::2] 

            # perform the inverse dwt on the selected indices,
            # making sure to use periodic boundary conditions
            x1 = pywt.idwt(output[even_indices], cD[even_indices], wavelet, 'per') 
            x2 = pywt.idwt(output[odd_indices], cD[odd_indices], wavelet, 'per') 

            # perform a circular shift right
            x2 = numpy.roll(x2, 1)

            # average and insert into the correct indices
            output[indices] = (x1 + x2)/2.  

    return output

def apply_threshold(output, scaler = 1., input=None):
    """ 
        output is a list of vectors (cA and cD, approximation
        and detail coefficients) exactly as you would expect
        from swt decomposition.  
           e.g. [(cA1, cD1), (cA2, cD2), ..., (cAn, cDn)]
 
        If input is none, this function will calculate the
        tresholds automatically for each waveform.
        Otherwise it will use the tresholds passed in, assuming
        that the length of the input is the same as the length
        of the output list.
        input looks like:
           [threshold1, threshold2, ..., thresholdn]
 
        scaler is a tuning parameter that will be multiplied on
        all thresholds.  Default = 1
 
    """
    
    for j in range(len(output)): 
        cA, cD = output[j]
        if input is None:
            dev = numpy.median(numpy.abs(cD - numpy.median(cD)))/0.6745
            thresh = math.sqrt(2*math.log(len(cD)))*dev*scaler
        else: thresh = scaler*input[j]
        cD = pywt.thresholding.hard(cD, thresh)
        output[j] = (cA, cD)


def process_waveforms_in_file(input_file_name, output_file_name):

    # Initialize, setting the mode to bath to avoid any X connections
    ROOT.gROOT.SetBatch()

    # Grab the input file and tree, setting the
    # branch address for the EventBranch
    input_file = ROOT.TFile(input_file_name)
    the_tree = input_file.Get("soudan_wf_analysis")
    event = ROOT.MGTEvent()
    the_tree.SetBranchAddress("EventBranch", event)


    # Baseline Transformer
    baseline = ROOT.MGWFBaselineRemover()
    init_baseline_time = 280e3

    # Extremum Transformer
    extremum = ROOT.MGWFExtremumFinder()

    # Pulse finder Transformer
    pulse_finder = ROOT.MGWFPulseFinder()

    # Bandpass transformer, this is used to smooth
    # the shaped waveforms before energy estimation 
    first_bandpass = ROOT.MGWFBandpassFilter()
    shaped_bandpass = 0.0001 # 100 kHz low-bandpass
    first_bandpass.SetUpperBandpass(shaped_bandpass)

    # Setting parameters of the risetime
    rise = ROOT.MGWFRisetimeCalculation()
    rise.SetInitialThresholdPercentage(0.1) #10 %
    rise.SetFinalThresholdPercentage(0.9) #90%
    rise.SetInitialScanToPercentage(0.8) #80%

    # Static window, for amplitude estimation
    static_window = ROOT.MGWFStaticWindow() 

    # Smoothing derivative
    der = ROOT.MGWFSavitzkyGolaySmoother(6, 1, 2)

    # Temporary waveforms
    newwf = ROOT.MGTWaveform()
    tempder = ROOT.MGTWaveform()
    bandpass_wf = ROOT.MGTWaveform()

    # Parameters for the wavelet transformation
    wl_trans = pywt.Wavelet('haar')
    level = 6
    length_of_pulse = 30e3

    # Setup objects for writing out, TFile, TTree, etc.
    output_file = ROOT.TFile(output_file_name, "recreate")
    output_tree = ROOT.TTree("energy_output_tree", "Soudan Energy Tree")

    # Setup MGMAnalysisClasses to encapsulate the output data
    muon_veto = ROOT.MGMMuonVeto()
    channel_info = ROOT.MGMBeGeChannelInfo()
    risetime = ROOT.MGMRisetimeInfo()
    pulser_on = array.array('L', [0]) 
    # This is a hack to get a 64-bit unsigned integer
    long_array = c_ulonglong*1
    time = long_array()

    output_tree.Branch("muon_veto", muon_veto)
    output_tree.Branch("channel_info", channel_info)
    output_tree.Branch("risetime_info", risetime)
    output_tree.Branch("pulser_on", pulser_on, "pulser_on/i")
    output_tree.Branch("time", time, "time/l")


    percentageDone = 0
    numEntries = the_tree.GetEntries()

    # The events has waveforms in the following configuration:
    # 0: channel 0, shaped 6 mus, low-energy
    # 1: channel 1, shaped 10 mus, low-energy
    # 2: channel 2, shaped 10 mus, high-energy
    # 3: muon veto 
    # 4: pre-amp trace, low-energy 
    # 5: pre-amp trace, high-energy 
    for entry in range(numEntries):
        # Outputting progress, every 10 percent
        if int(entry*100/numEntries) > 10*percentageDone: 
          percentageDone += 1
          print "Done (%): ", percentageDone*10

        # Clear the analysis objects
        muon_veto.regions.clear()
        channel_info.channels.clear()
        risetime.channels.clear()

        # Grab the event from the input tree
        the_tree.GetEntry(entry)
        
        # Set pulser flags (combining two flags from initial tree)
        pulser_on[0] = ((the_tree.pulser_chunk_two != 0) or (the_tree.pulser_chunk_one != 0))

        # Set time
        time[0] = the_tree.timestamp

        # Muon VETO
        # Use the pulser finder to determine the regions of the 
        # waveform where the muon veto has fired.
        pulse_finder.SetThreshold(-0.2) # -0.2 volts, it fires negative
        pulse_finder.Transform(event.GetWaveform(3))
        for an_event in pulse_finder.GetThePulseRegions():
            muon_veto.regions.push_back(an_event)

        # All channels
        for chan_num in (0,1,2,4,5):
            baseline.SetBaselineTime(init_baseline_time) # 250 mus
            wf = event.GetWaveform(chan_num)
            extremum.SetFindMaximum(True)
            extremum.Transform(wf)

            # Find parameter of waveform, max, min, etc.
            max_value = extremum.GetTheExtremumValue()
            avg_value = max_value
            extremum.SetFindMaximum(False)
            extremum.Transform(wf)
            min_value = extremum.GetTheExtremumValue()
            baseline_factor = 1
            
            # only process the shaped waveform with a bandpass filter
            if chan_num in (0,1,2):
                first_bandpass.Transform(wf)
                extremum.SetFindMaximum(True)
                extremum.Transform(wf)
                avg_value = extremum.GetTheExtremumValue()/wf.GetLength()
                baseline_factor = wf.GetLength()
            baseline_value = baseline.GetBaseline(wf)/baseline_factor 

            # Save values in channel_info object
            channel_info.channels.push_back(
              ROOT.MGMBeGeOneChannelInfo(baseline_value, max_value, min_value, avg_value))
        
        # Preamp trace channels
        for chan_num in (4,5):
            wf = event.GetWaveform(chan_num)

            # First do a bandpass filter to grab important values
            # Grab the max and the min
            first_bandpass.Transform(wf, bandpass_wf)
            extremum.SetFindMaximum(True)
            extremum.Transform(bandpass_wf)
            rise_max = extremum.GetTheExtremumValue() 
            rise_max_pos = extremum.GetTheExtremumPoint() 

            extremum.SetFindMaximum(False)
            extremum.Transform(bandpass_wf)
            rise_min = extremum.GetTheExtremumValue() 
            rise_min_pos = extremum.GetTheExtremumPoint() 

            # Perform the wavelet smoothing
            # Get the raw data from the waveform to pass to pywt
            vec = wf.GetVectorData()
            # make the waveform a dyadic (2^N) (FixME, we are assuming
            # the waveform is 8000 entries long)
            # reduce to length 4096
            vec.erase(vec.begin(), vec.begin()+3904)

            # Stationary Wavelet Transform
            output = pywt.swt(vec, wl_trans, level=level)
            # Thresholding
            apply_threshold(output, 0.8, get_threshold_list())
            # Inverse transform
            cA = iswt(output, wl_trans)

            # Reloading into waveform, but getting a small region around
            # the known waveform rise to reduce later calculation
            newwf.SetSamplingFrequency(wf.GetSamplingFrequency())
            start = int(100e3*wf.GetSamplingFrequency())
            end = start + int(length_of_pulse*wf.GetSamplingFrequency())
            # loading waveform from start to end
            newwf.SetData(cA[start:end], end-start)

            # Now find the risetime
            # Take the derivative to zero in on the pulse
            der.Transform(newwf, tempder)
            # Find minimum (FixME, assuming negative going pulse)
            extremum.SetFindMaximum(False)
            extremum.Transform(tempder)

            # Find the FWHM
            pulse_finder.SetThreshold(0.5*extremum.GetTheExtremumValue())
            pulse_finder.Transform(tempder)

            point = extremum.GetTheExtremumPoint()

            # Find the correct region in case there are other ones that have been
            # found.  I.e. this is the one with the extremum point within.
            regions = pulse_finder.GetThePulseRegions()
            test_point = 0
            for region in range(regions.size()):
                if regions[region].IsInRegion(point):
                    test_point = region
                    break
    
            
            if regions.size() == 0:
                # Means no regions were found (this should never happen, but might 
                # for a wf close to noise)
                # Estimate using the derivative peak then
                # Making a 4 mus window around this point.
                start = point*newwf.GetSamplingPeriod()-2e3
                end = point*newwf.GetSamplingPeriod()+2e3 
            else:
                # We found the correct point, set the start and stop time
                # at the FWHM
                start = regions[test_point].beginning*newwf.GetSamplingPeriod()
                end = regions[test_point].end*newwf.GetSamplingPeriod()
            # Gives the HWHM (half-width at half-max)
            diff = (end - start)/2.0 

            # This extends the window to one more full width on each side  
            start -= 2*diff
            end += 2*diff

            # First estimate and subtract the baseline
            # This check is to make sure we are on the
            # the waveform still
            if start < 0: start = 0
            if start < 1e3: 
                static_window.SetDelayTime(start)
            else:
                static_window.SetDelayTime(start-1e3)

            # Estimate, subtract baseline using 1 mus integration
            static_window.SetFirstRampTime(0)
            static_window.SetSecondRampTime(1e3)
            static_window.Transform(newwf)
            newwf -= static_window.GetPeakHeight()
    
            # now grab the peak height
            if end > length_of_pulse - 1e3: end = length_of_pulse - 1e3
            static_window.SetDelayTime(end)
            static_window.SetFirstRampTime(0)
            static_window.SetSecondRampTime(1e3)
            static_window.Transform(newwf)
   
            # We have the peak height, we feed into the risetime calculator
            max_value_to_find = static_window.GetPeakHeight()
            rise.SetPulsePeakHeight(max_value_to_find)
     
            # Scan from the start position defined by the beginning
            # of the baseline estimation 
            rise.SetScanFrom(int(start*newwf.GetSamplingFrequency()))
            rise.Transform(newwf)
            rt = rise.GetRiseTime()
            start_rt = rise.GetInitialThresholdCrossing()
            stop_rt = rise.GetFinalThresholdCrossing()

            # Save in the MGMAnalysis Object
            risetime.channels.push_back(
              ROOT.MGMRisetimeOneChannelInfo(start_rt, stop_rt, rt, 
                                             rise_max, rise_min,
                                             int(rise_max_pos), int(rise_min_pos)))

        
        output_tree.Fill()
    output_file.cd()
    output_tree.Write()

def main(input_file, output_file):
    # For usage when directly imported
    process_waveforms_in_file(input_file, output_file) 

Usage = \
"""
Usage:
analyze_waveforms.py [input_root_file] [output_root_file]
"""

if __name__ == '__main__':
   
    if len(sys.argv) != 3:
        print Usage;
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
