#include "LensSystem.h"
namespace illumination {

void   LensSystem::SetFocus(double position_mm) { focus_mm_ = position_mm; }
double LensSystem::GetFocus() const              { return focus_mm_; }
void   LensSystem::SetAperture(double na)        { aperture_ = na; }
double LensSystem::GetAperture() const           { return aperture_; }

} // namespace illumination
