#include <cassert>
#include "../../src/LightSource/LightSource.h"
#include "../../src/LensSystem/LensSystem.h"

int main() {
    illumination::LightSource ls;
    ls.SetPower(10.5);
    assert(ls.GetPower() == 10.5);
    assert(!ls.IsEnabled());
    ls.Enable();
    assert(ls.IsEnabled());
    ls.Disable();
    assert(!ls.IsEnabled());

    illumination::LensSystem lens;
    lens.SetFocus(1.23);
    assert(lens.GetFocus() == 1.23);
    lens.SetAperture(0.85);
    assert(lens.GetAperture() == 0.85);

    return 0;
}
