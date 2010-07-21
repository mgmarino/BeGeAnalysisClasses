
#ifndef _MGMMuonVeto_hh_
#define _MGMMuonVeto_hh_ 1
#include "TObject.h"
#include "MGWaveform.hh"
#include <vector>

class MGMMuonVeto: public TObject
{
  public:
    std::vector<MGWaveformRegion> regions;
    bool IsInVetoRegion(size_t);
    bool RangeIsInVetoRegion(size_t beginning, size_t end);
  public:
    size_t GetNumberOfRegions() { return regions.size(); }
    
  ClassDef(MGMMuonVeto,1)
};

#endif /* _MGMMuonVeto_hh_ */
