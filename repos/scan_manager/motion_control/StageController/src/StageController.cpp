#include "StageController.h"
namespace scan_manager {

void     StageController::MoveTo(const Position& pos) { current_ = pos; }
Position StageController::GetPosition() const          { return current_; }
void     StageController::Home()                       { current_ = {0.0, 0.0, 0.0}; }
bool     StageController::IsReady() const              { return ready_; }

} // namespace scan_manager
