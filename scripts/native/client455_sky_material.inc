//9157E0:ordinary sky materials and their intentionally asymmetric cleanup masks.
void CSkyBox::DrawSkyBox(void* view_matrix){
    mEntity.PrepareAnimation();
    auto* device=GetD3dDevice();auto* state=GetR3State();
    if(state->mIsFog){
        device->SetRenderState(D3DRS_FOGENABLE,TRUE);
        device->SetRenderState(D3DRS_FOGCOLOR,state->mFogColor);
        device->SetRenderState(D3DRS_FOGSTART,FtoDW(state->mFogStart));
        device->SetRenderState(D3DRS_FOGEND,FtoDW(state->mFogEnd));
        device->SetRenderState(D3DRS_FOGTABLEMODE,D3DFOG_NONE);
        device->SetRenderState(D3DRS_FOGVERTEXMODE,D3DFOG_LINEAR);
        device->SetRenderState(D3DRS_RANGEFOGENABLE,state->mFogRangeEnable);
    }else device->SetRenderState(D3DRS_FOGENABLE,FALSE);
    if(state->mIsNoFogSky)device->SetRenderState(D3DRS_FOGENABLE,FALSE);
    if(!mIsSkyLoad){
        device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
        device->SetTransform(D3DTS_VIEW,static_cast<const D3DMATRIX*>(view_matrix));
        return;
    }
    if(RF455_GetSkyDayEnabled())RF455_DrawSkyAtmosphere();
    auto* view=static_cast<D3DMATRIX*>(view_matrix);D3DMATRIX saved;
    memcpy(&saved,view,sizeof(saved));view->_41=view->_42=view->_43=0;
    device->SetTransform(D3DTS_VIEW,view);
    device->SetRenderState(D3DRS_ZENABLE,FALSE);
    device->SetRenderState(D3DRS_ZWRITEENABLE,FALSE);
    SetVPIPTex1(mEntity.GetStaticVertexBuffer()->m_lpVertexBuffer,mEntity.GetStaticIndexedBuffer()->m_lpIndexBuffer);
    MultiTexOff();device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE2X);
    float world[4][4];auto* objects=mEntity.GetObject();auto* groups=mEntity.GetMatGroup();
    for(int i=0;i<mMatGroupNum;++i){
        const short index=mMatGroupSort[i];const auto& group=groups[index];
        GetObjectMatrix(world,group.ObjectId,objects,R3GetTime()*30.0f);
        device->SetTransform(D3DTS_WORLD,reinterpret_cast<D3DMATRIX*>(world));
        const DWORD flags=mEntity.mMat[group.MtlId].m_dwFlag;
        device->SetTextureStageState(0,D3DTSS_COLORARG2,(flags&4)?D3DTA_TFACTOR:D3DTA_DIFFUSE);
        device->SetTextureStageState(0,D3DTSS_COLOROP,(flags&4)?D3DTOP_MODULATE:D3DTOP_MODULATE2X);
        int alpha=255;
        if(flags&8)alpha=int(RF455_FadeAlphaByte(RF455_GetSkyNightWeight()));
        if(flags&0x10)alpha=255-int(RF455_FadeAlphaByte(RF455_GetSkyNightWeight()));
        if(flags&0x20)alpha=255-int(RF455_FadeAlphaByte(RF455_GetSkyNightWeight()));
        if(alpha){
            if(flags&0x1c){
                device->SetRenderState(D3DRS_TEXTUREFACTOR,(DWORD(alpha)<<24)|(state->mFogColor&0xffffff));
                device->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_TFACTOR);
                device->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATE);
                device->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE);
            }
            mEntity.DrawOneMatGroup(&mMatGroup[index]);
            if(flags&0x18)device->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);
        }
    }
    device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
    device->SetRenderState(D3DRS_ZENABLE,TRUE);
    device->SetRenderState(D3DRS_ZWRITEENABLE,TRUE);
    // Target restores device VIEW but leaves the caller's translation zeroed.
    device->SetTransform(D3DTS_VIEW,&saved);
}
