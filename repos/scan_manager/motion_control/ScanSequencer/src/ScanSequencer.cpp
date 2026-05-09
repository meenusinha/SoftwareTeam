#include "ScanSequencer.h"
namespace scan_manager {

void       ScanSequencer::StartScan(const std::string&) { status_ = ScanStatus::SCANNING; progress_ = 0.0; }
void       ScanSequencer::StopScan()                    { status_ = ScanStatus::DONE; }
ScanStatus ScanSequencer::GetStatus() const             { return status_; }
double     ScanSequencer::GetProgress() const           { return progress_; }

} // namespace scan_manager
