void R3ClearFrameBuffer(){
    auto* device=GetD3dDevice();if(!device)return;
    //4558CDB20 has no legacy letterbox viewport mutation. Extra bloom targets
    // are tracked separately;this is its ordinary/main-effect target domain.
    if(stRealFullScreenEffectState)stRToTMain.ClearFrameBuffer();
    else device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,GetR3State()->mFogColor,1,0);
}
