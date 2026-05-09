#include <cassert>
#include "../../src/ExposureController/ExposureController.h"
#include "../../src/DoseManager/DoseManager.h"

int main() {
    expose_sequence::ExposureController ec;
    assert(ec.GetStatus() == expose_sequence::ExposeStatus::IDLE);
    ec.StartExposure("shot_001");
    assert(ec.GetStatus() == expose_sequence::ExposeStatus::EXPOSING);
    ec.StopExposure();
    assert(ec.GetStatus() == expose_sequence::ExposeStatus::DONE);

    expose_sequence::DoseManager dm;
    dm.SetTargetDose(25.0);
    assert(dm.GetTargetDose() == 25.0);
    dm.CalibrateDose();
    assert(dm.GetActualDose() == 25.0);
    dm.ApplyCorrection(0.5);
    assert(dm.GetActualDose() == 25.5);

    return 0;
}
