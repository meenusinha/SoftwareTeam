# ExposeSequence Subsystem — Components

## ExposureController

**Responsibility**: Controls the timing and lifecycle of individual exposure events (shots).

**Key state**:
- `status_`: IDLE → EXPOSING → DONE (or ERROR)
- `elapsed_ms_`: time elapsed since exposure start

**Design notes**:
- `StartExposure(shot_id)` opens the exposure gate and starts timing. In production, this also signals ScanSequencer that the gate is open.
- `StopExposure()` closes the gate. DoseManager computes the final dose at this point and logs it against the `shot_id`.
- `GetElapsedTime()` is used by DoseManager to compute dose rate (dose = power × time / area).
- One `ExposureController` instance manages the gate; multiple shots in one field share the same instance with reset between shots.

**Cross-subsystem dependency**:
- Receives gate-open trigger coordination from ScanSequencer (ScanManager). In the current design, ScanSequencer calls `StartExposure` implicitly by releasing the stage motion interlock.
- After `StopExposure`, DoseManager records actual dose and compares to target for the next shot correction.

## DoseManager

**Responsibility**: Owns the dose budget, monitors actual delivered dose, and issues corrections.

**Key state**:
- `target_dose_`: the desired dose in mJ/cm² for the current layer
- `actual_dose_`: cumulative dose delivered so far in the current shot

**Design notes**:
- `CalibrateDose()` synchronises `actual_dose_` to `target_dose_` as a baseline — run once per layer recipe load.
- `ApplyCorrection(delta)` adds a signed delta to `actual_dose_` to account for real-time measurement. Positive delta = more dose than expected.
- The correction loop: poll `StageController.GetPosition()` → compute position error → compute dose delta → call `ApplyCorrection(delta)` → if cumulative error > threshold, call `LightSource.SetPower(corrected_power)`.
- `GetActualDose()` is the live feedback signal for the dose control loop and for end-of-field dose reporting.

**Cross-subsystem dependency**:
- `StageController.GetPosition()` (ScanManager): provides the position signal that drives the dose-position correction loop. Adaptive dose correction cannot function without low-latency position feedback from ScanManager.
- `LightSource.SetPower()` (Illumination): the actuator output of the dose control loop. DoseManager computes the required power and issues `SetPower` calls directly.
