#pragma once
namespace illumination {

class LensSystem {
public:
    void   SetFocus(double position_mm);
    double GetFocus() const;
    void   SetAperture(double na);
    double GetAperture() const;

private:
    double focus_mm_  = 0.0;
    double aperture_  = 0.0;
};

} // namespace illumination
