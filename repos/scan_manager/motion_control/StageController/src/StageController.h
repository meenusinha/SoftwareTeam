#pragma once
#include <string>
namespace scan_manager {

struct Position { double x_mm, y_mm, z_mm; };

class StageController {
public:
    void     MoveTo(const Position& pos);
    Position GetPosition() const;
    void     Home();
    bool     IsReady() const;

private:
    Position current_ = {0.0, 0.0, 0.0};
    bool     ready_   = true;
};

} // namespace scan_manager
