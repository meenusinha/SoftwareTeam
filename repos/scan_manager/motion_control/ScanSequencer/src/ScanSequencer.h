#pragma once
#include <string>
namespace scan_manager {

enum class ScanStatus { IDLE, SCANNING, DONE, ERROR };

class ScanSequencer {
public:
    void       StartScan(const std::string& scan_id);
    void       StopScan();
    ScanStatus GetStatus() const;
    double     GetProgress() const;

private:
    ScanStatus status_   = ScanStatus::IDLE;
    double     progress_ = 0.0;
};

} // namespace scan_manager
