"""Replace obsolete bounded map records/reader and supply real minimap geometry."""
import re
from client455_trade_ore_port import patch_method


def port_map_data(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Map data anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='cland.h':
        raw=b'#include "client455_map_data.h"\r\n'+raw
        begin=raw.index(b'struct MINE_INFO');end=raw.index(b'};',raw.index(b'struct MAP_INFO',begin))+2
        raw=raw[:begin]+b'using MINE_INFO=RF455MineInfo;\r\nusing MAP_AREA_INFO=RF455MapAreaInfo;\r\nusing MAP_INFO=RF455MapInfo;'+raw[end:]
        once(b'\tMAP_INFO\tm_pMapInfo[MAX_MAP];',b'\tRF455MapData m_maps455;\r\n\tMAP_INFO* m_pMapInfo=nullptr;')
        raw,n=re.subn(rb'BYTE(\s+m_byMaxMapNum;)',rb'DWORD\1',raw)
        if n!=1:raise ValueError('Map count member')
        once(b'\tBOOL\tLoadData( void );',b'\tBOOL\tLoadData( void );\r\n\tvoid ToggleCurrentMinimap455();\r\n\tbool ApplyMiniMapGeometry455(BYTE index);\r\n\tconst RF455MapData& MapData455()const{return m_maps455;}\r\n\tRF455MapLoad MapLoadStatus455()const{return m_mapLoad455;}\r\nprivate:\r\n\tRF455MapLoad m_mapLoad455=RF455MapLoad::MissingInput;\r\npublic:')
        return raw,True
    if relative=='cland.cpp':
        raw=b'#include "client455_nation_paths.h"\r\n#include "client455_protocol_observation.h"\r\n#include <io.h>\r\n'+raw
        once(b'\tZeroMemory( &m_pMapInfo, sizeof( MAP_INFO ) * MAX_MAP );',b'\tm_maps455=RF455MapData{};m_pMapInfo=nullptr;')
        begin,end=section(raw,b'CLand::LoadData(',b'CLand::LoadData(')
        raw=raw[:begin]+b'''CLand::LoadData(void){
    char localized[260];std::sprintf(localized,"%s/NDMap.edf",RF455_GetClientDataRoot());
    m_mapLoad455=RF455_LoadMapData(m_maps455,"./DataTable/Map.edf",localized);
    if(m_mapLoad455!=RF455MapLoad::Complete && m_mapLoad455!=RF455MapLoad::BaseOnly)return FALSE;
    m_pMapInfo=m_maps455.maps.get();m_byMaxMapNum=m_maps455.count;
    RF455_ObserveProtocol("map-catalog",m_maps455.count,m_maps455.localizedCount,
                          static_cast<unsigned>(m_maps455.localizationStatus));
    return TRUE;
}'''+raw[end:]
        # Public real-provider path used by ordinary UI_SetMinimap and focused lab.
        # Existing UI reset/sprite/object creation remains a separate open port.
        raw+=b'''
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
'''
        # Keep one production provider for this exact pair of confirmed calls.
        start=raw.index(b'CLand::UI_SetMinimap(')
        b=raw.index(b'\tRECT l_rectMap;',start);e=raw.index(b'\t_GetMinimapWindow()->SetMapIndex(',b)
        raw=raw[:b]+b'\tif(!ApplyMiniMapGeometry455(pi_byMapIndex))return;\r\n'+raw[e:]
        once(b'\t_GetUISpriteMgr()->UnloadSprite( SP_ID_MINIMAP );', b'''    const auto* level = GetLevel();
    if (!m_pMapInfo || pi_byMapIndex >= m_byMaxMapNum || !level || !level->mBsp ||
        !level->mBsp->mNode || !GetD3dDevice() || !_GetUISpriteMgr()) return;
    const auto& map = m_pMapInfo[pi_byMapIndex];
    if (map.miniMapWidth <= 0 || map.miniMapHeight <= 0 || _access(map.pMinimapFileName, 0) != 0) return;
    _GetUISpriteMgr()->UnloadSprite( SP_ID_MINIMAP );''')
        once(b'\t\t\t_GetMinimapWindow()->Open();', b'''            if (_GetMinimapWindow()->GetMiniMapIndex() == m_pMapInfo[i].byIndex)
                _GetMinimapWindow()->Open();''')
        return raw,True
    if relative=='gameprogress/cinputprocessmgr.cpp':
        return patch_method(raw, section, b'CInputProcessMgr', b'InputProcess_Keyboard_OpenMinimapWindow', lambda _: b'''CInputProcessMgr::InputProcess_Keyboard_OpenMinimapWindow(void)
{
    if (!IsPressedKey(KM_WINDOW_MINIMAP)) return FALSE;
    if (auto* land = _GetLand()) land->ToggleCurrentMinimap455();
    return TRUE;
}'''), True
    if relative=='userinterface/gamewindow/etcwin/guiminimapwindow.cpp':
        begin,end=section(raw,b'CGUIMiniMapWindow::SetMapIndex(',b'CGUIMiniMapWindow::SetMapIndex(');body=raw[begin:end]
        a=body.index(b'\tif( m_byMapIndex > 7 )');b=body.index(b'\tif( m_byMapIndex == m_byMiniMapIndex )',a)
        body=body[:a]+b'\t// Dimensions/offset are supplied by the actual map record,not legacy8map tables.\r\n\tm_ptCutSize.x=-m_nuclearMapOffset455.x;m_ptCutSize.y=-m_nuclearMapOffset455.y;\r\n'+body[b:]
        raw=raw[:begin]+body+raw[end:];return raw,True
    return raw,False
