// Source reconstruction of455VA8F2E70/RVA4F2E70;the temporary managed
// texture/surface roundtrip is retained for non-compressed formats.
void *GetDDSTexFromBuffer(WORD xl,WORD yl,DWORD format,BYTE *buf)
{
    auto*device=GetD3dDevice();if(!device||!buf)return NULL;
    DWORD stride=0;
    switch(format){
        case D3DFMT_DXT1:stride=xl>>1;break;
        case D3DFMT_DXT5:stride=xl;break;
        case D3DFMT_A8R8G8B8:stride=4u*xl;break;
        case D3DFMT_A1R5G5B5:case D3DFMT_R5G6B5:stride=2u*xl;break;
        default:OutputDebugStringA("RF455 sprite:unsupported format");return NULL;
    }
    const size_t bytes=static_cast<size_t>(stride)*yl;
    // Preserve valid-input copying. Unlike455's unchecked first copy,the own
    // implementation bounds malformed input by the caller's published size.
    if(bytes>stDebugSize)return NULL;
    LPDIRECT3DTEXTURE9 texture=NULL,temporary=NULL;D3DLOCKED_RECT target={},source={};
    if(FAILED(D3DXCreateTexture(device,xl,yl,1,0,static_cast<D3DFORMAT>(format),D3DPOOL_MANAGED,&texture)))return NULL;
    if(FAILED(texture->LockRect(0,&target,NULL,0))){texture->Release();return NULL;}
    memcpy(target.pBits,buf,bytes);texture->UnlockRect(0);
    if(format==D3DFMT_DXT1||format==D3DFMT_DXT5)return texture;
    if(FAILED(D3DXCreateTexture(device,xl,yl,1,0,static_cast<D3DFORMAT>(format),D3DPOOL_MANAGED,&temporary))){texture->Release();return NULL;}
    LPDIRECT3DSURFACE9 from=NULL,to=NULL;
    HRESULT status=texture->GetSurfaceLevel(0,&from);
    if(SUCCEEDED(status))status=temporary->GetSurfaceLevel(0,&to);
    if(SUCCEEDED(status))status=D3DXLoadSurfaceFromSurface(to,NULL,NULL,from,NULL,NULL,D3DX_FILTER_TRIANGLE,0);
    if(from)from->Release();if(to)to->Release();
    if(FAILED(status)){temporary->Release();texture->Release();return NULL;}
    if(FAILED(temporary->LockRect(0,&source,NULL,0))){temporary->Release();texture->Release();return NULL;}
    if(FAILED(texture->LockRect(0,&target,NULL,0))){temporary->UnlockRect(0);temporary->Release();texture->Release();return NULL;}
    const bool valid=static_cast<size_t>(target.Pitch)*yl<=stDebugSize;
    if(valid)memcpy(target.pBits,source.pBits,bytes);
    texture->UnlockRect(0);temporary->UnlockRect(0);temporary->Release();
    if(!valid){texture->Release();return NULL;}
    return texture;
}
