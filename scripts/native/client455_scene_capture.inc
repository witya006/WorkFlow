//4558CD9F0 including its lower chunk8CD830,and8CDAD0/8CE020.
static CTextureRender sceneCapture455,auxiliaryScene455;
static IDirect3DTexture9* perturbation455=nullptr;
CTextureRender* RF455_GetSceneCaptureTarget(){return &sceneCapture455;}
CTextureRender* RF455_GetAuxiliarySceneTarget(){return &auxiliaryScene455;}
IDirect3DTexture9* RF455_GetPerturbationTexture(){return perturbation455;}
void InitFullScreenEffect(){
    auto* state=GetR3State();auto* device=GetD3dDevice();stTexSize=512;
    sceneCapture455.CreateTexture(device,DWORD(state->mScreenXsize),DWORD(state->mScreenYsize),TRUE);
    stRToTMain.CreateTexture(device,stTexSize,stTexSize,TRUE);
    stRToTBlur.CreateTexture(device,stTexSize,stTexSize,FALSE);
    auxiliaryScene455.CreateTexture(device,512,512,TRUE);
    stShadow.CreateTexture(device,256,256,FALSE);
    D3DXCreateTextureFromFileA(device,"system/PerbMap.dds",&perturbation455);
    //The existing void public ABI discards the target's final success value.
}
void ReleaseFullScreenEffect(){
    sceneCapture455.ReleaseTexture();stRToTMain.ReleaseTexture();
    stRToTBlur.ReleaseTexture();auxiliaryScene455.ReleaseTexture();stShadow.ReleaseTexture();
    if(perturbation455){perturbation455->Release();perturbation455=nullptr;}
}
IDirect3DTexture9* RF455_CaptureCurrentScene(){
    auto* texture=(stRealFullScreenEffectState?&stRToTMain:&sceneCapture455)->GetD3DTexture();
    IDirect3DSurface9 *destination,*source;auto* device=GetD3dDevice();
    texture->GetSurfaceLevel(0,&destination);device->GetRenderTarget(0,&source);
    device->StretchRect(source,nullptr,destination,nullptr,D3DTEXF_LINEAR);
    if(source)source->Release();
    //8CE020 deliberately retains the GetSurfaceLevel reference and ignores
    //HRESULTs,including a self-copy in active fullscreen mode. Do not claim a
    //balanced capture lifetime or certified failure domain from this port.
    return texture;
}
