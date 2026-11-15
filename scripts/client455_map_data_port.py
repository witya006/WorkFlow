"""Connect the 455 map catalog, minimap geometry and world map resources."""
import re
from pathlib import Path
from client455_trade_ore_port import patch_method, replace


def port_map_data(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Map data anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='cland.h':
        raw=b'#include "client455_map_data.h"\r\n'+raw
        begin=raw.index(b'struct MINE_INFO');end=raw.index(b'};',raw.index(b'struct MAP_INFO',begin))+2
        raw=raw[:begin]+b'using MINE_INFO=RF455MineInfo;\r\nusing MAP_AREA_INFO=RF455MapAreaInfo;\r\nusing MAP_INFO=RF455MapInfo;'+raw[end:]
        once(b'\tMAP_INFO\tm_pMapInfo[MAX_MAP];',b'\tRF455MapData m_maps455;\r\n\tRF455LocalMapLayer m_localMap455;\r\n\tMAP_INFO* m_pMapInfo=nullptr;')
        raw,n=re.subn(rb'BYTE(\s+m_byMaxMapNum;)',rb'DWORD\1',raw)
        if n!=1:raise ValueError('Map count member')
        once(b'\tBOOL\tLoadData( void );',b'\tBOOL\tLoadData( void );\r\n\tvoid ToggleCurrentMinimap455();\r\n\tbool ApplyMiniMapGeometry455(BYTE index);\r\n\tconst RF455MapData& MapData455()const{return m_maps455;}\r\n\tRF455MapLoad MapLoadStatus455()const{return m_mapLoad455;}\r\nprivate:\r\n\tRF455MapLoad m_mapLoad455=RF455MapLoad::MissingInput;\r\npublic:')
        once(b'\tinline\tvoid\t\t\tSetMapIndex( BYTE pi_byMapIndex  )\t\t{ m_byMapIndex = pi_byMapIndex; }',
             b'\tvoid SetMapIndex(BYTE index);\r\n\tconst RF455LocalMapLayer& LocalMapLayer455() const { return m_localMap455; }\r\n\tvoid ReceiveAreaLabel455(DWORD catalogIndex, WORD ordinal);\r\n\tvoid DrawAreaNotice455();\r\n\tconst char* AreaLabel455() const { return m_areaLabel455; }\r\nprivate:\r\n\tvoid SetAreaLabel455(const char* label, DWORD catalogIndex = 0xffffffffu);\r\n\tchar m_areaLabel455[64]{};\r\n\tDWORD m_areaLabelMap455 = 0xffffffffu;\r\n\tDWORD m_areaNoticeStart455 = 0;\r\npublic:')
        once(b'\tvoid ToggleCurrentMinimap455();',b'\tvoid ToggleCurrentMinimap455();\r\n\tvoid ShowMapLabel455(const char* label);')
        once(b'\tvoid\tOpenMinimapWindow( char * pi_pMapName, char * pi_pItemName );',
             b'\tbool OpenMapItem455(const char* name);')
        return raw,True
    if relative=='cland.cpp':
        raw=b'#include "client455_nation_paths.h"\r\n#include "client455_protocol_observation.h"\r\n#include <cstring>\r\n#include <mbstring.h>\r\n#include <utility>\r\n'+raw
        once(b'\tZeroMemory( &m_pMapInfo, sizeof( MAP_INFO ) * MAX_MAP );',b'\tm_localMap455.clear();\r\n\tm_areaLabel455[0] = 0;\r\n\tm_areaLabelMap455 = 0xffffffffu;\r\n\tm_areaNoticeStart455 = 0;\r\n\tm_maps455 = RF455MapData{};\r\n\tm_pMapInfo = nullptr;')
        begin,end=section(raw,b'CLand::LoadData(',b'CLand::LoadData(')
        raw=raw[:begin]+b'''CLand::LoadData(void){
    char localized[260];std::sprintf(localized,"%s/NDMap.edf",RF455_GetClientDataRoot());
    RF455MapData next;
    m_mapLoad455=RF455_LoadMapData(next,"./DataTable/Map.edf",localized);
    if(m_mapLoad455!=RF455MapLoad::Complete && m_mapLoad455!=RF455MapLoad::BaseOnly)return FALSE;
    auto* window = _GetMinimapWindow();
    if (window) {
        if (window->IsWorldMap455()) window->Close();
        window->ResetLocalMapLabels455();
    }
    SetAreaLabel455(nullptr);
    m_localMap455.clear();
    m_maps455 = std::move(next);
    m_pMapInfo=m_maps455.maps.get();m_byMaxMapNum=m_maps455.count;
    m_localMap455.select(m_maps455, m_byMapIndex);
    RF455_ObserveProtocol("map-catalog",m_maps455.count,m_maps455.localizedCount,
                          static_cast<unsigned>(m_maps455.localizationStatus));
    return TRUE;
}'''+raw[end:]
        raw=patch_method(raw,section,b'CLand',b'OpenMinimapWindow',lambda _:b'''CLand::OpenMapItem455(const char* name)
{
    auto* window = _GetMinimapWindow();
    const auto* map = RF455_FindMapByName(m_maps455, name);
    if (!window || !map) return false;
    const auto code = map->byIndex;
    if (code >= 0xff || code >= m_maps455.count || &m_maps455.maps[code] != map) return false;
    const auto index = static_cast<BYTE>(code);

    // RVA 0x3C9140 toggles when the requested local map is already selected.
    const auto showingSelected = [&] {
        return !window->IsWorldMap455() && window->GetMiniMapIndex() == index;
    };
    if (showingSelected() && window->IsShow()) {
        window->Close();
        return true;
    }
    if (!showingSelected() || !_GetUISpriteMgr() || !_GetUISpriteMgr()->GetSprite(SP_ID_MINIMAP)) {
        UI_SetMinimap(index);
        if (!showingSelected() || !_GetUISpriteMgr() || !_GetUISpriteMgr()->GetSprite(SP_ID_MINIMAP))
            return false;
    }
    window->Open();
    return true;
}''')
        once(b'void\nCLand::OpenMapItem455(',b'bool\nCLand::OpenMapItem455(')
        # Public real-provider path used by ordinary UI_SetMinimap and focused lab.
        # Existing UI reset/sprite/object creation remains a separate open port.
        raw+=b'''
void CLand::ReceiveAreaLabel455(DWORD catalogIndex, WORD ordinal)
{
    const auto* label = RF455_FindLocalMapLabel(m_maps455, catalogIndex, ordinal);
    if (label) SetAreaLabel455(label, catalogIndex);
}

void CLand::SetMapIndex(BYTE index)
{
    if (m_byMapIndex != index) {
        if (auto* window = _GetMinimapWindow()) window->ResetLocalMapLabels455();
        if (m_areaLabelMap455 != index) SetAreaLabel455(nullptr);
    }
    m_byMapIndex = index;
    m_localMap455.select(m_maps455, index);
}

bool CLand::ApplyMiniMapGeometry455(BYTE index){
    auto* window=_GetMinimapWindow();if(!window)return false;
    if(index==0xff)index=m_byMapIndex;
    if(!m_pMapInfo||index>=m_byMaxMapNum||!m_pLevel||!m_pLevel->mBsp||!m_pLevel->mBsp->mNode)return false;
    const auto& node=m_pLevel->mBsp->mNode[1];RECT bounds={node.bb_min[0],node.bb_min[2],node.bb_max[0],node.bb_max[2]};
    window->SetMapBound(bounds);const auto& row=m_pMapInfo[index];
    window->SetNuclearMapGeometry455(row.miniMapWidth,row.miniMapHeight,row.miniMapX,row.miniMapY);return true;
}

void CLand::ToggleCurrentMinimap455()
{
    auto* window = _GetMinimapWindow();
    if (!window) return;
    if (window->IsShow()) {
        window->Close();
        return;
    }
    // Transport01 uses a separate transit map. The three dungeon maps have no map window.
    if (m_byMapIndex == 14 || m_byMapIndex == 15 || m_byMapIndex == 16 || m_byMapIndex == 23)
        return;
    if (!window->IsCurrentMapBound455(m_byMapIndex)) UI_SetMinimap(m_byMapIndex);
    if (window->IsCurrentMapBound455(m_byMapIndex)) window->Open();
}

void CLand::ShowMapLabel455(const char* label)
{
    auto* window = _GetMinimapWindow();
    if (!label || !*label || !window || !m_pMapInfo) return;
    for (DWORD i = 0; i < m_byMaxMapNum; ++i) {
        if (_mbsicmp(reinterpret_cast<const unsigned char*>(m_pMapInfo[i].pName_UI),
                     reinterpret_cast<const unsigned char*>(label))) continue;
        if (i >= 0xff) return;
        const auto index = static_cast<BYTE>(i);
        UI_SetMinimap(index);
        if (!window->IsWorldMap455() && window->GetMiniMapIndex() == index) window->Open();
        return;
    }
}
'''
        # Keep one production provider for this exact pair of confirmed calls.
        start=raw.index(b'CLand::UI_SetMinimap(')
        b=raw.index(b'\tRECT l_rectMap;',start);e=raw.index(b'\t_GetMinimapWindow()->SetMapIndex(',b)
        raw=raw[:b]+b'\tif(!ApplyMiniMapGeometry455(pi_byMapIndex))return;\r\n'+raw[e:]
        unload = b'\t_GetUISpriteMgr()->UnloadSprite( SP_ID_MINIMAP );'
        load = b'\t_GetUISpriteMgr()->LoadSprite( SP_ID_MINIMAP, m_pMapInfo[pi_byMapIndex].pMinimapFileName );'
        newline = b'\r\n' if unload + b'\r\n' + load in raw else b'\n'
        once(unload + newline + load, b'''    const auto* level = GetLevel();
    if (!m_pMapInfo || pi_byMapIndex >= m_byMaxMapNum || !level || !level->mBsp ||
        !level->mBsp->mNode || !GetD3dDevice() || !_GetUISpriteMgr()) return;
    const auto& map = m_pMapInfo[pi_byMapIndex];
    if (map.miniMapWidth <= 0 || map.miniMapHeight <= 0 ||
        !_GetUISpriteMgr()->LoadMinimapSprite455(map.pMinimapFileName)) return;''')
        once(b'\t_GetMinimapWindow()->Init();', b'''    _GetMinimapWindow()->ResetWorldMap455();
    _GetMinimapWindow()->Init();''')
        source=Path(__file__).with_name('native')/'client455_area_notice.inc'
        return raw+b'\r\n'+source.read_bytes(),True
    if relative=='gameprogress/cgp_maingame.cpp':
        once(b'\t\t_GetUIScreen()->Draw();',
             b'\t\t_GetLand()->DrawAreaNotice455();\r\n\t\t_GetUIScreen()->Draw();')
        check = b'\tif( _GetMinimapWindow() && _GetMinimapWindow()->GetMiniMapIndex() != 0xFF )'
        load = b'\t\t_GetUISpriteMgr()->LoadSprite( SP_ID_MINIMAP, _GetLand()->GetMapInfo( _GetMinimapWindow()->GetMiniMapIndex() )->pMinimapFileName );'
        newline = b'\r\n' if check + b'\r\n' + load in raw else b'\n'
        once(check + newline + load,
             b'''    auto* minimap = _GetMinimapWindow();
    const auto* land = _GetLand();
    if (minimap && land && !minimap->IsWorldMap455()) {
        const auto index = minimap->GetMiniMapIndex();
        const auto& catalog = land->MapData455();
        if (index != 0xff && catalog.maps && index < catalog.count)
            _GetUISpriteMgr()->LoadMinimapSprite455(catalog.maps[index].pMinimapFileName);
    }''')
        return raw,True
    if relative=='gameprogress/cinputprocessmgr.cpp':
        return patch_method(raw, section, b'CInputProcessMgr', b'InputProcess_Keyboard_OpenMinimapWindow', lambda _: b'''CInputProcessMgr::InputProcess_Keyboard_OpenMinimapWindow(void)
{
    if (!IsPressedKey(KM_WINDOW_MINIMAP)) return FALSE;
    if (auto* land = _GetLand()) land->ToggleCurrentMinimap455();
    return TRUE;
}'''), True
    if relative=='gameobject/board/itemboard/cinventoryboard.cpp':
        raw=b'#include "client455_item_payloads.h"\n'+raw

        def use_map(body):
            start=body.index(b'\n{')+2
            body=body[:start]+b'''
    auto* mapBoards = _GetGBM();
    auto* sourceObject = mapBoards->GetOrgObject();
    auto* mapItem = sourceObject ? dynamic_cast<RF455BasicItem*>(sourceObject->GetItem455()) : nullptr;
    if (mapItem && mapItem->header().kind == 0) {
        const auto row = mapItem->rawData();
        if (row.data && row.size > 88 && row.data[88] == IEPT_MAP) {
            // RVA 0x079090 reads the immutable map code name from Item +152.
            constexpr std::size_t nameOffset = 152, nameBytes = 32;
            const char* name = row.size >= nameOffset + nameBytes
                ? reinterpret_cast<const char*>(row.data + nameOffset) : nullptr;
            auto* land = _GetLand();
            const bool opened = land && !mapItem->header().flag21 && name &&
                std::memchr(name, 0, nameBytes) && land->OpenMapItem455(name);
            mapBoards->ClearOperation();
            return opened;
        }
    }
'''+body[start:]
            return replace(body, b'if( pMapData )\n\t\t\t\t\t_GetLand()->OpenMinimapWindow( pMapData->GetMapName(), pMapData->GetName() );',
                           b'''auto* land = _GetLand();
                const bool opened = pMapData && land && land->OpenMapItem455(pMapData->GetMapName());
                _GetGBM()->ClearOperation();
                return opened;''')

        return patch_method(raw,section,b'CInventoryBoard',b'UI_UseRequest_ProcessObject',use_map),True
    if relative=='userinterface/gamewindow/etcwin/guiminimapwindow.h':
        raw=b'#include "client455_map_data.h"\r\n#include <string>\r\n'+raw
        once(b'\tvoid InitOpacity455();',b'''    void InitOpacity455();
    CGUIButton m_worldMapButton455;
    CGUIObject m_worldMapSurface455;
    RF455MapHitMask m_worldMapMask455;
    std::string m_worldMapName455;
    unsigned m_worldMapDepth455 = 0;
    POINT m_localMapPosition455{};
    POINT m_localMapSize455{};
    std::string m_localMapTooltip455;
    struct LocalMapLabel455 {
        std::string text;
        std::int32_t x, y;
        LONG width;
    };
    std::vector<LocalMapLabel455> m_localLabels455;
    bool m_localLabelsPrepared455 = false;
    void PrepareLocalMapLabels455(const RF455LocalMapLayer&);
    void DrawLocalMapLabels455();
    void ClearLocalMapTooltip455();
    void UpdateLocalMapTooltip455(LONG x, LONG y);
    void HandleLocalMapMouse455(_mouse_event&);
    int m_worldMapHover455 = -1;
    bool SelectWorldMap455(const RF455MapLayer&, unsigned depth);
    bool HandleWorldMapMouse455(_mouse_event&);
    void BindWorldMapSprite455();
    void DrawWorldMapLabels455();
    void LayoutWorldMap455();
    void UpdateWorldMapHover455(LONG x, LONG y);
    std::vector<POINT> m_worldLabelSizes455;
    std::vector<bool> m_worldLabelEnabled455;
public:
    bool IsWorldMap455() const { return !m_worldMapName455.empty(); }
    void ResetLocalMapLabels455();
    void ResetWorldMap455();
    void Close() override;
    void MouseMotionEvent(_mouse_motion_event& event) override;
private:''')
        return raw,True
    if relative=='userinterface/gamewindow/etcwin/guiminimapwindow.cpp':
        begin,end=section(raw,b'CGUIMiniMapWindow::SetMapIndex(',b'CGUIMiniMapWindow::SetMapIndex(');body=raw[begin:end]
        a=body.index(b'\tif( m_byMapIndex > 7 )');b=body.index(b'\tif( m_byMapIndex == m_byMiniMapIndex )',a)
        body=body[:a]+b'\t// Dimensions/offset are supplied by the actual map record,not legacy8map tables.\r\n\tm_ptCutSize.x=-m_nuclearMapOffset455.x;m_ptCutSize.y=-m_nuclearMapOffset455.y;\r\n'+body[b:]
        at=body.index(b'{')+1
        body=body[:at]+b'\r\n\tif (m_byMapIndex != pi_byMapIndex || m_byMiniMapIndex != pi_byMiniMapIndex) ResetLocalMapLabels455();'+body[at:]
        raw=raw[:begin]+body+raw[end:]
        raw=b'#include "cland.h"\r\n#include "client455_font.h"\r\n#include "client455_language.h"\r\n#include "client455_text_metrics.h"\r\n#include "r3text.h"\r\n#include <algorithm>\r\n#include <cstring>\r\n#include <mbstring.h>\r\n#include <utility>\r\nextern CLand* g_pLand;\r\n'+raw
        once(b'CGUIWindow::MouseEvent( event );', b'''if (HandleWorldMapMouse455(event)) return;
    HandleLocalMapMouse455(event);
    CGUIWindow::MouseEvent( event );''')
        source=Path(__file__).with_name('native')/'client455_world_map_owner.inc'
        return raw+b'\r\n'+source.read_bytes(),True
    return raw,False
