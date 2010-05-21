#include "MGMMuonVeto.hh"

ClassImp(MGMMuonVeto)

bool MGMMuonVeto::IsInVetoRegion(size_t test_position) 
{
  for( size_t i=0;i<regions.size();i++) {
    if (test_position >= regions[i].beginning &&
        test_position <= regions[i].end) return true;
  } 
  return false;
}
    
bool MGMMuonVeto::RangeIsInVetoRegion(size_t beginning, size_t end)
{
/* There are four overlap cases: 
 *   1. test_region is completely inside a veto region. 
 *   2. test_region beginning is inside a veto region, end outside. 
 *   3. test_region end is inside a veto region, beginning outside.
 *   4. test_region beginning is before a veto region, end is after. */

  /* This takes care of the first 3 cases. */
  if (IsInVetoRegion(beginning)) return true;
  else if (IsInVetoRegion(end)) return true;

  /* This takes care of the last case. */
  for( size_t i=0;i<regions.size();i++) {
    if (beginning <= regions[i].beginning &&
        end >= regions[i].end) return true;
  } 
  return false;
}
