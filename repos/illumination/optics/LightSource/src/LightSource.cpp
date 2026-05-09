#include "LightSource.h"
namespace illumination {

void   LightSource::SetPower(double watts) { power_watts_ = watts; }
double LightSource::GetPower() const       { return power_watts_; }
void   LightSource::Enable()               { enabled_ = true; }
void   LightSource::Disable()              { enabled_ = false; }
bool   LightSource::IsEnabled() const      { return enabled_; }

} // namespace illumination
