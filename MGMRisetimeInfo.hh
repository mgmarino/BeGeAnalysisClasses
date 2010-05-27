
#ifndef _MGMRisetimeInfo_hh_
#define _MGMRisetimeInfo_hh_ 1
#include "TObject.h"
#include <vector>

class MGMRisetimeOneChannelInfo
{
  
  public:
    MGMRisetimeOneChannelInfo() : start(0), stop(0), 
                                  risetime(0), 
                                  maximum(0), minimum(0),
                                  max_point(0), min_point(0) {}
    MGMRisetimeOneChannelInfo(Double_t aStart, Double_t aStop, 
                              Double_t aRT, 
                              Double_t amax, Double_t amin, 
                              UInt_t max_pt, UInt_t min_pt) : 
      start(aStart), stop(aStop), 
      risetime(aRT),
      maximum(amax), minimum(amin), 
      max_point(max_pt), min_point(min_pt) {}

  public:
    Double_t start; 
    Double_t stop; 
    Double_t risetime; 
    Double_t maximum; 
    Double_t minimum; 
    UInt_t max_point; 
    UInt_t min_point; 

  ClassDef(MGMRisetimeOneChannelInfo,3)
};

class MGMRisetimeInfo: public TObject
{
  public:
    std::vector<MGMRisetimeOneChannelInfo> channels;
    MGMRisetimeOneChannelInfo& GetChannel(size_t i) { return channels[i]; } 
    size_t GetNumChannels() { return channels.size(); }
    
  ClassDef(MGMRisetimeInfo,1)
};

#endif /* _MGMRisetimeInfo_hh_ */
