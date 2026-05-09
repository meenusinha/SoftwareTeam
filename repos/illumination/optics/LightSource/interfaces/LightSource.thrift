namespace cpp illumination

service LightSource {
    void   SetPower(1: double watts),
    double GetPower(),
    void   Enable(),
    void   Disable(),
    bool   IsEnabled()
}
