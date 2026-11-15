#include "2dsprite.h"
#include "client455_font.h"
#include "r3render.h"
#include "userinterface/guicontroller/guiscreen.h"
#include "userinterface/spritemgr.h"
#include <mmsystem.h>

namespace {
constexpr DWORD areaNoticeDuration = 5000;
constexpr DWORD areaNoticeFade = 500;

BYTE AreaNoticeAlpha455(DWORD elapsed)
{
    if (elapsed >= areaNoticeDuration) return 0;
    if (elapsed < areaNoticeFade) return static_cast<BYTE>(elapsed * 255 / areaNoticeFade);
    if (elapsed > areaNoticeDuration - areaNoticeFade)
        return static_cast<BYTE>((areaNoticeDuration - elapsed) * 255 / areaNoticeFade);
    return 255;
}
}

void CLand::SetAreaLabel455(const char* label, DWORD catalogIndex)
{
    // RVA 0x3C9D30 copies at most 63 bytes at multibyte boundaries.
    if (label) {
        _mbsnbcpy(reinterpret_cast<unsigned char*>(m_areaLabel455),
                  reinterpret_cast<const unsigned char*>(label), sizeof(m_areaLabel455) - 1);
        m_areaLabel455[sizeof(m_areaLabel455) - 1] = '\0';
        m_areaNoticeStart455 = timeGetTime();
    } else {
        m_areaLabel455[0] = '\0';
        m_areaNoticeStart455 = 0;
    }
    m_areaLabelMap455 = catalogIndex;
    if (auto* radar = _GetRadarWindow()) radar->SetAreaLabel455(m_areaLabel455);
}

void CLand::DrawAreaNotice455()
{
    if (!m_areaNoticeStart455) return;
    const DWORD elapsed = timeGetTime() - m_areaNoticeStart455;
    if (elapsed > areaNoticeDuration) {
        m_areaNoticeStart455 = 0;
        return;
    }
    const DWORD alpha = static_cast<DWORD>(AreaNoticeAlpha455(elapsed)) << 24;
    if (!alpha || !m_areaLabel455[0]) return;

    auto* device = GetD3dDevice();
    auto* screen = CGUIScreen::GetSingletonPtr();
    auto* sprites = _GetUISpriteMgr();
    constexpr DWORD action = 14, frame = 0;
    auto* atlas = sprites ? sprites->GetTargetSprite455(4) : nullptr;
    if (!device || !screen || !atlas || atlas->GetMaxActions() <= action ||
        atlas->GetMaxFrames(action) <= frame) return;
    auto* texture = atlas->GetD3D8TexPtr(action, frame);
    if (!texture) return;
    const LONG width = atlas->GetSpriteOrgXL(action, frame);
    const LONG height = atlas->GetSpriteOrgYL(action, frame);
    if (width <= 0 || height <= 0) return;
    const LONG x = (screen->GetSizeX() - width) / 2;
    const LONG y = 153 - height / 2;

    DWORD depth = D3DZB_TRUE;
    if (FAILED(device->GetRenderState(D3DRS_ZENABLE, &depth))) return;
    // The frame is padded to its texture size. Keep the shared atlas cursor untouched.
    Draw2DSprite(static_cast<float>(x), static_cast<float>(y),
                 static_cast<float>(atlas->GetSpriteXL(action, frame)),
                 static_cast<float>(atlas->GetSpriteYL(action, frame)), texture, alpha | 0xffffffu);

    constexpr DWORD textFlags = 0x40000020;
    if (RF455_GetFontSnapshotFlags(textFlags).font) {
        const LONG textWidth = (RF455_MeasureTextAnsi(m_areaLabel455).cx / 6) * 16;
        float position[] = {static_cast<float>(x + (width - textWidth) / 2),
                            static_cast<float>(y + (height - 32) / 2), 0.99f, 1.0f};
        device->SetRenderState(D3DRS_ZENABLE, FALSE);
        RF455_DrawTextAnsiScaled(position, m_areaLabel455, alpha | 0xa6deebu, textFlags, 1.0f);
    }
    device->SetRenderState(D3DRS_ZENABLE, depth);
}
