# ExposeSequence Subsystem — Overview

## Role in the Lithography Scanner

The ExposeSequence subsystem is the central coordinator of the wafer exposure process. It owns the dose budget for each wafer field, triggers and monitors individual exposures, and closes the dose control loop by correlating actual delivered energy with the target. It sits at the junction of the Illumination and ScanManager subsystems and orchestrates their interaction during active scanning.

## Key Responsibilities

- **Exposure triggering**: Initiate and terminate exposure events (open/close of the exposure gate) for each shot.
- **Dose control**: Maintain target dose (mJ/cm²) by monitoring actual cumulative energy and issuing corrections to the light source when deviations occur.
- **Shot coordination**: For multi-die reticles or multi-pass exposure strategies, sequence shots in the correct order with correct dose allocation per shot.
- **Fault management**: Detect dose errors above tolerance (e.g., overexpose, underexpose) and abort or flag the field accordingly.

## Interactions with Other Subsystems

- **ScanManager / StageController**: Real-time stage position is polled during scan to compute position-dependent dose corrections. If stage lags its nominal trajectory, dose per unit area increases (stage moving slower than programmed), requiring a power reduction.
- **ScanManager / ScanSequencer**: The scan gate open/close is coordinated — ScanSequencer tells ExposureController when to start/stop the active exposure window.
- **Illumination / LightSource**: DoseManager issues power correction commands (`SetPower`) to LightSource when the measured dose deviates from target.

## Design Constraints

- Dose correction latency from measurement to `SetPower` call must be < 2 ms to correct within one scan slit period.
- Dose accuracy target: ±0.5% of nominal dose across the exposed field.
- `ApplyCorrection` must be idempotent with respect to the calibration state — corrections are relative adjustments layered on top of the base calibration.
