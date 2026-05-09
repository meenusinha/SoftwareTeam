#include "DoseManager.h"
namespace expose_sequence {

void   DoseManager::SetTargetDose(double dose_mj_cm2) { target_dose_ = dose_mj_cm2; }
double DoseManager::GetTargetDose() const              { return target_dose_; }
double DoseManager::GetActualDose() const              { return actual_dose_; }
void   DoseManager::CalibrateDose()                    { actual_dose_ = target_dose_; }
void   DoseManager::ApplyCorrection(double delta)      { actual_dose_ += delta; }

} // namespace expose_sequence
