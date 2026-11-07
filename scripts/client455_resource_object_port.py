"""Exact selected common-object layout/lifecycle migration in owned source copies."""

def port_resource_object(raw,relative,native,section):
    def once(old,new):
        nonlocal raw
        if raw.count(old)!=1:raise ValueError('Resource-object source anchor changed:'+relative+':'+repr(old))
        raw=raw.replace(old,new)
    changed=False
    if relative=='cobject.h':
        once(b'm_pName[MAX_NAME_LENGTH]',b'm_pName[64]')
        once(b'\tCObject();',b'\tCObject();\r\n\tCObject(const CObject&);')
        once(b'\tvirtual ~CObject();',b'\tvirtual ~CObject();\r\n\tvirtual void Clear(){SetEmpty();}')
        once(b'_strcpy( m_pName, pi_pName );',b'_strcpy( m_pName, pi_pName, sizeof(m_pName) );')
        changed=True
    elif relative=='cobject.cpp':
        raw+=b'\r\n'+(native/'client455_object_copy.inc').read_bytes();changed=True
    elif relative=='cresobject.h':
        once(b'\tCResObject();',b'\tCResObject();\r\n\tCResObject(const CResObject&);')
        # Preserve every legacy byte/comment except the selected declarations.
        lines=raw.splitlines(keepends=True)
        scale=next(i for i,line in enumerate(lines) if b'\tm_fScale;' in line)
        lines.insert(scale+1,b'\tDWORD m_dwCreatedTime455; //7CCFA0 field244\r\n')
        color=next(line for line in lines if b'\tm_dwTextColor;' in line)
        lines=[line for line in lines if line!=color and b'\tm_dwPrevBlinkTime;' not in line and b'\tm_dwCurBlinkTime;' not in line]
        hide=next(i for i,line in enumerate(lines) if b'\tm_bIsHide;' in line);lines.insert(hide+1,color)
        effect=next(i for i,line in enumerate(lines) if b'\tm_dwEffectID[2];' in line)
        lines.insert(effect+1,b'\tunsigned char m_secondaryState455[84]; //91C490 defaults,full use remains open\r\n')
        raw=b''.join(lines);changed=True
    elif relative=='cresobject.cpp':
        first,last=section(raw,b'CResObject::CResObject(',b'CResObject::CResObject(')
        raw=raw[:first]+(native/'client455_resource_object_ctor.inc').read_bytes()+raw[last:]
        #7CD390 passes the64-byte object name directly. Remove the obsolete
        #32-byte formatting buffer from the migrated caller.
        first,last=section(raw,b'CResObject::RenderName(',b'CResObject::RenderName(')
        body=raw[first:last]
        for line in [b'char l_pBuf[32];',b'sprintf( l_pBuf, "%s", m_pName );']:
            if body.count(line)!=1:raise ValueError('Resource RenderName buffer changed')
            body=body.replace(line,b'')
        raw=raw[:first]+body.replace(b'l_pBuf',b'm_pName')+raw[last:]
        for name in [b'Enable',b'Disable']:
            first,last=section(raw,b'CResObject::'+name+b'(',b'CResObject::'+name+b'(')
            body=b'CResObject::'+name+b'(DWORD flags){\r\n\tassert(flags!=ROSF_INVALID);\r\n'
            body+=b'\tm_dwStatusFlag '+(b'|= flags;' if name==b'Enable' else b'&= ~flags;')+b'\r\n'
            if name==b'Enable':body+=b'\tif(m_dwStatusFlag&ROSF_OUT_OF_VISUAL_FIELD_SERVER)SetReceiveFixPositionMsg(FALSE);\r\n'
            body+=b'\tif((m_dwStatusFlag&(ROSF_OUT_OF_VISUAL_FIELD_CLIENT|ROSF_CLIPPED))||!(m_dwStatusFlag&ROSF_RENDER_MESH))DeleteEffectID();\r\n}'
            raw=raw[:first]+body+raw[last:]
        raw+=b'\r\n'+(native/'client455_resource_object_copy.inc').read_bytes();changed=True
    return raw,changed
