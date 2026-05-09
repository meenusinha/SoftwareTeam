# Illumination Subsystem — Interface Contracts

## LightSource Interface

Defined in `interfaces/LightSource.thrift`.

| Method | Description | When called |
|--------|-------------|-------------|
| `SetPower(watts)` | Set laser output power setpoint | Recipe setup; also called by DoseManager during scan for real-time correction |
| `GetPower()` | Read back current power setpoint | Monitoring, dose feedback loop |
| `Enable()` | Arm the laser — pulses will fire on gate signal | Before scan start, after stage is ready |
| `Disable()` | Inhibit pulses immediately | End of scan, safety interlock, between fields |
| `IsEnabled()` | Query armed state | Pre-scan checklist, interlock verification |

**Key contract**: `SetPower` followed by `GetPower` must reflect the new value within 5 ms. If the hardware cannot track the setpoint, the driver raises an alarm.

**Dose correction protocol**: DoseManager calls `SetPower(new_watts)` where `new_watts = current_power * (target_dose / actual_dose)`. This is a closed-loop correction applied every N pulses.

## LensSystem Interface

Defined in `interfaces/LensSystem.thrift`.

| Method | Description | When called |
|--------|-------------|-------------|
| `SetFocus(position_mm)` | Move condenser lens to axial position | Layer recipe load |
| `GetFocus()` | Read current focus position | Verification after set |
| `SetAperture(na)` | Set illumination sigma (NA ratio) | Layer recipe load |
| `GetAperture()` | Read current sigma | Verification, monitoring |

**Key contract**: Both `SetFocus` and `SetAperture` are synchronous — they block until servo settles. The caller (process control) does not need to poll.
