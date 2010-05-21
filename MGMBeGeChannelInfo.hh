
#ifndef _MGMBeGeChannelInfo_hh_
#define _MGMBeGeChannelInfo_hh_ 1
#include "TObject.h"
#include <vector>

class MGMBeGeOneChannelInfo
{
  
  public:
    MGMBeGeOneChannelInfo() : baseline(0), maximum(0), minimum(0), averagepeak(0) {}
    MGMBeGeOneChannelInfo(Double_t aBase, Double_t aMax, Double_t aMin, Double_t aPeak) : 
      baseline(aBase), maximum(aMax), minimum(aMin), averagepeak(aPeak) {}
    Double_t baseline; 
    Double_t maximum; 
    Double_t minimum; 
    Double_t averagepeak; 
  ClassDef(MGMBeGeOneChannelInfo,2)
};

class MGMBeGeChannelInfo: public TObject
{
  public:
    std::vector<MGMBeGeOneChannelInfo> channels;
    MGMBeGeOneChannelInfo& GetChannel(size_t i) { return channels[i]; } 
    size_t GetNumChannels() { return channels.size(); }
    
  ClassDef(MGMBeGeChannelInfo,1)
};

#endif /* _MGMBeGeChannelInfo_hh_ */
