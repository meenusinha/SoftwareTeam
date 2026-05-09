namespace cpp scan_manager

enum ScanStatus { IDLE = 0, SCANNING = 1, DONE = 2, ERROR = 3 }

service ScanSequencer {
    void       StartScan(1: string scan_id),
    void       StopScan(),
    ScanStatus GetStatus(),
    double     GetProgress()
}
