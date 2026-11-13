#include "client455_nation_paths.h"
#include "client455_multisampling.h"
#include "client455_protocol_observation.h"
#include "R3Sound.h"
#include "r3d3d8.h"
#include "r3render.h"
#include <dshow.h>
#include <d3dx9.h>
#include <wrl/client.h>
#include <algorithm>
#include <cstdio>
#include <cwchar>
#include <string>
#include <vector>

// DirectShow's Sample Grabber is available without the obsolete qedit.h header.
struct __declspec(uuid("6b652fff-11fe-4fce-92ad-0266b5d7c78f")) RF455SampleGrabber : IUnknown {
    virtual HRESULT STDMETHODCALLTYPE SetOneShot(BOOL) = 0;
    virtual HRESULT STDMETHODCALLTYPE SetMediaType(const AM_MEDIA_TYPE*) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetConnectedMediaType(AM_MEDIA_TYPE*) = 0;
    virtual HRESULT STDMETHODCALLTYPE SetBufferSamples(BOOL) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetCurrentBuffer(long*, long*) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetCurrentSample(IMediaSample**) = 0;
    virtual HRESULT STDMETHODCALLTYPE SetCallback(IUnknown*, long) = 0;
};

static const CLSID titleSampleGrabber = {0xc1f400a0, 0x3f08, 0x11d3, {0x9f,0x0b,0,0x60,0x08,0x03,0x9e,0x37}};
static const CLSID titleNullRenderer = {0xc1f400a4, 0x3f08, 0x11d3, {0x9f,0x0b,0,0x60,0x08,0x03,0x9e,0x37}};

class RF455TitleMovies {
public:
    explicit RF455TitleMovies(HWND owner)
        : owner_(owner), com_(CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED)) {
        char profile[MAX_PATH]{};
        const std::string relative = std::string(RF455_GetClientDataRoot()) + "\\CcrLogo.dat";
        const auto size = GetFullPathNameA(relative.c_str(), MAX_PATH, profile, nullptr);
        if (size && size < MAX_PATH) profile_ = profile;
        char enabled[2]{};
        captureRequested_ = GetEnvironmentVariableA("RF455_CAPTURE_TITLE", enabled, sizeof(enabled)) == 1 && enabled[0] == '1';
    }

    ~RF455TitleMovies() {
        Close();
        if (SUCCEEDED(com_)) CoUninitialize();
    }

    bool Start() {
        return Open(ReadPath("Logo", "./Snd/Bgm/ccrinc.avi"), 1);
    }

    bool Tick() {
        if (!events_) return false;
        long event;
        LONG_PTR first, second;
        while (events_->GetEvent(&event, &first, &second, 0) == S_OK) {
            events_->FreeEventParams(event, first, second);
            if (event != EC_COMPLETE && event != EC_USERABORT && event != EC_ERRORABORT) continue;
            RF455_ObserveProtocol("title-movie-end", stage_, unsigned(event), 0);
            const bool finishedLogo = stage_ == 1 && event == EC_COMPLETE;
            Close();
            return finishedLogo && StartPrologue();
        }
        return true;
    }

    void Skip() {
        RF455_ObserveProtocol("title-movie-skip", stage_, VK_ESCAPE, 0);
        Close();
    }

    bool Render() {
        const bool drawn = DrawFrame();
        if (!drawn && !waitingForFrame_) {
            waitingForFrame_ = true;
            RF455_ObserveProtocol("title-movie-await-frame", stage_, 0, 0);
        }
        Sleep(25);
        return drawn;
    }

private:
    bool DrawFrame() {
        RECT bounds{};
        auto* device = GetD3dDevice();
        if (!device || !GetClientRect(owner_, &bounds) || bounds.right <= 0 || bounds.bottom <= 0) return false;
        UploadFrame(*device);
        if (!textureReady_ || !R3BeginScene()) return false;
        const HRESULT clear = device->Clear(0, nullptr, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER, 0xff000000, 1.f, 0);
        if (SUCCEEDED(clear)) {
            // Title 455 stretches the decoded image to the client rect and excludes texture padding.
            float u[] = {0.f, float(width_) / float(textureWidth_)};
            float v[] = {0.f, float(height_) / float(textureHeight_)};
            Draw2DSprite(0, 0, float(bounds.right), float(bounds.bottom), u, v, texture_.Get(), 0xffffffff);
        }
        R3EndScene();
        if (FAILED(clear)) return false;
        ReportFrame(*device, bounds);
        return true;
    }

    void ReportFrame(IDirect3DDevice9& device, const RECT& bounds) {
        waitingForFrame_ = false;
        if (!renderReported_) {
            renderReported_ = true;
            RF455_ObserveProtocol("title-movie-draw", stage_, unsigned(bounds.right), unsigned(bounds.bottom));
        }
        const ULONGLONG captureDelay = stage_ == 1 ? 3300 : 650;
        if (captureRequested_ && !captureDone_ && GetTickCount64() - startedAt_ >= captureDelay && VisibleFrame()) {
            captureDone_ = true;
            Capture(device);
        }
    }

    bool VisibleFrame() const {
        const auto* pixels = reinterpret_cast<const BYTE*>(frame_.data());
        const auto size = frame_.size() * sizeof(long);
        for (size_t i = 0; i < size; i += 67)
            if (pixels[i] > 32) return true;
        return false;
    }

    void Capture(IDirect3DDevice9& device) const {
        using Microsoft::WRL::ComPtr;
        ComPtr<IDirect3DSurface9> target, image;
        D3DSURFACE_DESC desc{};
        // Verify the swap-chain image queued for Present, even if another render target is active.
        HRESULT result = device.GetBackBuffer(0, 0, D3DBACKBUFFER_TYPE_MONO, &target);
        if (SUCCEEDED(result)) result = target->GetDesc(&desc);
        if (SUCCEEDED(result)) result = device.CreateOffscreenPlainSurface(desc.Width, desc.Height, desc.Format,
                                                                           D3DPOOL_SYSTEMMEM, &image, nullptr);
        if (SUCCEEDED(result)) result = RF455_ReadRenderTarget(device, *target.Get(), *image.Get());
        if (SUCCEEDED(result)) {
            const char* file = stage_ == 1 ? "title-logo.png" : "title-prologue.png";
            result = D3DXSaveSurfaceToFileA(file, D3DXIFF_PNG, image.Get(), nullptr, nullptr);
        }
        if (SUCCEEDED(result) && stage_ == 1) {
            ComPtr<IDirect3DSurface9> source;
            result = texture_->GetSurfaceLevel(0, &source);
            if (SUCCEEDED(result)) {
                const RECT video{0, 0, LONG(width_), LONG(height_)};
                result = D3DXSaveSurfaceToFileA("title-logo-source.png", D3DXIFF_PNG, source.Get(), nullptr, &video);
            }
        }
        RF455_ObserveProtocol("title-movie-capture", stage_, unsigned(result), 0);
    }

    static unsigned TextureExtent(unsigned pixels) {
        unsigned extent = 1;
        while (extent < pixels) extent *= 2;
        return extent;
    }

    HRESULT ConnectVideo(const wchar_t* path) {
        using Microsoft::WRL::ComPtr;
        ComPtr<IBaseFilter> source, splitter, tap, sink;
        ComPtr<ICaptureGraphBuilder2> builder;
        HRESULT result = graph_->AddSourceFilter(path, L"Title movie", &source);
        if (SUCCEEDED(result)) result = CoCreateInstance(titleSampleGrabber, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&tap));
        if (SUCCEEDED(result)) result = tap.As(&grabber_);
        AM_MEDIA_TYPE format{};
        format.majortype = MEDIATYPE_Video;
        format.subtype = MEDIASUBTYPE_RGB24;
        format.formattype = FORMAT_VideoInfo;
        if (SUCCEEDED(result)) result = grabber_->SetMediaType(&format);
        if (SUCCEEDED(result)) result = grabber_->SetBufferSamples(TRUE);
        if (SUCCEEDED(result)) result = CoCreateInstance(titleNullRenderer, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&sink));
        if (SUCCEEDED(result)) result = graph_->AddFilter(tap.Get(), L"Title RGB frames");
        if (SUCCEEDED(result)) result = graph_->AddFilter(sink.Get(), L"Title video clock");
        if (SUCCEEDED(result)) result = CoCreateInstance(CLSID_CaptureGraphBuilder2, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&builder));
        if (SUCCEEDED(result)) result = builder->SetFiltergraph(graph_.Get());
        const auto* extension = std::wcsrchr(path, L'.');
        if (SUCCEEDED(result) && extension && _wcsicmp(extension, L".avi") == 0) {
            result = CoCreateInstance(CLSID_AviSplitter, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&splitter));
            if (SUCCEEDED(result)) result = graph_->AddFilter(splitter.Get(), L"Title AVI streams");
            if (SUCCEEDED(result)) result = builder->RenderStream(nullptr, &MEDIATYPE_Stream, source.Get(), nullptr, splitter.Get());
        }
        auto* streams = splitter ? splitter.Get() : source.Get();
        if (SUCCEEDED(result)) result = builder->RenderStream(nullptr, &MEDIATYPE_Video, streams, tap.Get(), sink.Get());
        if (FAILED(result)) return result;

        AM_MEDIA_TYPE actual{};
        result = grabber_->GetConnectedMediaType(&actual);
        if (SUCCEEDED(result)) {
            result = VFW_E_INVALIDMEDIATYPE;
            if (actual.formattype == FORMAT_VideoInfo && actual.subtype == MEDIASUBTYPE_RGB24 &&
                actual.pbFormat && actual.cbFormat >= sizeof(VIDEOINFOHEADER)) {
                const auto& bitmap = reinterpret_cast<const VIDEOINFOHEADER*>(actual.pbFormat)->bmiHeader;
                if (bitmap.biWidth > 0 && bitmap.biWidth <= 4096 && bitmap.biHeight != 0 &&
                    bitmap.biHeight >= -4096 && bitmap.biHeight <= 4096 && bitmap.biBitCount == 24) {
                    width_ = bitmap.biWidth;
                    bottomUp_ = bitmap.biHeight > 0;
                    height_ = bottomUp_ ? bitmap.biHeight : -bitmap.biHeight;
                    textureWidth_ = TextureExtent(width_);
                    textureHeight_ = TextureExtent(height_);
                    rowPitch_ = (width_ * 3 + 3) & ~3u;
                    frame_.resize(size_t(rowPitch_) * height_ / sizeof(long));
                    result = S_OK;
                }
            }
        }
        CoTaskMemFree(actual.pbFormat);
        if (actual.pUnk) actual.pUnk->Release();
        if (SUCCEEDED(result)) builder->RenderStream(nullptr, &MEDIATYPE_Audio, streams, nullptr, nullptr);
        return result;
    }

    void UploadFrame(IDirect3DDevice9& device) {
        if (!grabber_ || frame_.empty()) return;
        const auto frameBytes = long(frame_.size() * sizeof(long));
        long received = frameBytes;
        if (FAILED(grabber_->GetCurrentBuffer(&received, frame_.data())) || received != frameBytes) return;
        if (!texture_ && FAILED(device.CreateTexture(textureWidth_, textureHeight_, 1, 0, D3DFMT_A8R8G8B8,
                                                       D3DPOOL_MANAGED, texture_.ReleaseAndGetAddressOf(), nullptr))) return;
        D3DLOCKED_RECT locked{};
        if (FAILED(texture_->LockRect(0, &locked, nullptr, 0))) return;
        const auto* pixels = reinterpret_cast<const BYTE*>(frame_.data());
        for (unsigned y = 0; y < height_; ++y) {
            const auto sourceY = bottomUp_ ? height_ - 1 - y : y;
            auto* target = reinterpret_cast<DWORD*>(static_cast<BYTE*>(locked.pBits) + size_t(y) * locked.Pitch);
            const auto* source = pixels + size_t(sourceY) * rowPitch_;
            for (unsigned x = 0; x < width_; ++x, source += 3)
                target[x] = D3DCOLOR_XRGB(source[2], source[1], source[0]);
        }
        textureReady_ = SUCCEEDED(texture_->UnlockRect(0));
    }

    std::string ReadPath(const char* key, const char* fallback) const {
        if (profile_.empty()) return fallback;
        char value[64]{};
        GetPrivateProfileStringA("PlayAvi", key, fallback, value, sizeof(value), profile_.c_str());
        return value;
    }

    bool StartPrologue() {
        const auto count = profile_.empty() ? 0u : GetPrivateProfileIntA("PlayAvi", "PlayedNum", 0, profile_.c_str());
        const auto index = count ? timeGetTime() % count : 0u;
        char key[24];
        std::snprintf(key, sizeof(key), "Play%u", unsigned(index));
        return Open(ReadPath(key, "./Snd/Bgm/Prologue.avi"), 2);
    }

    bool Open(const std::string& name, unsigned stage) {
        if (!owner_ || (FAILED(com_) && com_ != RPC_E_CHANGED_MODE) || name.empty()) return false;
        wchar_t relative[MAX_PATH]{};
        if (!MultiByteToWideChar(CP_ACP, 0, name.c_str(), -1, relative, MAX_PATH)) return false;
        wchar_t fullPath[MAX_PATH]{};
        const auto length = GetFullPathNameW(relative, MAX_PATH, fullPath, nullptr);
        const auto attributes = length && length < MAX_PATH ? GetFileAttributesW(fullPath) : INVALID_FILE_ATTRIBUTES;
        if (attributes == INVALID_FILE_ATTRIBUTES || attributes & FILE_ATTRIBUTE_DIRECTORY) return false;
        HRESULT result = CoCreateInstance(CLSID_FilterGraph, nullptr, CLSCTX_INPROC_SERVER,
                                          IID_PPV_ARGS(graph_.ReleaseAndGetAddressOf()));
        if (SUCCEEDED(result)) result = ConnectVideo(fullPath);
        if (SUCCEEDED(result)) result = graph_.As(&control_);
        if (SUCCEEDED(result)) result = graph_.As(&events_);
        if (SUCCEEDED(result)) {
            Microsoft::WRL::ComPtr<IBasicAudio> audio;
            if (SUCCEEDED(graph_.As(&audio))) {
                const float volume = GetR3State()->mMusicOn
                    ? (std::max)(0.0f, (std::min)(1.0f, GetGlobalMusicVolume())) : 0.0f;
                audio->put_Volume(long(volume * 10000.0f) - 10000);
            }
            result = control_->Run();
        }
        if (FAILED(result)) {
            RF455_ObserveProtocol("title-movie-unavailable", stage, unsigned(result), 0);
            Close();
            return false;
        }
        stage_ = stage;
        startedAt_ = GetTickCount64();
        RF455_ObserveProtocol("title-movie-start", stage_, 0, 0);
        return true;
    }

    void Close() {
        if (control_) control_->Stop();
        texture_.Reset();
        textureReady_ = false;
        renderReported_ = false;
        waitingForFrame_ = false;
        captureDone_ = false;
        frame_.clear();
        grabber_.Reset();
        events_.Reset();
        control_.Reset();
        graph_.Reset();
    }

    HWND owner_;
    HRESULT com_;
    std::string profile_;
    unsigned stage_ = 0;
    unsigned width_ = 0, height_ = 0, rowPitch_ = 0;
    unsigned textureWidth_ = 0, textureHeight_ = 0;
    ULONGLONG startedAt_ = 0;
    bool bottomUp_ = true, textureReady_ = false, renderReported_ = false, waitingForFrame_ = false;
    bool captureRequested_ = false, captureDone_ = false;
    std::vector<long> frame_;
    Microsoft::WRL::ComPtr<IGraphBuilder> graph_;
    Microsoft::WRL::ComPtr<IMediaControl> control_;
    Microsoft::WRL::ComPtr<IMediaEvent> events_;
    Microsoft::WRL::ComPtr<RF455SampleGrabber> grabber_;
    Microsoft::WRL::ComPtr<IDirect3DTexture9> texture_;
};
