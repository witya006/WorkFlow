// Supplies right drags to the owned run's normal UI and world mouse handlers.
class RF455CameraMouseObservation {
public:
    RF455CameraMouseObservation() {
        auto& state = RF455_WorldObservation();
        if (!state.camera && !state.captureMonsters) return;
        const auto elapsed = GetTickCount64() - state.acceptedAt;
        const auto end = state.captureMonsters ? 1200 : 3000;
        if (elapsed < 300 || elapsed >= end) return;

        const auto gesture = static_cast<unsigned>((elapsed - 300) / 900);
        const auto offset = (elapsed - 300) % 900;
        const unsigned step = offset < 200 ? 0 : offset < 400 ? 1 : offset < 700 ? 2 : 3;
        const unsigned phase = gesture * 4 + step + 1;
        const bool changed = state.cameraPhase != phase;

        previous = gMouse;
        active = true;
        gMouse.x = 160;
        // A shorter drag puts the horizon in view during monster sampling.
        gMouse.y = step < 2 ? 420 : state.captureMonsters ? 280 : 74;
        gMouse.z = 0;
        gMouse.button = (step == 1 || step == 2) ? _RIGHT_BUTTON_DOWN : 0;
        if (step == 3 && changed) gMouse.button = _RIGHT_BUTTON_UP;
        gMouse.LDBClick = FALSE;
        gMouse.RDBClick = FALSE;
        if (changed) {
            state.cameraPhase = phase;
            RF455_ObserveProtocol("camera-mouse", phase, gMouse.y, gMouse.button);
        }
    }

    ~RF455CameraMouseObservation() {
        if (active) gMouse = previous;
    }

    RF455CameraMouseObservation(const RF455CameraMouseObservation&) = delete;
    RF455CameraMouseObservation& operator=(const RF455CameraMouseObservation&) = delete;

private:
    _MOUSE previous;
    bool active = false;
};
