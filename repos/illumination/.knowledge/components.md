# Illumination Subsystem — Components

## LightSource

**Responsibility**: Controls the excimer laser (or equivalent UV source) power and on/off state.

**Key state**:
- `power_watts_`: current commanded power level
- `enabled_`: whether the laser is currently armed and firing

**Design notes**:
- Power is set in watts; internally converted to laser driver current via a calibration curve.
- `Enable()` arms the laser interlock; actual pulses are triggered by the ScanSequencer's exposure gate signal.
- `Disable()` immediately inhibits pulses — used at end-of-scan and in safety interlocks.
- Power corrections from DoseManager arrive as absolute setpoints (not deltas) so the control loop in the hardware driver handles ramping.

**Cross-subsystem dependency**:
- DoseManager (ExposeSequence) calls `SetPower()` to apply real-time dose corrections.
- ScanSequencer (ScanManager) drives the exposure gate that gates individual pulses. LightSource state must be ENABLED before ScanSequencer can open the gate.

## LensSystem

**Responsibility**: Controls the illumination-side optics — focus position (for telecentricity tuning) and numerical aperture (sigma setting).

**Key state**:
- `focus_mm_`: current axial position of the condenser lens group
- `aperture_`: current sigma value (ratio of illumination NA to projection NA)

**Design notes**:
- Focus position is adjusted per-layer during recipe setup, not during active scanning.
- Aperture (sigma) determines the coherence of illumination; changes require a reticle alignment verification.
- Both parameters are read-back after set to verify servo settling before scan starts.

**Cross-subsystem dependency**:
- No real-time dependency during scanning. Set once per layer recipe by the process control system.
- Indirectly affects dose uniformity: incorrect focus degrades edge acuity and can cause apparent dose variation at feature edges.
