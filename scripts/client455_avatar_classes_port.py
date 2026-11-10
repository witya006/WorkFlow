"""Connect455class index/name writers without reusing legacy Level/Guild slots."""
def port_avatar_classes(raw,relative,section,native):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Avatar class anchor '+relative+':'+repr(old))
        raw=raw.replace(old,new)
    if relative=='character/avatar/cavatar.h':
        once(b'void\t\tSetClassName( char * pi_pClassName );',b'''void\t\tSetClassName( char * pi_pClassName );
    void RefreshClassNames455(BYTE slot,bool stringSetter);
    void SetPrimaryClassName455(DWORD index);
    void SetAdvancedClassName455(DWORD index);
    DWORD GetInitialClassIndex455()const{return m_dwClassDTIndex[1]==ID_INVALID?m_dwClassDTIndex[0]:m_dwClassDTIndex[1];}''')
        return raw,True
    if relative=='userinterface/gamewindow/guicharinfowindow.h':
        once(b'CGUIText\t\t\tm_uiTitle;',b'''//455value widgets have their own indices. Legacy Level/Guild remain
    //legacy fields;full455window placement/rendering is still pending.
    CGUIText m_uiInfoValues455[23];
    void SetInfoText455(BYTE slot,char* text){if(slot<23)m_uiInfoValues455[slot].SetString(text);}
    CGUIText* GetInfoValue455(BYTE slot){return slot<23?&m_uiInfoValues455[slot]:NULL;}
    CGUIText\t\t\tm_uiTitle;''')
        return raw,True
    if relative!='character/avatar/cavatar_etc.cpp':return raw,False
    raw=b'#include <cstring>\n'+raw
    def edit(sig,body):
        nonlocal raw
        first,last=section(raw,sig,sig);raw=raw[:first]+body+raw[last:]
    edit(b'CAvatar::SetClassDTIndex( BYTE pi_byOrderNo, DWORD pi_dwDTIndex )',b'''CAvatar::SetClassDTIndex( BYTE pi_byOrderNo, DWORD pi_dwDTIndex ){
        if(pi_byOrderNo>=4)return;
        m_dwClassDTIndex[pi_byOrderNo]=pi_dwDTIndex;
        if(_GetSkillBoard())_GetSkillBoard()->CreateClassSkill(m_dwClassDTIndex[pi_byOrderNo]);
        RefreshClassNames455(pi_byOrderNo,false);
    }''')
    edit(b'CAvatar::SetClassDTIndexByStrDTCode( BYTE pi_byOrderNo, char * pi_strDTCode )',b'''CAvatar::SetClassDTIndexByStrDTCode( BYTE pi_byOrderNo, char * pi_strDTCode ){
        if(pi_byOrderNo>=4||!pi_strDTCode)return;
        const auto row=_GetCharDataMgr()->GetClassData455(pi_strDTCode);if(!row.data)return;
        DWORD index;std::memcpy(&index,row.data+4,4);m_dwClassDTIndex[pi_byOrderNo]=index;
        if(_GetSkillBoard())_GetSkillBoard()->CreateClassSkill(m_dwClassDTIndex[pi_byOrderNo]);
        RefreshClassNames455(pi_byOrderNo,true);
    }''')
    edit(b'CAvatar::SetClassName( char * pi_pClassName )',b'''CAvatar::SetClassName( char * pi_pClassName ){
        if(!pi_pClassName||!_GetCharInfoWindow())return;
        const std::size_t length=std::strlen(pi_pClassName)+1;
        std::memset(m_pClassName,0,32);std::memcpy(m_pClassName,pi_pClassName,length>=32?31:length);
        _GetCharInfoWindow()->SetInfoText455(5,m_pClassName);
    }''')
    raw+=b'\n'+(native/'client455_avatar_classes.inc').read_bytes()
    return raw,True
