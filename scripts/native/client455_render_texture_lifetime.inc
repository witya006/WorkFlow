void CTextureRender::ReleaseTexture()
{
    // RVA 0x4DA280 gates cleanup on successful creation. This owner also
    // releases resources returned during a failed creation attempt.
    SAFE_RELEASE(m_pRenderToSurface);
    SAFE_RELEASE(m_pCausticSurf);
    SAFE_RELEASE(m_pCausticTex);
    SAFE_RELEASE(m_pZBuffer);
    m_IsLoaded = FALSE;
    m_ClearAtOnce = FALSE;
    m_bUseZbuffer = FALSE;
    m_pd3dDevice = nullptr; // Borrowed.
    m_dwXsize = m_dwYsize = 0;
}

BOOL CTextureRender::CreateTexture(LPDIRECT3DDEVICE9 pd3dDevice, DWORD x_size, DWORD y_size, BOOL use_zbuffer)
{
    if (m_IsLoaded) return FALSE;
    const auto allocate = [&]() {
        if (!pd3dDevice || !x_size || !y_size) return false;
        D3DDISPLAYMODE mode{};
        if (FAILED(pd3dDevice->GetDisplayMode(0, &mode))) return false;
        if (use_zbuffer &&
            (FAILED(pd3dDevice->CreateDepthStencilSurface(x_size, y_size, D3DFMT_D16,
                D3DMULTISAMPLE_NONE, 0, FALSE, &m_pZBuffer, nullptr)) || !m_pZBuffer)) return false;
        if (FAILED(D3DXCreateTexture(pd3dDevice, x_size, y_size, 1, D3DUSAGE_RENDERTARGET,
                                     mode.Format, D3DPOOL_DEFAULT, &m_pCausticTex)) ||
            !m_pCausticTex) return false;
        if (use_zbuffer) return true;

        D3DSURFACE_DESC desc{};
        if (FAILED(m_pCausticTex->GetSurfaceLevel(0, &m_pCausticSurf)) || !m_pCausticSurf ||
            FAILED(m_pCausticSurf->GetDesc(&desc))) return false;
        return SUCCEEDED(D3DXCreateRenderToSurface(pd3dDevice, desc.Width, desc.Height, desc.Format,
            FALSE, D3DFMT_UNKNOWN, &m_pRenderToSurface)) && m_pRenderToSurface;
    };
    if (!allocate()) {
        ReleaseTexture();
        return FALSE;
    }
    m_pd3dDevice = pd3dDevice;
    m_dwXsize = x_size;
    m_dwYsize = y_size;
    m_ClearAtOnce = FALSE;
    m_bUseZbuffer = use_zbuffer;
    m_IsLoaded = TRUE;
    return TRUE;
}
