//4558CD9F0 including its lower chunk8CD830,and8CDAD0/8CE020.
#include "client455_character_rfs.h"
#include "client455_filter_blit.h"
#include <memory>

static CTextureRender sceneCapture455,auxiliaryScene455;
static IDirect3DTexture9* perturbation455=nullptr;
static IDirect3DTexture9* worldBloom455=nullptr;
CTextureRender* RF455_GetSceneCaptureTarget(){return &sceneCapture455;}
CTextureRender* RF455_GetAuxiliarySceneTarget(){return &auxiliaryScene455;}
IDirect3DTexture9* RF455_GetPerturbationTexture(){return perturbation455;}
void InitFullScreenEffect(){
    auto* state=GetR3State();auto* device=GetD3dDevice();stTexSize=512;
    sceneCapture455.CreateTexture(device,DWORD(state->mScreenXsize),DWORD(state->mScreenYsize),TRUE);
    stRToTMain.CreateTexture(device,stTexSize,stTexSize,TRUE);
    stRToTBlur.CreateTexture(device,stTexSize,stTexSize,FALSE);
    auxiliaryScene455.CreateTexture(device,512,512,TRUE);
    D3DDISPLAYMODE mode{};
    if (device && !worldBloom455 && SUCCEEDED(device->GetDisplayMode(0, &mode))) {
        IDirect3DTexture9* texture = nullptr;
        if (SUCCEEDED(device->CreateTexture(256, 256, 1, D3DUSAGE_RENDERTARGET,
                                           mode.Format, D3DPOOL_DEFAULT, &texture, nullptr)))
            worldBloom455 = texture;
        else if (texture) texture->Release();
    }
    stShadow.CreateTexture(device,256,256,FALSE);
    constexpr std::uint64_t maxBytes = 64u * 1024u * 1024u;
    const auto source = RF455_GetCharacterRfsCache()->ReadLooseBytes("system/PerbMap.dds", maxBytes);
    if (device && source.status == RF455ResourceReadStatus::Ready && source.bytes && !source.bytes->empty()) {
        IDirect3DTexture9* texture = nullptr;
        const HRESULT result = D3DXCreateTextureFromFileInMemory(device, source.bytes->data(),
            static_cast<UINT>(source.bytes->size()), &texture);
        if (SUCCEEDED(result) && texture) {
            if (perturbation455) perturbation455->Release();
            perturbation455 = texture;
        } else if (texture) {
            texture->Release();
        }
    }
    //The existing void public ABI discards the target's final success value.
}
void ReleaseFullScreenEffect(){
    sceneCapture455.ReleaseTexture();stRToTMain.ReleaseTexture();
    stRToTBlur.ReleaseTexture();auxiliaryScene455.ReleaseTexture();stShadow.ReleaseTexture();
    if(worldBloom455){worldBloom455->Release();worldBloom455=nullptr;}
    if(perturbation455){perturbation455->Release();perturbation455=nullptr;}
}
IDirect3DTexture9* RF455_CaptureCurrentScene()
{
    auto* device = GetD3dDevice();
    auto* texture = (stRealFullScreenEffectState ? &stRToTMain : &sceneCapture455)->GetD3DTexture();
    if (!device || !texture) return nullptr;

    // RVA 0x4CE020 returns an owner-borrowed texture. Release each temporary
    // surface reference, including both when the active target is already it.
    const auto release = [](IDirect3DSurface9* surface) { surface->Release(); };
    using Surface = std::unique_ptr<IDirect3DSurface9, decltype(release)>;
    IDirect3DSurface9* level = nullptr;
    const auto levelResult = texture->GetSurfaceLevel(0, &level);
    Surface destination(level, release);
    if (FAILED(levelResult) || !destination) return nullptr;

    IDirect3DSurface9* target = nullptr;
    const auto targetResult = device->GetRenderTarget(0, &target);
    Surface source(target, release);
    if (FAILED(targetResult) || !source) return nullptr;
    if (source.get() == destination.get()) return texture;

    D3DSURFACE_DESC desc{};
    if (FAILED(source->GetDesc(&desc))) return nullptr;
    const auto filter = desc.MultiSampleType == D3DMULTISAMPLE_NONE ? D3DTEXF_LINEAR : D3DTEXF_NONE;
    const auto copied = device->StretchRect(source.get(), nullptr, destination.get(), nullptr, filter);
    return SUCCEEDED(copied) ? texture : nullptr;
}

namespace {
bool CopyBloomSource455(IDirect3DDevice9& device, IDirect3DTexture9* scratch)
{
    using Surface = std::unique_ptr<IDirect3DSurface9, void(*)(IDirect3DSurface9*)>;
    const auto release = [](IDirect3DSurface9* surface) { surface->Release(); };
    IDirect3DSurface9* source = nullptr;
    const auto sourceResult = device.GetRenderTarget(0, &source);
    Surface target(source, release);
    if (FAILED(sourceResult) || !target) return false;
    const auto levelZero = [release](IDirect3DTexture9* texture) -> Surface {
        IDirect3DSurface9* level = nullptr;
        if (texture) texture->GetSurfaceLevel(0, &level);
        return Surface(level, release);
    };
    auto seed = levelZero(scratch);
    if (!seed) return false;
    D3DSURFACE_DESC desc{};
    if (FAILED(target->GetDesc(&desc))) return false;
    if (desc.MultiSampleType == D3DMULTISAMPLE_NONE)
        return SUCCEEDED(device.StretchRect(target.get(), nullptr, seed.get(), nullptr, D3DTEXF_LINEAR));

    auto resolved = levelZero(sceneCapture455.GetD3DTexture());
    return resolved &&
           SUCCEEDED(device.StretchRect(target.get(), nullptr, resolved.get(), nullptr, D3DTEXF_NONE)) &&
           SUCCEEDED(device.StretchRect(resolved.get(), nullptr, seed.get(), nullptr, D3DTEXF_LINEAR));
}

void DrawSceneBloom455(IDirect3DDevice9& device, IDirect3DTexture9* texture, unsigned passes,
                       DWORD tint, float edge)
{
    IDirect3DStateBlock9* state = nullptr;
    const auto create = device.CreateStateBlock(D3DSBT_ALL, &state);
    if (!state) return;
    if (FAILED(create) || FAILED(state->Capture())) {
        state->Release();
        return;
    }
    D3DVIEWPORT9 viewport{};
    if (FAILED(device.GetViewport(&viewport))) {
        state->Release();
        return;
    }
    // 455 RVAs 0x14A830 and 0x13CB40 share this composite before UI.
    struct Vertex { float x, y, z, rhw; DWORD color; float u, v; };
    const float x = static_cast<float>(viewport.X) - 0.5f;
    const float y = static_cast<float>(viewport.Y) - 0.5f;
    const float right = x + viewport.Width, bottom = y + viewport.Height;
    const Vertex quad[] = {
        {x, y, 0.1f, 0.5f, tint, edge, edge},
        {right, y, 0.1f, 0.5f, tint, 1.0f, edge},
        {x, bottom, 0.1f, 0.5f, tint, edge, 1.0f},
        {right, bottom, 0.1f, 0.5f, tint, 1.0f, 1.0f},
    };
    HRESULT hr = RF455_SetFixedVertexFormat(&device, D3DFVF_XYZRHW | D3DFVF_DIFFUSE | D3DFVF_TEX1);
    if (SUCCEEDED(hr)) hr = device.SetPixelShader(nullptr);
    const struct { D3DRENDERSTATETYPE type; DWORD value; } render[] = {
        {D3DRS_ZENABLE, FALSE}, {D3DRS_ZWRITEENABLE, FALSE},
        {D3DRS_LIGHTING, FALSE}, {D3DRS_FOGENABLE, FALSE},
        {D3DRS_STENCILENABLE, FALSE}, {D3DRS_SCISSORTESTENABLE, FALSE},
        {D3DRS_CULLMODE, D3DCULL_NONE}, {D3DRS_ALPHATESTENABLE, FALSE},
        {D3DRS_ALPHABLENDENABLE, TRUE}, {D3DRS_SEPARATEALPHABLENDENABLE, FALSE},
        {D3DRS_BLENDOP, D3DBLENDOP_ADD},
        {D3DRS_SRCBLEND, D3DBLEND_INVSRCCOLOR}, {D3DRS_DESTBLEND, D3DBLEND_ONE},
    };
    for (const auto& pair : render)
        if (SUCCEEDED(hr)) hr = device.SetRenderState(pair.type, pair.value);
    if (SUCCEEDED(hr)) hr = device.SetStreamSourceFreq(0, 1);
    if (SUCCEEDED(hr)) hr = device.SetTexture(0, texture);
    const struct { D3DTEXTURESTAGESTATETYPE type; DWORD value; } stage[] = {
        {D3DTSS_COLOROP, D3DTOP_MODULATE}, {D3DTSS_COLORARG1, D3DTA_TEXTURE},
        {D3DTSS_COLORARG2, D3DTA_DIFFUSE}, {D3DTSS_ALPHAOP, D3DTOP_MODULATE},
        {D3DTSS_ALPHAARG1, D3DTA_TEXTURE}, {D3DTSS_ALPHAARG2, D3DTA_DIFFUSE},
        {D3DTSS_TEXCOORDINDEX, 0}, {D3DTSS_TEXTURETRANSFORMFLAGS, D3DTTFF_DISABLE},
        {D3DTSS_RESULTARG, D3DTA_CURRENT},
    };
    for (const auto& pair : stage)
        if (SUCCEEDED(hr)) hr = device.SetTextureStageState(0, pair.type, pair.value);
    if (SUCCEEDED(hr)) hr = device.SetTextureStageState(1, D3DTSS_COLOROP, D3DTOP_DISABLE);
    if (SUCCEEDED(hr)) hr = device.SetSamplerState(0, D3DSAMP_ADDRESSU, D3DTADDRESS_CLAMP);
    if (SUCCEEDED(hr)) hr = device.SetSamplerState(0, D3DSAMP_ADDRESSV, D3DTADDRESS_CLAMP);
    if (SUCCEEDED(hr)) hr = device.SetSamplerState(0, D3DSAMP_MINFILTER, D3DTEXF_LINEAR);
    if (SUCCEEDED(hr)) hr = device.SetSamplerState(0, D3DSAMP_MAGFILTER, D3DTEXF_LINEAR);
    if (SUCCEEDED(hr)) hr = device.SetSamplerState(0, D3DSAMP_MIPFILTER, D3DTEXF_NONE);
    for (unsigned n = 0; n < passes && SUCCEEDED(hr); ++n)
        hr = device.DrawPrimitiveUP(D3DPT_TRIANGLESTRIP, 2, quad, sizeof(Vertex));
    state->Apply();
    state->Release();
}

bool CompositeSceneBloom455(unsigned shaderPasses, unsigned fixedQuality, unsigned compositePasses,
                            DWORD tint, float edge)
{
    if (stFullScreenEffectState || stRealFullScreenEffectState) return true;
    auto* device = GetD3dDevice();
    auto* scratch = auxiliaryScene455.GetD3DTexture();
    auto* result = worldBloom455;
    if (!device || !scratch || !result) return true;
    if (FAILED(device->EndScene())) return false;
    bool blurred = false;
    if (CopyBloomSource455(*device, scratch)) {
        if (RF455_FilterBlitAvailable())
            blurred = RF455_FilterBlit(result, scratch, shaderPasses);
        else
            blurred = RF455_FilterBlitFixed(result, scratch, fixedQuality);
    }
    if (FAILED(device->BeginScene())) return false;
    if (blurred) DrawSceneBloom455(*device, result, compositePasses, tint, edge);
    return true;
}
}

bool RF455_CompositeWorldBloom(unsigned quality)
{
    if (!quality) return true;
    if (quality > 2) quality = 2;
    return CompositeSceneBloom455(quality + 1, quality, quality, 0x6e6e6e6e, 0.5f / 256.0f);
}

bool RF455_CompositeClassicLobbyBloom(unsigned quality)
{
    if (!quality) return true;
    // RVA 0x13CBB5 rerenders the lobby into the auxiliary texture. The fork
    // uses the current scene as the seed to avoid a second mutable lobby draw.
    if (quality == 2 && !CompositeSceneBloom455(3, 1, 1, 0x80808080u, 1.5f / 256.0f))
        return false;
    // Pinned RVA 0x13CC5C uses one white composite when BBoShasi is enabled.
    return CompositeSceneBloom455(2, 1, 1, 0xffffffffu, 0.5f / 256.0f);
}
