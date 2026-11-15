namespace {
constexpr DWORD worldMapHoverColor455 = 0xfffafa00;
const char* worldMapLabel455(const RF455MapLabel& label)
{
    return label.text.empty() ? "" : reinterpret_cast<const char*>(label.text.data());
}
}

void CGUIMiniMapWindow::LayoutWorldMap455()
{
    const LONG width = gScreen.GetSizeX();
    const LONG height = gScreen.GetSizeY();
    if (width <= 0 || height <= 0) return;
    SetPos(0, 0);
    SetSize(width, height);
    m_worldMapSurface455.SetPos(0, 0);
    m_worldMapSurface455.SetSize(width, height);
}

void CGUIMiniMapWindow::ResetWorldMap455()
{
    if (!IsWorldMap455()) return;
    Remove(&m_worldMapSurface455);
    m_worldMapSurface455.SetSpriteInfo(nullptr);
    m_worldMapMask455.clear();
    m_worldMapName455.clear();
    m_worldMapDepth455 = 0;
    m_worldLabelSizes455.clear();
    m_worldLabelEnabled455.clear();
    m_worldMapHover455 = -1;
    SetPos(m_localMapPosition455);
    SetSize(m_localMapSize455.x, m_localMapSize455.y);
}

void CGUIMiniMapWindow::Close()
{
    ClearLocalMapTooltip455();
    const bool world = IsWorldMap455();
    ResetWorldMap455();
    if (world) {
        // The shared slot holds the last world layer until the local map is reopened.
        m_byMiniMapIndex = 0xff;
        m_mapTerrain455.SetSpriteInfo(nullptr);
    }
    CGUIWindow::Close();
}

bool CGUIMiniMapWindow::SelectWorldMap455(const RF455MapLayer& layer, unsigned depth)
{
    char path[128];
    if (!g_pLand || depth > 3 || !RF455_WorldMapSpritePath(layer, path, sizeof(path))) return false;
    const auto name = reinterpret_cast<const char*>(layer.name.data());
    const auto end = static_cast<const char*>(std::memchr(name, 0, layer.name.size()));
    std::string nextName(name, end ? static_cast<std::size_t>(end - name) : layer.name.size());
    if (m_worldMapName455 == nextName && m_worldMapDepth455 == depth) return true;

    RF455MapHitMask nextMask;
    if (!nextMask.load(layer)) return false;
    std::vector<POINT> nextSizes;
    std::vector<bool> nextEnabled;
    nextSizes.reserve(layer.labels.size());
    nextEnabled.reserve(layer.labels.size());
    const auto& catalog = g_pLand->MapData455();
    for (std::size_t i = 0; i < layer.labels.size(); ++i) {
        const auto* label = worldMapLabel455(layer.labels[i]);
        nextSizes.push_back({RF455_TextWidth(label), RF455_DefaultTextHeight()});
        const auto childName = nextName + "_" + std::to_string(i + 1);
        nextEnabled.push_back(*label && (!depth || RF455_FindMapLayer(catalog, RF455MapLayerSection::World, childName.c_str())));
    }
    if (!gSpriteMgr.LoadMinimapSprite455(path)) return false;

    ClearLocalMapTooltip455();
    if (!IsWorldMap455()) {
        GetPos(m_localMapPosition455);
        GetSize(m_localMapSize455);
        m_worldMapSurface455.AddMouseEventHandler(this);
        m_worldMapSurface455.AddMouseMotionEventHandler(this);
        Add(&m_worldMapSurface455);
    }
    m_worldMapName455.swap(nextName);
    m_worldMapDepth455 = depth;
    m_worldMapMask455 = std::move(nextMask);
    m_worldLabelSizes455.swap(nextSizes);
    m_worldLabelEnabled455.swap(nextEnabled);
    m_worldMapHover455 = -1;
    LayoutWorldMap455();
    SPRITE_INFO image{gSpriteMgr.GetSprite(SP_ID_MINIMAP), 0, 0};
    m_worldMapSurface455.SetSpriteInfo(&image);
    return true;
}

void CGUIMiniMapWindow::BindWorldMapSprite455()
{
    LayoutWorldMap455();
    m_worldMapSurface455.SetSpriteInfo(nullptr);
    if (!g_pLand) return;
    const auto* layer = RF455_FindMapLayer(g_pLand->MapData455(), RF455MapLayerSection::World, m_worldMapName455.c_str());
    char path[128];
    if (!layer || !RF455_WorldMapSpritePath(*layer, path, sizeof(path)) ||
        !gSpriteMgr.LoadMinimapSprite455(path)) return;
    SPRITE_INFO image{gSpriteMgr.GetSprite(SP_ID_MINIMAP), 0, 0};
    m_worldMapSurface455.SetSpriteInfo(&image);
}

void CGUIMiniMapWindow::UpdateWorldMapHover455(LONG x, LONG y)
{
    m_worldMapHover455 = -1;
    if (!g_pLand || !m_worldMapSurface455.IsCrossed(x, y) ||
        !m_worldMapSurface455.GetSpriteInfo()->pSprite) return;
    const auto* layer = RF455_FindMapLayer(g_pLand->MapData455(), RF455MapLayerSection::World, m_worldMapName455.c_str());
    const auto width = m_worldMapSurface455.GetSizeX();
    const auto height = m_worldMapSurface455.GetSizeY();
    if (!layer || width <= 0 || height <= 0) return;
    const auto px = x - m_worldMapSurface455.GetPosX();
    const auto py = y - m_worldMapSurface455.GetPosY();
    if (px < 0 || py < 0 || px >= width || py >= height) return;
    const float xFraction = static_cast<float>(static_cast<double>(px) / width);
    const float yFraction = static_cast<float>(static_cast<double>(py) / height);
    m_worldMapHover455 = m_worldMapMask455.hit(static_cast<std::uint32_t>(layer->width * double(xFraction)),
                                             static_cast<std::uint32_t>(layer->height * double(yFraction)));
    if (m_worldMapHover455 >= 0 &&
        (static_cast<std::size_t>(m_worldMapHover455) >= m_worldLabelEnabled455.size() ||
         !m_worldLabelEnabled455[m_worldMapHover455])) m_worldMapHover455 = -1;
}

bool CGUIMiniMapWindow::HandleWorldMapMouse455(_mouse_event& event)
{
    if (event.source == &m_worldMapButton455 && event.id == MOUSE_CLICKED && !IsWorldMap455()) {
        if (gScreen.ExistObject()) return true;
        if (g_pLand && g_pLand->MapData455().maps && m_byMiniMapIndex < g_pLand->MapData455().count) {
            const auto& catalog = g_pLand->MapData455();
            const char* label = catalog.maps[m_byMiniMapIndex].pName_UI;
            if (*label) {
                const auto* parent = RF455_FindWorldMapParent(catalog, label);
                if (parent) SelectWorldMap455(*parent, 0);
            }
        }
        return true;
    }
    if (!IsWorldMap455()) return false;
    if (event.source != &m_worldMapSurface455 || !g_pLand || gScreen.ExistObject()) return true;
    const auto& catalog = g_pLand->MapData455();
    if (event.id == MOUSE_LEAVED) {
        m_worldMapHover455 = -1;
    } else if (event.id == LMOUSE_STROKED) {
        const auto separator = m_worldMapName455.rfind('_');
        if (m_worldMapDepth455 < 3 && separator != std::string::npos) {
            const auto name = m_worldMapName455.substr(0, separator);
            const auto* parent = RF455_FindMapLayer(catalog, RF455MapLayerSection::World, name.c_str());
            if (parent) SelectWorldMap455(*parent, m_worldMapDepth455 + 1);
        }
    } else if (event.id == MOUSE_STROKED || event.id == MOUSE_HOVERED) {
        UpdateWorldMapHover455(event.xPos, event.yPos);
        if (m_worldMapHover455 < 0 || event.id != MOUSE_STROKED) return true;
        const auto* layer = RF455_FindMapLayer(catalog, RF455MapLayerSection::World, m_worldMapName455.c_str());
        if (!layer || static_cast<std::size_t>(m_worldMapHover455) >= layer->labels.size()) return true;
        const auto* label = worldMapLabel455(layer->labels[m_worldMapHover455]);
        const auto childName = m_worldMapName455 + "_" + std::to_string(m_worldMapHover455 + 1);
        if (!m_worldMapDepth455) {
            if (*label) g_pLand->ShowMapLabel455(label);
        } else if (const auto* child = RF455_FindMapLayer(catalog, RF455MapLayerSection::World, childName.c_str())) {
            SelectWorldMap455(*child, m_worldMapDepth455 - 1);
        }
    }
    return true;
}

void CGUIMiniMapWindow::ClearLocalMapTooltip455()
{
    if (!m_localMapTooltip455.empty() && GetMouseDetectedObject() == &m_uiMiniMap)
        gScreen.RemoveTooltip();
    m_localMapTooltip455.clear();
}

void CGUIMiniMapWindow::ResetLocalMapLabels455()
{
    ClearLocalMapTooltip455();
    m_localLabels455.clear();
    m_localLabelsPrepared455 = false;
}

void CGUIMiniMapWindow::PrepareLocalMapLabels455(const RF455LocalMapLayer& local)
{
    // 0x3C9869..0x3C994E populates this overlay in native label order.
    // 0x307E50/0x308130 moves an existing exact text match to its last anchor.
    const auto& labels = local.layer()->labels;
    m_localLabels455.reserve(labels.size());
    for (std::size_t index = 0; index < labels.size(); ++index) {
        const auto* text = local.labelAt(index);
        if (!text) continue;
        const auto x = static_cast<std::int32_t>(labels[index].fields[1]);
        const auto y = static_cast<std::int32_t>(labels[index].fields[2]);
        const auto match = std::find_if(m_localLabels455.begin(), m_localLabels455.end(),
            [text](const LocalMapLabel455& label) {
                return _mbscmp(reinterpret_cast<const unsigned char*>(label.text.c_str()),
                               reinterpret_cast<const unsigned char*>(text)) == 0;
            });
        if (match == m_localLabels455.end()) {
            m_localLabels455.push_back({text, x, y, RF455_TextWidth(text)});
        } else {
            match->x = x;
            match->y = y;
        }
    }
    m_localLabelsPrepared455 = true;
}

void CGUIMiniMapWindow::DrawLocalMapLabels455()
{
    if (!g_pLand || !IsCurrentMapBound455(g_pLand->GetMapIndex())) return;
    const auto& local = g_pLand->LocalMapLayer455();
    const auto* layer = local.layer();
    const LONG width = m_mapTerrain455.GetSizeX();
    const LONG height = m_mapTerrain455.GetSizeY();
    if (!layer || !layer->width || !layer->height || width <= 0 || height <= 0 ||
        !RF455_TextResourcesReady())
        return;
    if (!m_localLabelsPrepared455) PrepareLocalMapLabels455(local);
    const int labelHeight = RF455_DefaultTextHeight();
    if (labelHeight <= 0 || labelHeight > height || !m_alpha455) return;

    const DWORD color = (static_cast<DWORD>(m_alpha455) << 24) | 0xffffffu;
    const LONG left = m_mapTerrain455.GetPosX();
    const LONG top = m_mapTerrain455.GetPosY();
    for (const auto& label : m_localLabels455) {
        if (label.width <= 0 || label.width > width) continue;
        const auto x = std::int64_t(label.x) * width / layer->width - label.width / 2;
        const auto y = std::int64_t(label.y) * height / layer->height - labelHeight / 2;
        const auto offsetX = (std::max<std::int64_t>)(0, (std::min<std::int64_t>)(x, width - label.width));
        const auto offsetY = (std::max<std::int64_t>)(0, (std::min<std::int64_t>)(y, height - labelHeight));
        DrawR3Hangul(left + static_cast<LONG>(offsetX), top + static_cast<LONG>(offsetY),
                     const_cast<char*>(label.text.c_str()), color, R3_HAN_OUTLINE);
    }
}

void CGUIMiniMapWindow::UpdateLocalMapTooltip455(LONG x, LONG y)
{
    const auto* target = GetMouseDetectedObject();
    if (target && target != &m_uiMiniMap) return;
    const char* label = nullptr;
    if (IsShow() && !gScreen.ExistObject() && g_pLand &&
        IsCurrentMapBound455(g_pLand->GetMapIndex())) {
        const auto width = m_mapTerrain455.GetSizeX();
        const auto height = m_mapTerrain455.GetSizeY();
        const auto left = static_cast<std::int64_t>(x) - m_mapTerrain455.GetPosX();
        const auto top = static_cast<std::int64_t>(y) - m_mapTerrain455.GetPosY();
        if (left >= 0 && left < width && top >= 0 && top < height) {
            const float xFraction = static_cast<float>(static_cast<double>(left) / width);
            const float yFraction = static_cast<float>(static_cast<double>(top) / height);
            label = g_pLand->LocalMapLayer455().labelAt(xFraction, yFraction);
        }
    }
    const auto length = label ? std::strcspn(label, "\r\n") : 0;
    if (!length || length >= TOOLTIP_MAX_STR) {
        ClearLocalMapTooltip455();
        return;
    }
    if (m_localMapTooltip455.compare(0, std::string::npos, label, length) == 0) return;
    char lines[1][TOOLTIP_MAX_STR]{};
    std::memcpy(lines[0], label, length);
    m_localMapTooltip455.assign(lines[0], length);
    gScreen.SetTooltip(1, lines);
}

void CGUIMiniMapWindow::HandleLocalMapMouse455(_mouse_event& event)
{
    if (event.source != &m_uiMiniMap) return;
    if (event.id == MOUSE_HOVERED) {
        m_localMapTooltip455.clear();
        UpdateLocalMapTooltip455(event.xPos, event.yPos);
    } else if (event.id == MOUSE_LEAVED || event.id == MOUSE_STROKED || event.id == LMOUSE_STROKED) {
        // CGUIObject clears the shared tooltip before dispatching these events.
        m_localMapTooltip455.clear();
    }
}

void CGUIMiniMapWindow::MouseMotionEvent(_mouse_motion_event& event)
{
    if (!IsWorldMap455()) {
        if (event.source == &m_uiMiniMap && event.id == MOUSE_MOVE)
            UpdateLocalMapTooltip455(event.xPos, event.yPos);
        CGUIWindow::MouseMotionEvent(event);
    } else if (event.source == &m_worldMapSurface455 && event.id == MOUSE_MOVE) {
        UpdateWorldMapHover455(event.xPos, event.yPos);
    }
}

void CGUIMiniMapWindow::DrawWorldMapLabels455()
{
    if (!g_pLand || !m_worldMapSurface455.GetSpriteInfo()->pSprite) return;
    const auto* layer = RF455_FindMapLayer(g_pLand->MapData455(), RF455MapLayerSection::World, m_worldMapName455.c_str());
    if (!layer || !layer->width || !layer->height || m_worldLabelSizes455.size() != layer->labels.size() ||
        m_worldLabelEnabled455.size() != layer->labels.size()) return;
    const LONG width = m_worldMapSurface455.GetSizeX(), height = m_worldMapSurface455.GetSizeY();
    for (std::size_t i = 0; i < layer->labels.size(); ++i) {
        const auto& label = layer->labels[i];
        const auto* text = worldMapLabel455(label);
        if (!*text) continue;
        const auto size = m_worldLabelSizes455[i];
        const auto x = static_cast<std::int64_t>(static_cast<std::int32_t>(label.fields[1])) * width / layer->width - size.x / 2;
        const auto y = static_cast<std::int64_t>(static_cast<std::int32_t>(label.fields[2])) * height / layer->height - size.y / 2;
        const auto left = static_cast<LONG>((std::max<std::int64_t>)(0, (std::min<std::int64_t>)(x, width - size.x)));
        const auto top = static_cast<LONG>((std::max<std::int64_t>)(0, (std::min<std::int64_t>)(y, height - size.y)));
        const DWORD color = !m_worldLabelEnabled455[i] ? 0xff8d8d8d :
            (static_cast<int>(i) == m_worldMapHover455 ? worldMapHoverColor455 : 0xffffffff);
        DrawR3Hangul(left, top, const_cast<char*>(text), color, R3_HAN_OUTLINE);
    }
    LONG y = static_cast<LONG>(height * 0.9);
    for (unsigned id : {0x7e7u, 0x7e8u}) {
        const auto* text = RF455_GetNormalLanguagePack()->get(id);
        DrawR3Hangul((width - RF455_TextWidth(text)) / 2, y, const_cast<char*>(text), 0xffffffff, R3_HAN_OUTLINE);
        y += RF455_DefaultTextHeight() + 5;
    }
}
