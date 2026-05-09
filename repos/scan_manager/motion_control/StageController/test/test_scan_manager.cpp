#include <cassert>
#include "../../src/StageController/StageController.h"
#include "../../src/ScanSequencer/ScanSequencer.h"

int main() {
    scan_manager::StageController sc;
    assert(sc.IsReady());
    sc.MoveTo({10.0, 20.0, 0.5});
    auto pos = sc.GetPosition();
    assert(pos.x_mm == 10.0 && pos.y_mm == 20.0 && pos.z_mm == 0.5);
    sc.Home();
    auto home = sc.GetPosition();
    assert(home.x_mm == 0.0 && home.y_mm == 0.0 && home.z_mm == 0.0);

    scan_manager::ScanSequencer seq;
    assert(seq.GetStatus() == scan_manager::ScanStatus::IDLE);
    seq.StartScan("scan_001");
    assert(seq.GetStatus() == scan_manager::ScanStatus::SCANNING);
    seq.StopScan();
    assert(seq.GetStatus() == scan_manager::ScanStatus::DONE);

    return 0;
}
