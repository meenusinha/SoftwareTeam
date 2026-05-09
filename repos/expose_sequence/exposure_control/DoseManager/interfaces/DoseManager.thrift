namespace cpp expose_sequence

service DoseManager {
    void   SetTargetDose(1: double dose_mj_cm2),
    double GetTargetDose(),
    double GetActualDose(),
    void   CalibrateDose(),
    void   ApplyCorrection(1: double delta_dose)
}
