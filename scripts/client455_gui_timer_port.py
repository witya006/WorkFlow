"""Add the source-owned455 timer child to typed ordinary icons only."""
import re

def port_gui_timer(raw,relative,section):
    if relative=='userinterface/guicontroller/guiitem.h':
        anchor=b'#include "GUIObject.h"'
        if raw.count(anchor)!=1:raise ValueError('Timer header include anchor')
        raw=raw.replace(anchor,anchor+b'\r\n#include "client455_gui_timer.h"\r\n#include "client455_gui_animation.h"')
        raw,count=re.subn(rb'(BeginDelayAnimation\( DWORD pi_dwTime \)\s*)\{;\}',rb'\1{if(m_typedIcon455)BeginDelayAnimation455(pi_dwTime);}',raw)
        if count!=1:raise ValueError('Typed timer virtual entry anchor')
        raw,count=re.subn(rb'(IsDelayAnimation\( void \)\s*)\{ return m_uiDelay.IsStarted\(\); \}',rb'\1{ return m_typedIcon455?m_timer455.IsStarted455():m_uiDelay.IsStarted(); }',raw)
        if count!=1:raise ValueError('Typed derived timer query anchor')
        return raw,True
    if relative!='userinterface/guicontroller/guiitem.cpp':return raw,False
    def prepend(signature,statement):
        nonlocal raw
        begin,end=section(raw,signature,signature);body=raw[begin:end];at=body.index(b'{')+1
        raw=raw[:begin]+body[:at]+b'\r\n\t'+statement+body[at:]+raw[end:]
    prepend(b'CGUIItem::CGUIItem(',b'm_timer455.Show(TRUE);')
    begin,end=section(raw,b'CGUIItem::SetData(',b'CGUIItem::SetData(')
    raw=raw[:end-1]+b'\r\n\tif(m_typedIcon455){m_timer455=pi_pItem->m_timer455;m_readyCue455.ConfigureReady455();SetPos(m_ptPos.x,m_ptPos.y);}\r\n'+raw[end-1:]
    prepend(b'CGUIItem::SetEmpty(',b'if(m_typedIcon455){ResetTimerOnEmpty455();SetObjectIndex455(0xffffffff);SetItemID(0xffffffff);m_wNum=1;m_pRefItem=nullptr;m_gradeFrame455.SetARGB(0);return;}')
    prepend(b'CGUISFItem::BeginDelayAnimation(',b'if(m_typedIcon455){BeginDelayAnimation455(pi_dwTime);return;}')
    prepend(b'CGUISFItem::SetPos( LONG',b'if(m_typedIcon455){CGUIItem::SetPos(pi_nPosX,pi_nPosY);return;}')
    prepend(b'CGUISFItem::SetSize( LONG',b'if(m_typedIcon455){CGUIItem::SetSize(pi_nWidth,pi_nHeight);return;}')
    prepend(b'CGUISFItem::Draw( void )',b'if(m_typedIcon455)return CGUIItem::Draw();')
    prepend(b'CGUISFItem::Draw( RECT',b'if(m_typedIcon455)return CGUIItem::Draw(pi_rtClipping);')
    return raw,True
