"""Own the icon registry in MainApp and route typed quantity/usable setters."""
import re
def port_icon_links(raw,relative):
    if relative=='mainapp.h':
        raw=b'#include "client455_icon_links.h"\r\n'+raw
        anchor=b'\tRF455ClientItems m_items455;'
        if raw.count(anchor)!=1:raise ValueError('Icon registry lifetime owner anchor')
        raw=raw.replace(anchor,b'\tRF455IconLinks m_iconLinks455;\r\n'+anchor)
        anchor=b'RF455ClientItems& Items455(){return m_items455;}'
        if raw.count(anchor)!=1:raise ValueError('Icon registry public owner anchor')
        raw=raw.replace(anchor,anchor+b'\r\n\tRF455IconLinks& IconLinks455(){return m_iconLinks455;}')
        return raw,True
    if relative=='userinterface/guicontroller/guiitem.h':
        for pattern,replacement in [
            (rb'\{\s*m_wNum\s*=\s*pi_wNum;\s*\}',b'{if(m_typedIcon455)SetNum455(pi_wNum);else m_wNum=pi_wNum;}'),
            (rb'\{\s*m_byUsable\s*=\s*pi_bUsable;\s*\}',b'{if(m_typedIcon455)SetUsable455(static_cast<BYTE>(pi_bUsable));else m_byUsable=pi_bUsable;}')]:
            raw,count=re.subn(pattern,replacement,raw)
            if count!=1:raise ValueError('Typed icon setter anchor changed:'+repr(pattern))
        return raw,True
    return raw,False
