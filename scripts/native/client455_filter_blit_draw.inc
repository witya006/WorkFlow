#include "client455_filter_blit.h"
#include <memory>

namespace {
struct FilterRelease455 {
    template<class T> void operator()(T* value) const { value->Release(); }
};
template<class T> using FilterRef455 = std::unique_ptr<T, FilterRelease455>;

struct FilterTarget455 {
    IDirect3DTexture9* texture;
    FilterRef455<IDirect3DSurface9> surface;
    D3DSURFACE_DESC desc{};

    explicit FilterTarget455(IDirect3DTexture9* value) : texture(value) {}

    bool open() {
        IDirect3DSurface9* level = nullptr;
        const auto hr = texture->GetSurfaceLevel(0, &level);
        surface.reset(level);
        return SUCCEEDED(hr) && surface && SUCCEEDED(surface->GetDesc(&desc)) &&
            desc.Width && desc.Height && (desc.Usage & D3DUSAGE_RENDERTARGET);
    }
};

struct FilterSavedState455 {
    FilterRef455<IDirect3DSurface9> targets[4];
    FilterRef455<IDirect3DSurface9> depth;
    FilterRef455<IDirect3DStateBlock9> state;
    D3DVIEWPORT9 viewport{};
    DWORD targetCount = 0;

    bool capture(IDirect3DDevice9& device) {
        D3DCAPS9 caps{};
        if (FAILED(device.GetDeviceCaps(&caps)) || !caps.NumSimultaneousRTs) return false;
        targetCount = caps.NumSimultaneousRTs < 4 ? caps.NumSimultaneousRTs : 4;
        for (DWORD slot = 0; slot < targetCount; ++slot) {
            IDirect3DSurface9* surface = nullptr;
            const auto hr = device.GetRenderTarget(slot, &surface);
            targets[slot].reset(surface);
            if (FAILED(hr) && (slot == 0 || hr != D3DERR_NOTFOUND)) return false;
        }
        if (!targets[0]) return false;

        IDirect3DSurface9* surface = nullptr;
        const auto depthResult = device.GetDepthStencilSurface(&surface);
        depth.reset(surface);
        if (FAILED(depthResult) && depthResult != D3DERR_NOTFOUND) return false;
        if (FAILED(device.GetViewport(&viewport))) return false;
        IDirect3DStateBlock9* block = nullptr;
        const auto stateResult = device.CreateStateBlock(D3DSBT_ALL, &block);
        state.reset(block);
        return SUCCEEDED(stateResult) && state && SUCCEEDED(state->Capture());
    }

    bool restore(IDirect3DDevice9& device) const {
        // State blocks restore shader/texture state and stream zero; render
        // targets and depth are restored explicitly before applying the block.
        bool restored = SUCCEEDED(device.SetRenderTarget(0, targets[0].get()));
        for (DWORD slot = 1; slot < targetCount; ++slot) {
            if (FAILED(device.SetRenderTarget(slot, targets[slot].get()))) restored = false;
        }
        if (FAILED(device.SetDepthStencilSurface(depth.get()))) restored = false;
        if (FAILED(state->Apply())) restored = false;
        if (FAILED(device.SetViewport(&viewport))) restored = false;
        return restored;
    }
};

HRESULT filterTextures455(IDirect3DDevice9& device, IDirect3DTexture9* texture)
{
    for (DWORD slot = 0; slot < 4; ++slot) {
        const auto hr = device.SetTexture(slot, texture);
        if (FAILED(hr)) return hr;
    }
    return S_OK;
}

HRESULT filterBasePipeline455(IDirect3DDevice9& device, const FilterSavedState455& saved,
                             DWORD samplerCount)
{
    const struct { D3DRENDERSTATETYPE state; DWORD value; } renderStates[] = {
        {D3DRS_ZENABLE, FALSE},
        {D3DRS_ZWRITEENABLE, FALSE},
        {D3DRS_STENCILENABLE, FALSE},
        {D3DRS_FOGENABLE, FALSE},
        {D3DRS_ALPHABLENDENABLE, FALSE},
        {D3DRS_ALPHATESTENABLE, FALSE},
        {D3DRS_SCISSORTESTENABLE, FALSE},
        {D3DRS_CLIPPLANEENABLE, 0},
        {D3DRS_CULLMODE, D3DCULL_NONE},
        {D3DRS_FILLMODE, D3DFILL_SOLID},
        {D3DRS_SRGBWRITEENABLE, FALSE},
        {D3DRS_COLORWRITEENABLE, 0x0f},
    };
    const struct { D3DSAMPLERSTATETYPE state; DWORD value; } samplerStates[] = {
        {D3DSAMP_ADDRESSU, D3DTADDRESS_CLAMP},
        {D3DSAMP_ADDRESSV, D3DTADDRESS_CLAMP},
        {D3DSAMP_MINFILTER, D3DTEXF_LINEAR},
        {D3DSAMP_MAGFILTER, D3DTEXF_LINEAR},
        {D3DSAMP_MIPFILTER, D3DTEXF_NONE},
        {D3DSAMP_MIPMAPLODBIAS, 0},
        {D3DSAMP_MAXMIPLEVEL, 0},
        {D3DSAMP_SRGBTEXTURE, FALSE},
    };
    auto hr = device.SetDepthStencilSurface(nullptr);
    for (DWORD slot = 1; slot < saved.targetCount && SUCCEEDED(hr); ++slot)
        hr = device.SetRenderTarget(slot, nullptr);
    for (const auto& state : renderStates) {
        if (FAILED(hr)) return hr;
        hr = device.SetRenderState(state.state, state.value);
    }
    for (DWORD slot = 0; slot < samplerCount && SUCCEEDED(hr); ++slot) {
        for (const auto& state : samplerStates) {
            hr = device.SetSamplerState(slot, state.state, state.value);
            if (FAILED(hr)) return hr;
        }
    }
    return SUCCEEDED(hr) ? device.SetStreamSourceFreq(0, 1) : hr;
}

HRESULT filterPipeline455(IDirect3DDevice9& device, const FilterSavedState455& saved,
                         UINT width, UINT height)
{
    auto hr = filterBasePipeline455(device, saved, 4);
    if (SUCCEEDED(hr)) hr = RF455_BindR3VertexProgram(&device, stFilterBlit455);
    if (SUCCEEDED(hr)) hr = device.SetPixelShader(stBlurBlit455);

    // x86 RVAs 0x4D9060/0x4D9350. The shader's a0 selects registers 10,
    // 15, 20 and 25. Tap spacing for all passes comes from the output.
    const float viewProjection[20] = {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1.0f / 19.8f, 4.8f / 19.8f,
        0, 0, 0, 1,
        2, 0, 0, 0,
    };
    const float a = 0.001f - 0.5f / width;
    const float b = 1.5f / width - 0.001f;
    const float c = 0.001f - 0.5f / height;
    const float d = 1.5f / height - 0.001f;
    const float taps[4][4] = {{a,c,0,0}, {a,d,0,0}, {b,d,0,0}, {b,c,0,0}};
    if (SUCCEEDED(hr)) hr = device.SetVertexShaderConstantF(0, viewProjection, 5);
    for (UINT lane = 0; lane < 4 && SUCCEEDED(hr); ++lane)
        hr = device.SetVertexShaderConstantF(10 + lane * 5, taps[lane], 1);
    return hr;
}

HRESULT filterPass455(IDirect3DDevice9& device, const FilterTarget455& destination,
                      const FilterTarget455& source)
{
    const D3DVIEWPORT9 viewport{0, 0, destination.desc.Width, destination.desc.Height, 0.0f, 1.0f};
    const float quad[4][5] = {
        {-1,-1,0,0,1}, {1,-1,0,1,1}, {1,1,0,1,0}, {-1,1,0,0,0},
    };
    auto hr = filterTextures455(device, nullptr);
    if (SUCCEEDED(hr)) hr = device.SetRenderTarget(0, destination.surface.get());
    if (SUCCEEDED(hr)) hr = device.SetViewport(&viewport);
    if (SUCCEEDED(hr)) hr = device.Clear(0, nullptr, D3DCLEAR_TARGET, 0xff000000, 1.0f, 0);
    if (SUCCEEDED(hr)) hr = filterTextures455(device, source.texture);
    if (SUCCEEDED(hr)) hr = device.DrawPrimitiveUP(D3DPT_TRIANGLEFAN, 2, quad, sizeof(quad[0]));
    return hr;
}

HRESULT filterFixedPipeline455(IDirect3DDevice9& device, const FilterSavedState455& saved)
{
    auto hr = filterBasePipeline455(device, saved, 1);
    if (SUCCEEDED(hr)) hr = RF455_SetFixedVertexFormat(&device, D3DFVF_XYZRHW | D3DFVF_DIFFUSE | D3DFVF_TEX1);
    if (SUCCEEDED(hr)) hr = device.SetPixelShader(nullptr);
    const struct { D3DRENDERSTATETYPE state; DWORD value; } renderStates[] = {
        {D3DRS_LIGHTING, FALSE},
        {D3DRS_SPECULARENABLE, FALSE},
        {D3DRS_ALPHABLENDENABLE, TRUE},
        {D3DRS_SEPARATEALPHABLENDENABLE, FALSE},
        {D3DRS_BLENDOP, D3DBLENDOP_ADD},
        {D3DRS_SRCBLEND, D3DBLEND_SRCALPHA},
        {D3DRS_DESTBLEND, D3DBLEND_ONE},
    };
    for (const auto& state : renderStates) {
        if (FAILED(hr)) return hr;
        hr = device.SetRenderState(state.state, state.value);
    }
    const struct { DWORD stage; D3DTEXTURESTAGESTATETYPE state; DWORD value; } textureStates[] = {
        {0, D3DTSS_TEXCOORDINDEX, 0},
        {0, D3DTSS_TEXTURETRANSFORMFLAGS, D3DTTFF_DISABLE},
        {0, D3DTSS_RESULTARG, D3DTA_CURRENT},
        {0, D3DTSS_COLOROP, D3DTOP_MODULATE},
        {0, D3DTSS_COLORARG1, D3DTA_TEXTURE},
        {0, D3DTSS_COLORARG2, D3DTA_DIFFUSE},
        {0, D3DTSS_ALPHAOP, D3DTOP_SELECTARG1},
        {0, D3DTSS_ALPHAARG1, D3DTA_TEXTURE},
        {1, D3DTSS_COLOROP, D3DTOP_DISABLE},
        {1, D3DTSS_ALPHAOP, D3DTOP_DISABLE},
    };
    for (const auto& state : textureStates) {
        if (FAILED(hr)) return hr;
        hr = device.SetTextureStageState(state.stage, state.state, state.value);
    }
    return hr;
}

HRESULT filterFixedPass455(IDirect3DDevice9& device, const FilterTarget455& destination,
                           IDirect3DTexture9* source, unsigned quality)
{
    const auto width = destination.desc.Width;
    const auto height = destination.desc.Height;
    const D3DVIEWPORT9 full{0, 0, width, height, 0.0f, 1.0f};
    const D3DVIEWPORT9 inset{1, 1, width - 2, height - 2, 0.0f, 1.0f};
    auto hr = device.SetTexture(0, nullptr);
    if (SUCCEEDED(hr)) hr = device.SetRenderTarget(0, destination.surface.get());
    if (SUCCEEDED(hr)) hr = device.SetViewport(&full);
    if (SUCCEEDED(hr)) hr = device.Clear(0, nullptr, D3DCLEAR_TARGET, 0xff000000, 1.0f, 0);
    if (SUCCEEDED(hr)) hr = device.SetViewport(&inset);
    if (SUCCEEDED(hr)) hr = device.SetTexture(0, source);
    if (FAILED(hr)) return hr;

    // x86 0x4CF420 selects a 3x3 or 5x5 kernel. 0x4CEF30 draws a shifted
    // full-target quad for each tap, using the inset viewport for clipping.
    const int radius = static_cast<int>(quality);
    const unsigned kernel = 2 * quality + 1;
    const DWORD diffuse = 0xff000000u | (255 / (kernel * kernel)) * 0x00010101u;
    struct Vertex { float x, y, z, rhw; DWORD color; float u, v; };
    static_assert(sizeof(Vertex) == 28, "455 fixed filter vertex stride");
    Vertex vertices[5 * 5 * 6];
    auto* next = vertices;
    for (int x = -radius; x <= radius; ++x) {
        for (int y = -radius; y <= radius; ++y) {
            const float left = x - 0.5f;
            const float top = y - 0.5f;
            const float right = left + width;
            const float bottom = top + height;
            const Vertex topLeft{left, top, 0.1f, 0.5f, diffuse, 0.001f, 0.001f};
            const Vertex topRight{right, top, 0.1f, 0.5f, diffuse, 0.999f, 0.001f};
            const Vertex bottomLeft{left, bottom, 0.1f, 0.5f, diffuse, 0.001f, 0.999f};
            const Vertex bottomRight{right, bottom, 0.1f, 0.5f, diffuse, 0.999f, 0.999f};
            *next++ = topLeft;
            *next++ = topRight;
            *next++ = bottomLeft;
            *next++ = bottomLeft;
            *next++ = topRight;
            *next++ = bottomRight;
        }
    }
    return device.DrawPrimitiveUP(D3DPT_TRIANGLELIST, 2 * kernel * kernel, vertices, sizeof(Vertex));
}
}

bool RF455_FilterBlitAvailable()
{
    return stFilterBlit455.shader && stFilterBlit455.declaration && stBlurBlit455;
}

bool RF455_FilterBlit(IDirect3DTexture9* output, IDirect3DTexture9* input, unsigned passes)
{
    // x86 RVA 0x4D9730 alternates the two render-target textures.
    auto* device = GetD3dDevice();
    if (!device || !output || !input || output == input || !passes || !RF455_FilterBlitAvailable())
        return false;
    FilterTarget455 targets[] = {FilterTarget455(output), FilterTarget455(input)};
    if (!targets[0].open() || !targets[1].open() || targets[0].surface.get() == targets[1].surface.get())
        return false;
    FilterSavedState455 saved;
    if (!saved.capture(*device)) return false;
    auto hr = device->BeginScene();
    if (FAILED(hr)) return false;

    hr = filterPipeline455(*device, saved, targets[0].desc.Width, targets[0].desc.Height);
    for (unsigned pass = 0; pass < passes && SUCCEEDED(hr); ++pass) {
        const auto destination = pass % 2;
        hr = filterPass455(*device, targets[destination], targets[1 - destination]);
    }
    const auto end = device->EndScene();
    const auto unbound = filterTextures455(*device, nullptr);
    if (SUCCEEDED(hr)) hr = unbound;
    if (SUCCEEDED(hr) && SUCCEEDED(end) && passes % 2 == 0) {
        hr = device->StretchRect(targets[1].surface.get(), nullptr, targets[0].surface.get(), nullptr,
                                 D3DTEXF_LINEAR);
    }
    const bool restored = saved.restore(*device);
    return SUCCEEDED(hr) && SUCCEEDED(end) && restored;
}

bool RF455_FilterBlitFixed(IDirect3DTexture9* output, IDirect3DTexture9* input, unsigned quality)
{
    auto* device = GetD3dDevice();
    if (!device || !output || !input || output == input || quality < 1 || quality > 2) return false;
    FilterTarget455 destination(output), source(input);
    if (!destination.open() || !source.open() || destination.surface.get() == source.surface.get() ||
        destination.desc.Width <= 2 || destination.desc.Height <= 2) return false;
    FilterSavedState455 saved;
    if (!saved.capture(*device)) return false;
    auto hr = device->BeginScene();
    if (FAILED(hr)) return false;

    hr = filterFixedPipeline455(*device, saved);
    if (SUCCEEDED(hr)) hr = filterFixedPass455(*device, destination, input, quality);
    const auto end = device->EndScene();
    const auto unbound = device->SetTexture(0, nullptr);
    const bool restored = saved.restore(*device);
    return SUCCEEDED(hr) && SUCCEEDED(end) && SUCCEEDED(unbound) && restored;
}
