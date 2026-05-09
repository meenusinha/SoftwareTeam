# ExposeSequence Subsystem — Interface Contracts

## ExposureController Interface

Defined in `interfaces/ExposureController.thrift`.

| Method | Description | When called |
|--------|-------------|-------------|
| `StartExposure(shot_id)` | Open exposure gate, begin shot timing | ScanSequencer gate-open coordination |
| `StopExposure()` | Close exposure gate | End of scan slit window |
| `GetStatus()` | Current state (IDLE/EXPOSING/DONE/ERROR) | Job control, DoseManager |
| `GetElapsedTime()` | ms since StartExposure | DoseManager dose-rate calculation |

**Key contract**: `StartExposure` and `StopExposure` are paired within a single scan field. Calling `StartExposure` twice without an intervening `StopExposure` is a protocol error and triggers a safety abort.

## DoseManager Interface

Defined in `interfaces/DoseManager.thrift`.

| Method | Description | When called |
|--------|-------------|-------------|
| `SetTargetDose(dose_mj_cm2)` | Set the dose target for this layer | Recipe load, before scan |
| `GetTargetDose()` | Read the current dose target | Monitoring, verification |
| `GetActualDose()` | Read cumulative dose delivered | Dose control loop, end-of-field reporting |
| `CalibrateDose()` | Reset actual dose to target as baseline | Layer recipe load |
| `ApplyCorrection(delta_dose)` | Add delta to actual dose accounting | Dose control loop, position-based correction |

**Adaptive dose correction using stage position — design intent**:

The new feature to implement is:
1. During scan, poll `StageController.GetPosition()` at each pulse period.
2. Compare actual stage X position to nominal trajectory position.
3. Compute position error `δx` (actual − nominal).
4. Derive dose delta: `δDose = target_dose × (δx / slit_width_mm)`.
5. Call `ApplyCorrection(δDose)` to update the actual dose account.
6. If cumulative `|actual_dose − target_dose| / target_dose > tolerance`, call `LightSource.SetPower(power × target_dose / actual_dose)`.

This requires DoseManager to hold a reference to both `StageController` (ScanManager) and `LightSource` (Illumination), establishing a real-time dependency on both other subsystems.
