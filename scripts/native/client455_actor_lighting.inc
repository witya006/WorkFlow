void CResObject::SetLightColorFromMap(){
    //7CE7A0:map color first;after-image takes priority over explicit blink color.
    ZeroMemory(&m_d3dLight,sizeof(m_d3dLight));
    ZeroMemory(&m_d3dMaterial,sizeof(m_d3dMaterial));
    DWORD color=0;bool defined=false;
    Vector3f position={m_vecPos[0],m_vecPos[1],m_vecPos[2]};
    if(_GetLevel()&&_GetLevel()->IsLoadedBsp()){
        color=_GetLevel()->mBsp->GetLightFromPoint(position,2);defined=true;
    }
    if(IsEnable(ROSF_AFTER_IMAGE_OF_OBJECT)){color=0xffa0a0ff;defined=true;}
    else if(m_bIsBlink){color=m_dwBlinkColor455;defined=true;}
    //The target reads an uninitialised local without BSP or either override.
    //Do not invent a white-light fallback for this still-unaccepted domain.
    if(!defined)throw std::logic_error("455 actor map light requires loaded BSP or explicit color override");
    ::GetMatLightFromColor(&m_d3dLight,&m_d3dMaterial,color,1.0f);
    m_d3dLight.Direction.x=-m_d3dLight.Direction.x;
    m_d3dLight.Direction.y=-m_d3dLight.Direction.y;
    m_d3dLight.Direction.z=-m_d3dLight.Direction.z;
    m_d3dLight.Ambient.r=m_d3dLight.Ambient.g=m_d3dLight.Ambient.b=1.0f;
    m_d3dMaterial.Diffuse.r+=.15f;
    m_d3dMaterial.Diffuse.g+=.1f;m_d3dMaterial.Diffuse.b+=.1f;
    m_d3dMaterial.Ambient.r+=.2f;m_d3dMaterial.Ambient.g+=.2f;m_d3dMaterial.Ambient.b+=.2f;
    m_d3dMaterial.Specular.r=m_d3dMaterial.Diffuse.r*.3f;
    m_d3dMaterial.Specular.g=m_d3dMaterial.Diffuse.g*.3f;
    m_d3dMaterial.Specular.b=m_d3dMaterial.Diffuse.b*.3f;
    m_d3dMaterial.Specular.a=1.0f;m_d3dMaterial.Power=10.0f;
    _GetCharIF()->SetLight(m_d3dLight);
}

void CResObject::SetBlink455(BOOL enabled,DWORD color){
    //7CEA00 stores both full-width fields,including color when disabling.
    m_bIsBlink=enabled;m_dwBlinkColor455=color;
}
