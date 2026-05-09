#include "ExposureController.h"
namespace expose_sequence {

void         ExposureController::StartExposure(const std::string&) { status_ = ExposeStatus::EXPOSING; elapsed_ms_ = 0.0; }
void         ExposureController::StopExposure()                    { status_ = ExposeStatus::DONE; }
ExposeStatus ExposureController::GetStatus() const                  { return status_; }
double       ExposureController::GetElapsedTime() const             { return elapsed_ms_; }

} // namespace expose_sequence
