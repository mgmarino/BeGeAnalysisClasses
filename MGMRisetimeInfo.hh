
#ifndef _MGMRisetimeInfo_hh_
#define _MGMRisetimeInfo_hh_ 1
#include "TObject.h"
#include <vector>

class MGMRisetimeOneChannelInfo
{
  
  public:
    MGMRisetimeOneChannelInfo() : start(0), stop(0), risetime(0), maximum(0), minimum(0) {}
    MGMRisetimeOneChannelInfo(Double_t aStart, Double_t aStop, 
                              Double_t aRT, Double_t amax,
                              Double_t amin) : 
      start(aStart), stop(aStop), risetime(aRT),
      maximum(amax), minimum(amin) {}
    Double_t start; 
    Double_t stop; 
    Double_t risetime; 
    Double_t maximum; 
    Double_t minimum; 
  ClassDef(MGMRisetimeOneChannelInfo,2)
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
