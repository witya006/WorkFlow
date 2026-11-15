#include "client455_screen_transition.h"
#include "client455_character_rfs.h"
#include "client455_nation_paths.h"
#include "../../../CLand.h"
#include <cmath>
#include <cstdio>
#include <cstring>

extern CLand* g_pLand;

namespace {
IDirect3DTexture9* LoadTransitionTexture455(const char* path)
{
    constexpr std::uint64_t maxBytes = 16u * 1024u * 1024u;
    auto* device = GetD3dDevice();
    if (!device) return nullptr;
    const auto source = RF455_GetCharacterRfsCache()->ReadLooseBytes(path, maxBytes);
    if (source.status != RF455ResourceReadStatus::Ready || !source.bytes || source.bytes->empty())
        return nullptr;
    IDirect3DTexture9* texture = nullptr;
    const auto result = D3DXCreateTextureFromFileInMemory(device, source.bytes->data(),
        static_cast<UINT>(source.bytes->size()), &texture);
    if (FAILED(result) && texture) {
        texture->Release();
        return nullptr;
    }
    return texture;
}

bool IsLoadingImageName455(const char* name, std::size_t capacity)
{
    if (!name || !capacity || !*name) return false;
    const auto* end = static_cast<const char*>(std::memchr(name, '\0', capacity));
    if (!end) return false;
    for (auto* p = name; p != end; ++p) {
        const char c = *p;
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9') || c == '_' || c == '-') continue;
        return false;
    }
    return true;
}
}

void CGUIMapLoadingWindow::ReleaseTransition455()
{
    if (m_transitionImage455) m_transitionImage455->Release();
    if (m_transitionMask455) m_transitionMask455->Release();
    m_transitionImage455 = m_transitionMask455 = nullptr;
    m_transitionOpacity455 = 0.0f;
    m_transitionOpening455 = false;
}

void CGUIMapLoadingWindow::PrepareTransition455()
{
    ReleaseTransition455();
    SetSprite();
    if (m_transitionMap455 == 0xff) return;
    const auto* land = g_pLand;
    if (!land) return;
    const auto& catalog = land->MapData455();
    if (!catalog.maps || m_transitionMap455 >= catalog.count) return;
    const auto& map = catalog.maps[m_transitionMap455];
    const auto* nation = RF455_GetNormalNationPaths();
    const char* directory = nation && std::strcmp(nation->folder, "zh-cn") == 0
        ? ".\\SpriteImage\\zh-cn\\Loading" : ".\\SpriteImage\\Common\\Loading";
    char path[MAX_PATH];

    // Pinned RVA 0x02E0A0 chooses a named map image in 30% of cases,
    // otherwise one of 125 numbered images. Keep the random engine local to
    // this screen so a loading screen cannot perturb gameplay random state.
    unsigned random = timeGetTime() * 214013u + 2531011u;
    const bool namedFirst = ((random >> 16) & 0x7fffu) % 10000 >= 7000;
    const bool namedAvailable = IsLoadingImageName455(map.pName, sizeof map.pName);
    if (namedFirst && namedAvailable) {
        std::snprintf(path, sizeof path, "%s\\%s.dds", directory, map.pName);
        m_transitionImage455 = LoadTransitionTexture455(path);
    }
    if (!m_transitionImage455) {
        random = random * 214013u + 2531011u;
        const unsigned number = (((random >> 16) & 0x7fffu) % 125) + 1;
        std::snprintf(path, sizeof path, "%s\\%03u.dds", directory, number);
        m_transitionImage455 = LoadTransitionTexture455(path);
    }
    if (!m_transitionImage455 && !namedFirst && namedAvailable) {
        std::snprintf(path, sizeof path, "%s\\%s.dds", directory, map.pName);
        m_transitionImage455 = LoadTransitionTexture455(path);
    }
    if (!m_transitionImage455) return;
    std::snprintf(path, sizeof path, "%s\\transition.dds", directory);
    m_transitionMask455 = LoadTransitionTexture455(path);
    m_transitionOpening455 = true;
    SPRITE_INFO noSprite{nullptr, 0, 0};
    SetSpriteInfo(&noSprite);
}

void CGUIMapLoadingWindow::FrameTransition455(float elapsed)
{
    if (!m_transitionImage455 || !std::isfinite(elapsed) || elapsed <= 0.0f) return;
    // Pinned RVA 0x14A780 advances or retreats at 0.7 per second.
    const float step = elapsed * 0.7f;
    if (m_transitionOpening455) {
        m_transitionOpacity455 += step;
        if (m_transitionOpacity455 > 1.0f) m_transitionOpacity455 = 1.0f;
    } else {
        m_transitionOpacity455 -= step;
        if (m_transitionOpacity455 <= 0.0f) ReleaseTransition455();
    }
}

void CGUIMapLoadingWindow::DrawTransition455()
{
    if (m_transitionImage455 && m_transitionOpacity455 > 0.0f)
        RF455_DrawScreenTransition(m_transitionImage455, m_transitionMask455, m_transitionOpacity455);
}

bool CGUIMapLoadingWindow::IsTransitionCovered455() const
{
    return !m_transitionOpening455 || m_transitionOpacity455 >= 1.0f;
}
