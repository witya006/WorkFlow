"""Port actual typed icon index/grade-frame drawing without renumbering old UI."""
def port_item_icon(raw,relative,native,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Icon source anchor changed:'+relative+':'+repr(old))
        raw=raw.replace(old,new)
    changed=False
    if relative=='userinterface/guicontroller/guiitem.h':
        once(b'\tCGUIItem();',b'\tCGUIItem();\r\n'+(native/'client455_item_icon_members.inc').read_bytes());changed=True
    elif relative=='userinterface/guicontroller/guiitem.cpp':
        begin,end=section(raw,b'CGUIItem::SetSprite( void )',b'CGUIItem::SetSprite( void )');body=raw[begin:end];at=body.index(b'{')+1
        raw=raw[:begin]+body[:at]+b'\r\n\tif(m_typedIcon455){SetTypedSprite455();return;}'+body[at:]+raw[end:]
        for signature in [b'CGUIItem::Draw( void )',b'CGUIItem::Draw( RECT & pi_rtClipping )']:
            begin,end=section(raw,signature,signature);body=raw[begin:end];at=body.index(b'{')+1
            call=b'\r\n\tif(m_typedIcon455)return DrawTypedIcon455('+ (b'nullptr' if b'void' in signature else b'&pi_rtClipping')+b');'
            raw=raw[:begin]+body[:at]+call+body[at:]+raw[end:]
        begin,end=section(raw,b'CGUIItem::SetData(',b'CGUIItem::SetData(');body=raw[begin:end]
        body=body[:-1]+b'\r\n\tm_objectIndex455=pi_pItem->m_objectIndex455;m_grade455=pi_pItem->m_grade455;m_typedIcon455=pi_pItem->m_typedIcon455;\r\n\tm_gradeFrameVisible455=pi_pItem->m_gradeFrameVisible455;m_gradeFrame455=pi_pItem->m_gradeFrame455;\r\n}'
        raw=raw[:begin]+body+raw[end:];changed=True
    elif relative=='userinterface/spritemgr.h':
        once(b'\tCSpriteUnitList\t\tm_listSpriteUnit;',b'\tCSpriteUnitList\t\tm_listSpriteUnit;\r\n\tCSprite* m_targetSprites455[55]={};')
        once(b'\tCSpriteMgr();',b'\tCSpriteMgr();\r\n\tCSprite* GetTargetSprite455(unsigned id);\r\n\tvoid UnloadTargetSprites455();\r\n\tBOOL GetTargetSpriteInfo455(BYTE,DWORD,DWORD,int,SPRITE_INFO&);');changed=True
    elif relative=='userinterface/spritemgr.cpp':
        raw=b'#include <io.h>\r\n'+raw
        begin,end=section(raw,b'CSpriteMgr::UnloadSpriteAll(',b'CSpriteMgr::UnloadSpriteAll(');body=raw[begin:end];at=body.index(b'{')+1
        raw=raw[:begin]+body[:at]+b'\r\n\tUnloadTargetSprites455();'+body[at:]+raw[end:]
        raw+=b'\r\n'+(native/'client455_target_sprites.inc').read_bytes();changed=True
    return raw,changed
