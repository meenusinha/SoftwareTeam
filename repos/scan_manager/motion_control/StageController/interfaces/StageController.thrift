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
