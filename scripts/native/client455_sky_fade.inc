// Pinned4558B58A0/8B5900. State is owned by the original r3util TU.
void SetFadeSky(DWORD color,float fade_time) {
    stSkyFadeTime=-0.600100040435791015625f;
    stSkyFadeColor=color;
    stSkyStartTick=R3GetTime();
    stIsFadeInStart=FALSE;
    stAllSkyFadeTime=fade_time;
    stSkyFadeAlpha=0.0000001f;
}

BOOL DrawFadeSKy() {
    // The final active frame still draws alpha0. Only the next call exits.
    if(stSkyFadeAlpha==0)return TRUE;
    stAllSkyFadeTime=RF455_FadeSubtract(stAllSkyFadeTime,R3GetLoopTime());
    if(stSkyFadeTime>0) {
        const float tick=RF455_FadeTick(R3GetTime(),stSkyStartTick,stSkyFadeTime);
        if(tick>1) {stSkyFadeAlpha=0;stSkyFadeTime=0;}
        else stSkyFadeAlpha=RF455_FadeComplement(tick);
    } else if(stSkyFadeTime<0) {
        const float tick=RF455_FadeTick(R3GetTime(),stSkyStartTick,-stSkyFadeTime);
        if(tick>1) {stSkyFadeAlpha=1;stSkyFadeTime=0;}
        else stSkyFadeAlpha=tick;
    }
    if(!stIsFadeInStart && stAllSkyFadeTime<0.6f) {
        stIsFadeInStart=TRUE;
        stSkyFadeTime=0.600100040435791015625f;
        stSkyStartTick=R3GetTime();
    }
    SetFadeFactor(stSkyFadeColor,stSkyFadeAlpha);
    const DWORD color=GetColorToColorAlpha(GetFogColor(),stSkyFadeColor,stSkyFadeAlpha);
    GetD3dDevice()->SetRenderState(D3DRS_FOGCOLOR,color);
    const auto* state=GetR3State();
    const float start=RF455_FadeFog(state->mFogStart,6.0f,stSkyFadeAlpha);
    const float end=RF455_FadeFog(state->mFogEnd,600.0f,stSkyFadeAlpha);
    GetD3dDevice()->SetRenderState(D3DRS_FOGSTART,FtoDW(start));
    GetD3dDevice()->SetRenderState(D3DRS_FOGEND,FtoDW(end));
    return FALSE;
}
