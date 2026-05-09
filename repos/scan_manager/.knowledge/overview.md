# ScanManager Subsystem — Overview

## Role in the Lithography Scanner

The ScanManager subsystem controls the precision motion of the wafer stage and reticle stage during scanning exposure. In a step-and-scan system, both stages move synchronously in opposite directions while the illumination slit sweeps across the reticle and wafer. Precise position control and real-time position feedback are the core responsibilities of this subsystem.

## Key Responsibilities

- **Stage motion control**: Command the wafer stage (X, Y, Z) to target positions with nanometer-level accuracy.
- **Scan sequencing**: Orchestrate the sequence of stage moves for each die field: step to start position, accelerate, scan at constant velocity, decelerate, step to next field.
- **Real-time position feedback**: Provide instantaneous X, Y, Z position to other subsystems (especially ExposeSequence) so they can correlate position with dose delivery.
- **Synchronisation**: Coordinate the exposure gate signal timing with the stage velocity profile so each laser pulse lands at the correct wafer position.

## Interactions with Other Subsystems

- **ExposeSequence / ExposureController**: ScanSequencer sends the exposure gate open/close signals to ExposureController to bracket the active scan window.
- **ExposeSequence / DoseManager**: DoseManager polls `StageController.GetPosition()` in real time to detect position errors that would require a dose correction. If the stage is behind schedule, the dose per unit area increases; a correction is sent to LightSource.
- **Illumination / LightSource**: Not a direct caller, but scan velocity changes (e.g., deceleration) change the dose-per-pulse footprint, which requires Illumination to adjust power.

## Design Constraints

- Position readback latency must be < 1 ms to support real-time dose correction at the ExposeSequence layer.
- Stage moves are deterministic: the position at any time `t` during scan is predictable from the velocity profile, allowing feed-forward dose correction.
- Scan abort (StopScan) must halt the stage within one slit width to prevent overexposure.
