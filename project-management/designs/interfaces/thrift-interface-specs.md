# Thrift Interface Specifications

## Illumination Repo

### LightSource.thrift
```thrift
namespace cpp illumination

service LightSource {
    void   SetPower(1: double watts),
    double GetPower(),
    void   Enable(),
    void   Disable(),
    bool   IsEnabled()
}
```

### LensSystem.thrift
```thrift
namespace cpp illumination

service LensSystem {
    void   SetFocus(1: double position_mm),
    double GetFocus(),
    void   SetAperture(1: double na),
    double GetAperture()
}
```

---

## ScanManager Repo

### StageController.thrift
```thrift
namespace cpp scan_manager

struct Position {
    1: double x_mm,
    2: double y_mm,
    3: double z_mm
}

service StageController {
    void     MoveTo(1: Position pos),
    Position GetPosition(),
    void     Home(),
    bool     IsReady()
}
```

### ScanSequencer.thrift
```thrift
namespace cpp scan_manager

enum ScanStatus { IDLE = 0, SCANNING = 1, DONE = 2, ERROR = 3 }

service ScanSequencer {
    void       StartScan(1: string scan_id),
    void       StopScan(),
    ScanStatus GetStatus(),
    double     GetProgress()
}
```

---

## ExposeSequence Repo

### ExposureController.thrift
```thrift
namespace cpp expose_sequence

enum ExposeStatus { IDLE = 0, EXPOSING = 1, DONE = 2, ERROR = 3 }

service ExposureController {
    void         StartExposure(1: string shot_id),
    void         StopExposure(),
    ExposeStatus GetStatus(),
    double       GetElapsedTime()
}
```

### DoseManager.thrift
```thrift
namespace cpp expose_sequence

service DoseManager {
    void   SetTargetDose(1: double dose_mj_cm2),
    double GetTargetDose(),
    double GetActualDose(),
    void   CalibrateDose(),
    void   ApplyCorrection(1: double delta_dose)
}
```
