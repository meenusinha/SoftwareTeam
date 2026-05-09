#pragma once
namespace expose_sequence {

class DoseManager {
public:
    void   SetTargetDose(double dose_mj_cm2);
    double GetTargetDose() const;
    double GetActualDose() const;
    void   CalibrateDose();
    void   ApplyCorrection(double delta_dose);

private:
    double target_dose_  = 0.0;
    double actual_dose_  = 0.0;
};

} // namespace expose_sequence
