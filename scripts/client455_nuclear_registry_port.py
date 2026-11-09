"""Own the actual record registry and aiming member in one client container."""


def port_nuclear_registry(raw,relative):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Nuclear registry anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='mainapp.h':
        raw=b'#include "client455_nuclear_registry.h"\r\n'+raw
        once(b'RF455NuclearAiming m_nuclearAiming455;',b'RF455NuclearContainer m_nuclear455;')
        once(b'RF455NuclearAiming& NuclearAiming455(){return m_nuclearAiming455;}',b'RF455NuclearAiming& NuclearAiming455(){return m_nuclear455.Aiming();}\r\n\tRF455NuclearContainer& Nuclear455(){return m_nuclear455;}')
        return raw,True
    if relative=='mainapp.cpp':
        once(b'm_nuclearAiming455.Clear();',b'm_nuclear455.ClearAll();\r\n\tm_nuclear455.Aiming().Clear();')
        return raw,True
    if relative=='gameprogress/cgp_maingame.cpp':
        raw=b'#include "client455_nuclear_registry.h"\r\n'+raw
        once(b'RF455_NuclearAiming().FrameMove();',b'RF455_NuclearContainer().FrameMove();')
        return raw,True
    return raw,False
