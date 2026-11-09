"""Restore actual MiniMap-owned marker children and confirmed UI operations."""


def port_nuclear_minimap(raw,relative,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Nuclear MiniMap anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='userinterface/gamewindow/etcwin/guiminimapwindow.h':
        raw=b'#include "client455_nuclear_minimap.h"\r\n'+raw
        once(b'\tCGUIScrollbarEX m_opacityScrollbar455;',b'\tCGUINuclearBomb455 m_nuclearMarkers455[3];\r\n\tPOINT m_nuclearMapOffset455={};\r\n\tvoid InitNuclearMarkers455();\r\n\tvoid ReleaseNuclearMarkers455();\r\n\tCGUIScrollbarEX m_opacityScrollbar455;')
        once(b'\tvoid ScrollEvent(_scroll_event& event);',b'\tvoid SetNuclearMapGeometry455(LONG width,LONG height,LONG x,LONG y);\r\n\tvoid SetNuclearMarker455(BYTE index,BOOL show,const float* foundPosition);\r\n\tCGUINuclearBomb455& NuclearMarker455(BYTE index);\r\n\tvoid ScrollEvent(_scroll_event& event);')
        return raw,True
    if relative=='userinterface/gamewindow/etcwin/guiminimapwindow.cpp':
        once(b'\tInitOpacity455();',b'\tInitOpacity455();\r\n\tInitNuclearMarkers455();')
        once(b'\tm_frameSkin455.ReleaseSprite();',b'\tReleaseNuclearMarkers455();\r\n\tm_frameSkin455.ReleaseSprite();')
        begin,end=section(raw,b'CGUIMiniMapWindow::SetMapBound(',b'CGUIMiniMapWindow::SetMapBound(');body=raw[begin:end]
        if body.count(b'SetPixelPerMeter();')!=1:raise ValueError('MiniMap bounds scale boundary')
        body=body.replace(b'SetPixelPerMeter();',b'SetPixelPerMeter();\r\n\tfor(auto& marker:m_nuclearMarkers455)marker.SetMapBound455(m_rtMapBound);');raw=raw[:begin]+body+raw[end:]
        return raw,True
    return raw,False
