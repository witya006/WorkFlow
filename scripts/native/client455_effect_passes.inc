void RenderOpaqueEffects455(){
    D3DXMATRIX identity;D3DXMatrixIdentity(&identity);GetD3dDevice()->SetTransform(D3DTS_WORLD,&identity);
    if(GetR3State()->mIsFog)GetD3dDevice()->SetRenderState(D3DRS_FOGENABLE,FALSE);
    for(DWORD i=0;i<stELcnt;++i){
        auto& effect=stEffectList[i];if(effect.mState==3||effect.mState==5)continue;
        if(effect.mFlag&0x4c4b400u){RenderCommonEffect(i);continue;}
        if(!(effect.mFlag&_MT_FLAG_PARTICLE)&&effect.mEntity->IsFirstAlpha())continue;
        if(effect.mFlag&0x32)continue;
        RenderCommonEffect(i);
    }
}
void RenderAlphaEffects455(){
    for(DWORD i=0;i<stELcnt;++i){
        auto& effect=stEffectList[i];if(effect.mFlag&0x4c4b400u)continue;
        if(effect.mState==3||effect.mState==5)continue;
        if(!(effect.mFlag&_MT_FLAG_PARTICLE)&&!effect.mEntity->IsFirstAlpha())continue;
        if(effect.mFlag&0x12)continue;
        RenderCommonEffect(i);
    }
    // Target does not apply the preceding state filters in its final fade pass.
    for(DWORD i=0;i<stELcnt;++i)if(stEffectList[i].mFlag&_MT_FLAG_ENTITY_FADE)RenderCommonEffect(i);
    if(GetR3State()->mIsFog)GetD3dDevice()->SetRenderState(D3DRS_FOGENABLE,TRUE);
}
void RenderAllEffectsList(){RenderOpaqueEffects455();RenderAlphaEffects455();}
