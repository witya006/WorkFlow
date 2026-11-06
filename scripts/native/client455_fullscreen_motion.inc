if(stFullScreenEffectState&_FSE_MOTION_BLUR){
    // 4558CEB13..8CEC59 deliberately clears the CURRENT blur target and ends
    // with an opaque current-scene draw. Do not substitute a temporal blend.
    if(stRealFullScreenEffectState!=stOldRealFullScreenEffectState){
        stOldRealFullScreenEffectState=stRealFullScreenEffectState;
        Draw2DSprite(0,0,float(stTexSize),float(stTexSize),u,v,stRToTMain.GetD3DTexture(),0xffffffff);
        stRToTBlur.ClearFrameBuffer(0xff000000);
    }
    const DWORD alpha=static_cast<DWORD>(static_cast<double>(st455FullScreenDensity)*255.0);
    Draw2DSprite(0,0,float(stTexSize),float(stTexSize),u,v,stRToTMain.GetD3DTexture(),0x00ffffff|(alpha<<24));
    stRToTBlur.ClearFrameBuffer(0xff000000);
    Draw2DSprite(0,0,float(stTexSize),float(stTexSize),u,v,stRToTMain.GetD3DTexture(),0xffffffff);
}
