# ScanManager Subsystem — Interface Contracts

## StageController Interface

Defined in `interfaces/StageController.thrift`.

| Method | Description | When called |
|--------|-------------|-------------|
| `MoveTo(pos)` | Command stage to XYZ position | Step-to-field, pre-scan positioning |
| `GetPosition()` | Read current XYZ position | Real-time by DoseManager every pulse; by job control for monitoring |
| `Home()` | Return stage to origin (0,0,0) | System startup, post-abort recovery |
| `IsReady()` | True when stage has settled at commanded position | Pre-scan checklist, gate open guard |

**Key contract for dose correction**: `GetPosition()` must return a position that is accurate to within ±10 nm and have end-to-end latency ≤ 1 ms from physical encoder read to API return. DoseManager uses successive `GetPosition()` calls to compute velocity and detect any deviation from the nominal scan trajectory. A position error of δx at scan speed v causes a dose error of δDose = Dose × (δx / slit_width). This is the core data that drives `DoseManager.ApplyCorrection()`.

## ScanSequencer Interface

Defined in `interfaces/ScanSequencer.thrift`.

| Method | Description | When called |
|--------|-------------|-------------|
| `StartScan(scan_id)` | Begin the full scan sequence for one field | Job control, per-die |
| `StopScan()` | End the scan (normal or abort) | End of field, fault handler |
| `GetStatus()` | Query current state (IDLE/SCANNING/DONE/ERROR) | Job control polling, UI |
| `GetProgress()` | Fraction complete (0.0–1.0) | UI, estimated time remaining |

**Key contract**: After `StartScan()` returns, the subsystem is committed to completing the scan or raising an error. The caller must not issue another `StartScan()` until `GetStatus()` returns DONE or ERROR.
