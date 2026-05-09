# ScanManager Subsystem — Components

## StageController

**Responsibility**: Manages the physical motion of the wafer stage in X, Y, and Z axes.

**Key state**:
- `current_`: current XYZ position in millimetres
- `ready_`: whether the stage has settled at its commanded position

**Design notes**:
- `MoveTo(pos)` is non-blocking in the stub; in production it would block until the stage servo reports settled.
- `Home()` returns the stage to (0, 0, 0) — used at system startup and after a scan abort.
- `GetPosition()` is the critical real-time readback: called every pulse period by DoseManager during active scanning.
- Z-axis control is used for auto-focus levelling before scan start, not during scan.

**Cross-subsystem dependency**:
- DoseManager (ExposeSequence) polls `GetPosition()` at high rate to compute position error and derive dose correction.
- StageController position data is the ground truth for all dose-to-position mapping.

## ScanSequencer

**Responsibility**: Orchestrates the multi-step sequence for exposing one wafer die field.

**Key state**:
- `status_`: IDLE → SCANNING → DONE (or ERROR on fault)
- `progress_`: fraction of current scan completed (0.0–1.0)

**Design notes**:
- `StartScan(scan_id)` triggers the full sequence: move to scan start position, open exposure gate, scan, close gate, log completion.
- The `scan_id` is used for traceability — links this scan event to the wafer job record.
- `StopScan()` is both a normal end-of-scan call and an emergency abort — the implementation must handle both safely.
- `GetProgress()` is polled by higher-level job control to update the UI and estimate remaining time.

**Cross-subsystem dependency**:
- ScanSequencer sends the exposure gate open signal to ExposureController (ExposeSequence) at the start of the active scan window.
- ScanSequencer must wait for LightSource (Illumination) to report `IsEnabled() == true` before opening the gate.
