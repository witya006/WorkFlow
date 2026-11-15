#include <new>
#include <utility>

namespace {
std::unique_ptr<RF455SceneInput455> PrepareLevel455(const char* name)
{
    const auto length = name ? strnlen_s(name, 256) : 0;
    if (length <= 4 || length >= 256 || _stricmp(name + length - 4, ".bsp"))
        return nullptr;
    // CLevel::LoadLevel opens the supplied file, then loads the BSP from
    // the engine's MapPath using the supplied filename's basename.
    char base[256];
    std::memcpy(base, name, length + 1);
    StripEXT(base);
    StripPath(base);
    const auto& mapRoot = GetR3State()->MapPath;
    if (strnlen_s(mapRoot, sizeof mapRoot) == sizeof mapRoot) return nullptr;
    char bsp[256];
    const int pathLength = std::snprintf(bsp, sizeof bsp, "%s%s\\%s.bsp",
                                         mapRoot, base, base);
    if (!*base || pathLength <= 0 || static_cast<std::size_t>(pathLength) >= sizeof bsp) return nullptr;

    // The argument can be a different file with the same basename. Retain
    // the original route's check that this explicit input is readable.
    if (_stricmp(name, bsp) != 0) {
        std::unique_ptr<FILE, decltype(&std::fclose)> input(std::fopen(name, "rb"), std::fclose);
        if (!input) return nullptr;
    }

    auto input = std::unique_ptr<RF455SceneInput455>(new (std::nothrow) RF455SceneInput455(bsp));
    if (input && !input->validateBsp()) {
        input->reject(bsp);
        return nullptr;
    }
    if (input) {
        char r3m[256];
        std::memcpy(r3m, bsp, pathLength - 4);
        std::memcpy(r3m + pathLength - 4, ".r3m", sizeof ".r3m");
        // CLevel selects this binary branch by loose file presence, with the
        // archive group disabled. A null material lease records the MST route.
        if (IsExistFile(r3m) && !input->prepareMapMaterials(r3m)) return nullptr;
    }
    return input;
}
}

char* CLand::IndexedMapName455(BYTE index)
{
    if (!m_pLevel || !m_maps455.maps || index == 0xff || index >= m_maps455.count) return nullptr;
    // Pinned 455 RVA 0x3C8BC9 passes the BSP path at map row +358 to LoadLevel.
    auto& name = m_maps455.maps[index].pBspFileName;
    return *name && std::memchr(name, '\0', sizeof name) ? name : nullptr;
}

bool CLand::PreparedMapMatches455(BYTE index, const char* name) const
{
    const auto& mapRoot = GetR3State()->MapPath;
    return m_preparedMap455 && index == m_preparedMapIndex455 &&
        _stricmp(name, m_preparedMapName455) == 0 &&
        strnlen_s(mapRoot, sizeof mapRoot) < sizeof mapRoot &&
        _stricmp(mapRoot, m_preparedMapRoot455) == 0;
}

void CLand::DiscardPreparedMap455()
{
    m_preparedMap455.reset();
}

std::unique_ptr<RF455SceneInput455> CLand::TakePreparedMap455(BYTE index)
{
    const auto* name = IndexedMapName455(index);
    if (name && PreparedMapMatches455(index, name)) return std::move(m_preparedMap455);
    DiscardPreparedMap455();
    return name ? PrepareLevel455(name) : nullptr;
}

bool CLand::CanLoadMap455(BYTE index)
{
    const auto* name = IndexedMapName455(index);
    if (name && PreparedMapMatches455(index, name)) return true;
    DiscardPreparedMap455();
    if (!name) return false;

    auto prepared = PrepareLevel455(name);
    if (!prepared) return false;
    constexpr std::size_t maxPreparedMapBytes = 32u * 1024u * 1024u;
    if (prepared->fitsRetention(maxPreparedMapBytes)) {
        m_preparedMapIndex455 = index;
        strcpy_s(m_preparedMapName455, name);
        strcpy_s(m_preparedMapRoot455, GetR3State()->MapPath);
        m_preparedMap455 = std::move(prepared);
    }
    return true;
}
