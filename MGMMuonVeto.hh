
#ifndef _MGMMuonVeto_hh_
#define _MGMMuonVeto_hh_ 1
#include "TObject.h"
#include <vector>

class MGWaveformRegion {
  public:
    size_t beginning;
    size_t end;
    MGWaveformRegion() : beginning(0), end(0) {}
    MGWaveformRegion(size_t aBeg, size_t anEnd) : beginning(aBeg), end(anEnd) {}
    bool IsInRegion(size_t test) { return (test >= beginning && test <= end); }
};


class MGMMuonVeto: public TObject
{

  public:
    std::vector<MGWaveformRegion> regions;
    bool IsInVetoRegion(size_t);
    bool RangeIsInVetoRegion(size_t beginning, size_t end);
  public:
    size_t GetNumberOfRegions() { return regions.size(); }
    
  ClassDef(MGMMuonVeto,2)
};

#endif /* _MGMMuonVeto_hh_ */
