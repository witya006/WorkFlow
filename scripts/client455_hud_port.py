"""Restore the upper gauge panel and radar artwork used by the 455 HUD."""
from client455_trade_ore_port import patch_method, remove_methods, replace


def port_hud(raw,relative,native,section):
    if relative == 'userinterface/gamewindow/etcwin/guiradarwindow.h':
        raw = replace(raw, b'\tvoid\tSetSprite( void );', b'''\tvoid\tSetSprite( void );
    void SetAreaLabel455(const char* label);
    void MouseEvent(_mouse_event& event) override;''')
        anchor = b'\tRADAR_CHAR_INFO\t* GetCharInfo( DWORD pi_dwID );'
        return replace(raw, anchor, b'''    CGUIButton m_openMap455;
    CGUIButton m_zoomIn455;
    CGUIButton m_zoomOut455;
    CGUIText m_areaLabel455;
    unsigned m_zoomLevel455 = 2;

''' + anchor), True
    if relative == 'cland.cpp':
        return patch_method(raw, section, b'CLand', b'UI_SetRadar', lambda _: b'''CLand::UI_SetRadar(void)
{
    if (auto* radar = _GetRadarWindow()) {
        radar->SetMapRotate(0.0f);
        radar->SetAreaLabel455(m_areaLabel455);
    }
}'''), True
    if relative=='userinterface/gamewindow/etcwin/guiradarwindow.cpp':
        owner = b'CGUIRadarWindow'
        raw = remove_methods(raw, section, owner, tuple((name, b'void') for name in (
            b'Init', b'SetSprite', b'UpdateCharPosition', b'SetViewedCharInRadarBoard',
            b'SetSprite_CharObj', b'SetSprite_CharDir',
        )))
        raw = patch_method(raw, section, owner, b'AddCharacter', lambda body: replace(
            body, b'\t\tl_pCharInfo->uiCharDir.SetSize( 11, 14 );\n', b''))
        return b'#include <cmath>\n#include <stdexcept>\n'+raw+b'\n'+(native/'client455_radar.inc').read_bytes(),True
    if relative=='userinterface/gamewindow/guigaugeexpwindow.h':
        raw=b'#include "client455_image_text.h"\n'+raw
        for old,new in [(b'MAX_GAUGE_NO\t3',b'MAX_GAUGE_NO\t4'),(b'\t\tSTAMINA_BAR',b'\t\tSTAMINA_BAR,\n\t\tFOURTH_BAR455')]:
            if raw.count(old)!=1:raise ValueError('HUD dimension/enum anchor')
            raw=raw.replace(old,new)
        old=b'\tBOOL\t\t\t\t\tm_bCreated;'
        if raw.count(old)!=1:raise ValueError('HUD member anchor')
        raw=raw.replace(old,old+b'\n'+(native/'client455_hud_members.inc').read_bytes())
        return raw,True
    if relative!='userinterface/gamewindow/guigaugeexpwindow.cpp':return raw,False
    for sig in [b'CGUIGaugeExpWindow::Init(',b'CGUIGaugeExpWindow::SetSprite(',b'CGUIGaugeExpWindow::SetGauge( Bar pi_eBar, DWORD pi_dwMaxGauge',b'CGUIGaugeExpWindow::SetGauge( Bar pi_eBar, DWORD pi_dwCurGauge',b'CGUIGaugeExpWindow::SetLevel(']:
        first,last=section(raw,sig,sig);start=raw.rfind(b'void',0,first)
        if raw[start:first].strip()!=b'void':raise ValueError('HUD return-type anchor')
        raw=raw[:start]+b'//455 implementation below.\n'+raw[last:]
    raw=b'#include <cstdio>\n#include <cstring>\n#include <stdexcept>\n'+raw
    return raw+b'\n'+(native/'client455_hud.inc').read_bytes(),True
