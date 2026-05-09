namespace cpp illumination

service LensSystem {
    void   SetFocus(1: double position_mm),
    double GetFocus(),
    void   SetAperture(1: double na),
    double GetAperture()
}
