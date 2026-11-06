// The ordinary legacy public text API now routes through the recovered455
// Unicode/GDI backend. These are source adapters,not original455C++ symbols.
void InitR3Text(){}
void ReleaseR3Text(){}
void R3LoadTextTexture(){RF455_LoadTextResources(GetD3dDevice(),GetR3State()->mAvailableTextureMem);}
void R3ReleaseTextTexture(){RF455_ReleaseTextResources();}
void DrawR3Hangul(LONG x,LONG y,char*text,DWORD color,DWORD flags){
    float position[]={static_cast<float>(x),static_cast<float>(y),0.99f,1};
    GetD3dDevice()->SetRenderState(D3DRS_ZENABLE,FALSE);
    RF455_DrawLegacyText(position,text,color,flags);
    GetD3dDevice()->SetRenderState(D3DRS_ZENABLE,TRUE);
}
void DrawR3Hangul3D(float position[4],char*text,DWORD color,DWORD flags){
    GetD3dDevice()->SetRenderState(D3DRS_ZENABLE,TRUE);
    RF455_DrawLegacyText(position,text,color,flags);
}
void DrawR3Hangul(LONG x,LONG y,char*text,DWORD color,float clip[2][2],DWORD flags){
    float position[]={static_cast<float>(x),static_cast<float>(y),0.99f,1};
    GetD3dDevice()->SetRenderState(D3DRS_ZENABLE,FALSE);
    RF455_DrawLegacyText(position,text,color,flags|0x80,&clip[0][0]);
    GetD3dDevice()->SetRenderState(D3DRS_ZENABLE,TRUE);
}
DWORD GetOutLineColor(){return RF455_GetTextOutline();}
void SetOutLineColor(DWORD color){RF455_SetTextOutline(color);}
