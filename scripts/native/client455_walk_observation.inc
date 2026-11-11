// Bounded input-state fixture for the owned, hidden live-client run.
// SetKeyboardState affects only the calling thread's keyboard table.
class RF455WalkKeyObservation {
public:
    explicit RF455WalkKeyObservation(DWORD forwardKey) {
        auto& state = RF455_WorldObservation();
        if (!state.walk || (state.combat && !state.combatApproachMs) ||
            forwardKey != VK_UP || state.walkKeyReleased) return;
        const auto elapsed = GetTickCount64() - state.acceptedAt;
        if (elapsed < 450) return;
        const auto end = 450 + (state.combat ? state.combatApproachMs : state.walkDurationMs);
        if (elapsed >= end) {
            state.walkKeyReleased = true;
            RF455_ObserveProtocol("walk-key-up", forwardKey, static_cast<unsigned>(elapsed),
                                  (GetKeyState(VK_UP) & 0x8000) != 0);
            return;
        }

        if (!GetKeyboardState(previous) || (previous[VK_UP] & 0x80)) return;
        BYTE staged[256];
        std::memcpy(staged, previous, sizeof(staged));
        staged[VK_UP] |= 0x80;
        restore = SetKeyboardState(staged) != FALSE;
        if (restore && !state.walkKeyObserved && (GetKeyState(VK_UP) & 0x8000)) {
            state.walkKeyObserved = true;
            RF455_ObserveProtocol("walk-key-down", forwardKey, static_cast<unsigned>(elapsed), 1);
        }
    }

    ~RF455WalkKeyObservation() {
        if (restore && !SetKeyboardState(previous))
            RF455_ObserveProtocol("walk-key-restore-failed", VK_UP, 0, 0);
    }

    RF455WalkKeyObservation(const RF455WalkKeyObservation&) = delete;
    RF455WalkKeyObservation& operator=(const RF455WalkKeyObservation&) = delete;

private:
    BYTE previous[256];
    bool restore = false;
};

class RF455CombatModifierObservation {
public:
    bool apply(DWORD modifier) {
        if (modifier == DWORD(-1)) return true;
        if (modifier != VK_CONTROL && modifier != VK_SHIFT) return false;
        if (!GetKeyboardState(previous)) return false;
        BYTE staged[256];
        std::memcpy(staged, previous, sizeof staged);
        staged[modifier] |= 0x80;
        restore = SetKeyboardState(staged) != FALSE;
        return restore;
    }

    ~RF455CombatModifierObservation() {
        if (restore && !SetKeyboardState(previous))
            RF455_ObserveProtocol("combat-key-restore-failed", 0, 0, 0);
    }

private:
    BYTE previous[256];
    bool restore = false;
};
