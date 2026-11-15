#include "client455_screen_transition.h"
#include <cmath>

namespace {
HRESULT transitionPipeline455(IDirect3DDevice9& device, IDirect3DTexture9* image)
{
    const struct { D3DRENDERSTATETYPE state; DWORD value; } states[] = {
        {D3DRS_ZENABLE, FALSE},
        {D3DRS_ZWRITEENABLE, FALSE},
        {D3DRS_FOGENABLE, FALSE},
        {D3DRS_STENCILENABLE, FALSE},
        {D3DRS_SCISSORTESTENABLE, FALSE},
        {D3DRS_CLIPPLANEENABLE, 0},
        {D3DRS_CULLMODE, D3DCULL_NONE},
        {D3DRS_FILLMODE, D3DFILL_SOLID},
        {D3DRS_COLORWRITEENABLE, 0x0f},
        {D3DRS_ALPHATESTENABLE, FALSE},
        {D3DRS_ALPHABLENDENABLE, TRUE},
        {D3DRS_SEPARATEALPHABLENDENABLE, FALSE},
        {D3DRS_BLENDOP, D3DBLENDOP_ADD},
        {D3DRS_SRCBLEND, D3DBLEND_SRCALPHA},
        {D3DRS_DESTBLEND, D3DBLEND_INVSRCALPHA},
    };

    for (const auto& state : states) {
        const auto hr = device.SetRenderState(state.state, state.value);
        if (FAILED(hr)) return hr;
    }
    const auto hr = device.SetStreamSourceFreq(0, 1);
    return FAILED(hr) ? hr : device.SetTexture(0, image);
}

HRESULT drawTransitionProgram455(IDirect3DDevice9& device, IDirect3DTexture9* mask, float progress)
{
    // Rows of the transposed matrix: identity * LookAtLH((0,0,-1), (0,0,0), (0,1,0))
    // * OrthoLH(2, 2, -1, 1). The shader reads these as c0 through c3.
    const float matrix[16] = {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 0.5f, 1,
        0, 0, 0, 1,
    };
    const float alpha[4] = {progress, progress, progress, progress};
    const float quad[4][7] = {
        {-1, 1, 0, 0, 0, 0, 0},
        { 1, 1, 0, 1, 0, 1, 0},
        {-1,-1, 0, 0, 1, 0, 1},
        { 1,-1, 0, 1, 1, 1, 1},
    };
    auto hr = RF455_BindR3VertexProgram(&device, stTransitionVertex455);
    if (SUCCEEDED(hr)) hr = device.SetPixelShader(stTransitionPixel455);
    if (SUCCEEDED(hr)) hr = device.SetTexture(1, mask);
    if (SUCCEEDED(hr)) hr = device.SetVertexShaderConstantF(0, matrix, 4);
    if (SUCCEEDED(hr)) hr = device.SetPixelShaderConstantF(1, alpha, 1);
    for (DWORD stage = 0; stage < 2 && SUCCEEDED(hr); ++stage) {
        hr = device.SetTextureStageState(stage, D3DTSS_COLOROP, D3DTOP_DISABLE);
        if (SUCCEEDED(hr)) hr = device.SetTextureStageState(stage, D3DTSS_COLORARG1, D3DTA_TEXTURE);
        if (SUCCEEDED(hr)) hr = device.SetTextureStageState(stage, D3DTSS_ALPHAOP, D3DTOP_DISABLE);
    }
    if (SUCCEEDED(hr)) hr = device.DrawPrimitiveUP(D3DPT_TRIANGLESTRIP, 2, quad, sizeof(quad[0]));
    return hr;
}

HRESULT drawTransitionFixed455(IDirect3DDevice9& device, float progress)
{
    D3DMATRIX identity{};
    identity._11 = identity._22 = identity._33 = identity._44 = 1.0f;
    D3DMATRIX view = identity;
    view._43 = 1.0f;
    D3DMATRIX projection = identity;
    projection._33 = projection._43 = 0.5f;
    const DWORD alpha = static_cast<DWORD>(progress * 255.0f);
    const float quad[4][5] = {
        {-1, 1, 0, 0, 0},
        { 1, 1, 0, 1, 0},
        {-1,-1, 0, 0, 1},
        { 1,-1, 0, 1, 1},
    };

    auto hr = RF455_SetFixedVertexFormat(&device, D3DFVF_XYZ | D3DFVF_TEX1);
    if (SUCCEEDED(hr)) hr = device.SetPixelShader(nullptr);
    if (SUCCEEDED(hr)) hr = device.SetRenderState(D3DRS_LIGHTING, FALSE);
    if (SUCCEEDED(hr)) hr = device.SetRenderState(D3DRS_TEXTUREFACTOR, alpha << 24);
    if (SUCCEEDED(hr)) hr = device.SetTransform(D3DTS_WORLD, &identity);
    if (SUCCEEDED(hr)) hr = device.SetTransform(D3DTS_VIEW, &view);
    if (SUCCEEDED(hr)) hr = device.SetTransform(D3DTS_PROJECTION, &projection);

    const struct { D3DTEXTURESTAGESTATETYPE state; DWORD value; } states[] = {
        {D3DTSS_TEXCOORDINDEX, 0},
        {D3DTSS_TEXTURETRANSFORMFLAGS, D3DTTFF_DISABLE},
        {D3DTSS_RESULTARG, D3DTA_CURRENT},
        {D3DTSS_COLOROP, D3DTOP_SELECTARG1},
        {D3DTSS_COLORARG1, D3DTA_TEXTURE},
        {D3DTSS_ALPHAOP, D3DTOP_SELECTARG1},
        {D3DTSS_ALPHAARG1, D3DTA_TFACTOR},
    };
    for (const auto& state : states) {
        if (FAILED(hr)) return hr;
        hr = device.SetTextureStageState(0, state.state, state.value);
    }
    if (SUCCEEDED(hr)) hr = device.SetTextureStageState(1, D3DTSS_COLOROP, D3DTOP_DISABLE);
    if (SUCCEEDED(hr)) hr = device.SetTextureStageState(1, D3DTSS_ALPHAOP, D3DTOP_DISABLE);
    if (SUCCEEDED(hr)) hr = device.DrawPrimitiveUP(D3DPT_TRIANGLESTRIP, 2, quad, sizeof(quad[0]));
    return hr;
}
}

bool RF455_DrawScreenTransition(IDirect3DTexture9* image, IDirect3DTexture9* mask, float progress)
{
    // Client 455 x86 RVA 0x4D9C10 draws the loading image over the current scene.
    if (!image || !std::isfinite(progress) || progress <= 0.0f) return false;
    auto* device = GetD3dDevice();
    if (!device) return false;
    if (progress > 1.0f) progress = 1.0f;

    IDirect3DStateBlock9* state = nullptr;
    const auto created = device->CreateStateBlock(D3DSBT_ALL, &state);
    if (!state) return false;
    if (FAILED(created) || FAILED(state->Capture())) {
        state->Release();
        return false;
    }

    auto hr = transitionPipeline455(*device, image);
    if (SUCCEEDED(hr)) {
        if (mask && stTransitionVertex455.shader && stTransitionVertex455.declaration && stTransitionPixel455)
            hr = drawTransitionProgram455(*device, mask, progress);
        else
            hr = drawTransitionFixed455(*device, progress);
    }
    const auto restored = state->Apply();
    state->Release();
    return SUCCEEDED(hr) && SUCCEEDED(restored);
}
