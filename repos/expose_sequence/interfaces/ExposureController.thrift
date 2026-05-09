namespace cpp expose_sequence

enum ExposeStatus { IDLE = 0, EXPOSING = 1, DONE = 2, ERROR = 3 }

service ExposureController {
    void         StartExposure(1: string shot_id),
    void         StopExposure(),
    ExposeStatus GetStatus(),
    double       GetElapsedTime()
}
