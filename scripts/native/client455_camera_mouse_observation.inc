// Supplies bounded camera and combat gestures to the owned run's mouse handlers.
class RF455CameraMouseObservation {
public:
    RF455CameraMouseObservation() {
        auto& state = RF455_WorldObservation();
        if (!state.camera && !state.captureMonsters) return;
        const auto elapsed = GetTickCount64() - state.acceptedAt;
        if (state.combat) {
            if (elapsed >= 1280) sampleCombatClick(state, elapsed);
            return;
        }
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
    void sampleCombatClick(RF455WorldObservation& state, ULONGLONG elapsed) {
        const auto draw = state.combatDraw;
        state.combatDraw = {};
        if (state.combatButtonDown) {
            previous = gMouse;
            active = true;
            gMouse.button = _LEFT_BUTTON_UP;
            gMouse.LDBClick = FALSE;
            gMouse.RDBClick = FALSE;
            state.combatButtonDown = false;
            return;
        }
        if (elapsed < state.nextCombatClickAt || elapsed >= 18000 || state.combatTarget)
            return;
        if (!draw.present) {
            if (!state.combatTarget) scanCombatView(state, elapsed);
            return;
        }

        const auto* viewport = GetR3State();
        previous = gMouse;
        active = true;
        gMouse.x = static_cast<int>((1.0f + draw.screenX) * viewport->mScreenXsize * 0.5f);
        gMouse.y = static_cast<int>((1.0f - draw.screenY) * viewport->mScreenYsize * 0.5f);
        gMouse.z = 0;
        gMouse.button = _LEFT_BUTTON_DOWN;
        gMouse.LDBClick = FALSE;
        gMouse.RDBClick = FALSE;
        state.combatTarget = draw.serial;
        state.nextCombatClickAt = elapsed + 700;
        state.combatButtonDown = true;
        RF455_ObserveProtocol("combat-click", ++state.combatClicks, draw.serial,
                              static_cast<unsigned>(elapsed));
    }

    void scanCombatView(RF455WorldObservation& state, ULONGLONG elapsed) {
        const auto offset = (elapsed - 1280) % 800;
        if (offset >= 600) return;
        const unsigned step = offset < 120 ? 0 : offset < 280 ? 1 : offset < 460 ? 2 : 3;
        const auto phase = static_cast<unsigned>(100 + ((elapsed - 1280) / 800) * 4 + step);
        const bool changed = phase != state.cameraPhase;
        previous = gMouse;
        active = true;
        gMouse.x = step ? 190 : 320;
        gMouse.y = 250;
        if (step == 2) {
            if (changed) state.combatScanBaseYaw = _GetCamera()->GetYaw();
            const float perPixel = GetR3State()->mScreenXsize * (0.2f / 1024.0f);
            const int y = 250 + static_cast<int>((26.0f - state.combatScanBaseYaw) / perPixel);
            const int bottom = static_cast<int>(GetR3State()->mScreenYsize) - 45;
            gMouse.y = y < 45 ? 45 : y > bottom ? bottom : y;
        }
        gMouse.z = 0;
        gMouse.button = step == 1 || step == 2 ? _RIGHT_BUTTON_DOWN :
                        step == 3 && changed ? _RIGHT_BUTTON_UP : 0;
        gMouse.LDBClick = FALSE;
        gMouse.RDBClick = FALSE;
        if (changed) {
            state.cameraPhase = phase;
            RF455_ObserveProtocol("combat-camera", phase, gMouse.y, gMouse.button);
        }
    }

    _MOUSE previous;
    bool active = false;
};
