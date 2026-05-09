#pragma once
#include <string>
namespace expose_sequence {

enum class ExposeStatus { IDLE, EXPOSING, DONE, ERROR };

class ExposureController {
public:
    void         StartExposure(const std::string& shot_id);
    void         StopExposure();
    ExposeStatus GetStatus() const;
    double       GetElapsedTime() const;

private:
    ExposeStatus status_      = ExposeStatus::IDLE;
    double       elapsed_ms_  = 0.0;
};

} // namespace expose_sequence
