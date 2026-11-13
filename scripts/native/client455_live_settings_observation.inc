// Opt-in diagnostics on our live client only. No account data or server writes.
#include "userinterface/gamewindow/etcwin/guioptionwindow.h"
#include "gameobject/manager/ccharactermgr.h"
#include "client455_enhanced_lighting.h"

static void RF455_ObserveLiveSettings(CGUIOptionWindow& options, CCharacterMgr& characters) {
    static const bool enabled = [] {
        char value[2]{};
        return GetEnvironmentVariableA("RF455_OBSERVE_SETTINGS", value, 2) == 1 && value[0] == '1';
    }();
    if (!enabled || !RF455_WorldObservation().acceptedAt) return;
    static unsigned phase = 0;
    static ULONGLONG next = 0;
    static bool originalLighting = false;
    static BOOL originalAuto = FALSE;
    static BYTE originalDistance = 0;
    if (phase >= 6 || GetTickCount64() < next) return;
    next = GetTickCount64() + 500;
    auto click = [&](CGUIObject& control) {
        _mouse_event event{};event.source=&control;event.id=MOUSE_CLICKED;
        options.MouseEvent(event);
    };
    auto capture = [&](const char* name) {
        const auto frame = RF455_SaveWorldFrame(name);
        return SUCCEEDED(frame.result) && frame.width == 1920 && frame.height == 1080;
    };
    bool ok = true;
    switch (phase) {
    case 0:
        originalLighting = RF455_EnhancedActorLightingEnabled();
        originalAuto = characters.IsEnableAutoVisualFieldAdjustment();
        originalDistance = characters.GetVisualFieldAdjustmentLevel();
        ok = capture("settings-world-before.png");
        options.Open();click(options.Tab455(CGUIOptionWindow::GraphicsPage));
        ok = ok && options.IsShow() && RF455_EnhancedActorLightingAvailable();
        break;
    case 1:
        ok = capture("settings-world-menu.png");
        click(options.Lighting455(1));
        options.SwitchOn(CGUIOptionWindow::AutoSeeDist, FALSE);
        options.SetGraphicOption(CGUIOptionWindow::SeeDist, 2);
        ok = options.Apply455() && ok;
        ok = ok && RF455_EnhancedActorLightingEnabled() &&
             !characters.IsEnableAutoVisualFieldAdjustment() && characters.GetVisualFieldAdjustmentLevel() == 2;
        break;
    case 2:
        ok = capture("settings-world-menu-applied.png");
        options.Close();
        break;
    case 3:
        ok = capture("settings-world-enhanced.png") && RF455_EnhancedActorLightingEnabled();
        options.Open();click(options.Lighting455(originalLighting ? 1 : 0));
        options.SwitchOn(CGUIOptionWindow::AutoSeeDist, originalAuto);
        options.SetGraphicOption(CGUIOptionWindow::SeeDist, originalDistance);
        ok = options.Apply455() && ok;
        options.Close();
        break;
    case 4:
        ok = capture("settings-world-restored.png") &&
             RF455_EnhancedActorLightingEnabled() == originalLighting &&
             characters.IsEnableAutoVisualFieldAdjustment() == originalAuto &&
             characters.GetVisualFieldAdjustmentLevel() == originalDistance;
        break;
    case 5:
        ok = !options.IsShow();
        break;
    }
    RF455_ObserveProtocol("settings-live", phase++, ok, RF455_EnhancedActorLightingEnabled());
}
