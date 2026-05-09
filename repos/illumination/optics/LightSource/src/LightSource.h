#pragma once
namespace illumination {

class LightSource {
public:
    void   SetPower(double watts);
    double GetPower() const;
    void   Enable();
    void   Disable();
    bool   IsEnabled() const;

private:
    double power_watts_ = 0.0;
    bool   enabled_     = false;
};

} // namespace illumination
