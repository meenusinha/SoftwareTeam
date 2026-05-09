# Illumination Subsystem — Overview

## Role in the Lithography Scanner

The Illumination subsystem is responsible for producing, shaping, and conditioning the UV light beam used to expose photoresist on silicon wafers. In a deep-UV (DUV) or extreme-UV (EUV) scanner, the quality of the light delivered to the wafer plane directly determines the resolution and uniformity of the printed pattern.

## Key Responsibilities

- **Laser source control**: Turn the excimer or solid-state laser on/off and regulate its output power in watts. Stable power is critical for dose repeatability.
- **Beam conditioning**: The raw laser beam is shaped through illumination optics (fly-eye lens arrays, beam expanders, aperture blades) to achieve the required illumination mode (conventional, annular, dipole, quadrupole).
- **Numerical aperture setting**: The lens system adjusts the illumination-side NA to match the required depth of focus and resolution for a given process layer.
- **Dose coupling**: While the DoseManager in ExposeSequence owns the dose target, the actual delivered energy per unit area depends on laser power × exposure time. The Illumination subsystem must respond to power adjustment requests in real time during a scan.

## Interactions with Other Subsystems

- **ExposeSequence / DoseManager**: DoseManager requests power corrections (via `SetPower`) when the actual dose deviates from target. Illumination must apply the correction within one scan slit period.
- **ScanManager / ScanSequencer**: Scan speed and slit width determine the dose-per-pulse relationship. When scan speed changes, Illumination may need to adjust laser repetition rate or power to maintain target dose.

## Design Constraints

- Power setpoint changes must settle within 5 ms to avoid dose non-uniformity within a scan slit.
- Laser enable/disable must be interlock-safe: the system must not fire while stage is settling.
