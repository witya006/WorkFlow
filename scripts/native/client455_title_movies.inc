#include "client455_nation_paths.h"
#include "client455_protocol_observation.h"
#include "R3Sound.h"
#include <dshow.h>
#include <wrl/client.h>
#include <algorithm>
#include <cstdio>
#include <string>

class RF455TitleMovies {
public:
    explicit RF455TitleMovies(HWND owner)
        : owner_(owner), com_(CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED)) {
        char profile[MAX_PATH]{};
        const std::string relative = std::string(RF455_GetClientDataRoot()) + "\\CcrLogo.dat";
        const auto size = GetFullPathNameA(relative.c_str(), MAX_PATH, profile, nullptr);
        if (size && size < MAX_PATH) profile_ = profile;
    }

    ~RF455TitleMovies() {
        Close();
        if (SUCCEEDED(com_)) CoUninitialize();
    }

    bool Start() {
        return Open(ReadPath("Logo", "./Snd/Bgm/ccrinc.avi"), 1) || StartPrologue();
    }

    bool Tick() {
        if (!events_) return false;
        long event;
        LONG_PTR first, second;
        while (events_->GetEvent(&event, &first, &second, 0) == S_OK) {
            events_->FreeEventParams(event, first, second);
            if (event != EC_COMPLETE && event != EC_USERABORT && event != EC_ERRORABORT) continue;
            RF455_ObserveProtocol("title-movie-end", stage_, unsigned(event), 0);
            Close();
            return StartPrologue();
        }
        return true;
    }

    void Skip() {
        RF455_ObserveProtocol("title-movie-skip", stage_, VK_ESCAPE, 0);
        prologuePending_ = false;
        Close();
    }

    void Resize() {
        if (!video_ || !owner_) return;
        RECT bounds{};
        if (!GetClientRect(owner_, &bounds)) return;
        long width = bounds.right, height = bounds.bottom;
        if (width <= 0 || height <= 0) return;
        long videoWidth = 0, videoHeight = 0;
        if (picture_ && SUCCEEDED(picture_->GetVideoSize(&videoWidth, &videoHeight)) &&
            videoWidth > 0 && videoHeight > 0) {
            if (double(width) * videoHeight < double(height) * videoWidth)
                height = long(double(width) * videoHeight / videoWidth);
            else
                width = long(double(height) * videoWidth / videoHeight);
        }
        video_->SetWindowPosition((bounds.right - width) / 2, (bounds.bottom - height) / 2, width, height);
    }

private:
    std::string ReadPath(const char* key, const char* fallback) const {
        if (profile_.empty()) return fallback;
        char value[64]{};
        GetPrivateProfileStringA("PlayAvi", key, fallback, value, sizeof(value), profile_.c_str());
        return value;
    }

    bool StartPrologue() {
        if (!prologuePending_) return false;
        prologuePending_ = false;
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
        if (SUCCEEDED(result)) result = graph_->RenderFile(fullPath, nullptr);
        if (SUCCEEDED(result)) result = graph_.As(&control_);
        if (SUCCEEDED(result)) result = graph_.As(&events_);
        if (SUCCEEDED(result)) result = graph_.As(&video_);
        if (SUCCEEDED(result)) result = video_->put_Owner(reinterpret_cast<OAHWND>(owner_));
        if (SUCCEEDED(result)) result = video_->put_WindowStyle(WS_CHILD | WS_CLIPSIBLINGS | WS_CLIPCHILDREN);
        if (SUCCEEDED(result)) result = video_->put_MessageDrain(reinterpret_cast<OAHWND>(owner_));
        if (SUCCEEDED(result)) {
            graph_.As(&picture_);
            Microsoft::WRL::ComPtr<IBasicAudio> audio;
            if (SUCCEEDED(graph_.As(&audio))) {
                const float volume = GetR3State()->mMusicOn
                    ? (std::max)(0.0f, (std::min)(1.0f, GetGlobalMusicVolume())) : 0.0f;
                audio->put_Volume(long(volume * 10000.0f) - 10000);
            }
            Resize();
            result = control_->Run();
        }
        if (SUCCEEDED(result)) result = video_->put_Visible(OATRUE);
        if (FAILED(result)) {
            RF455_ObserveProtocol("title-movie-unavailable", stage, unsigned(result), 0);
            Close();
            return false;
        }
        stage_ = stage;
        RF455_ObserveProtocol("title-movie-start", stage_, 0, 0);
        return true;
    }

    void Close() {
        if (control_) control_->Stop();
        if (video_) {
            video_->put_Visible(OAFALSE);
            video_->put_MessageDrain(0);
            video_->put_Owner(0);
        }
        picture_.Reset();
        video_.Reset();
        events_.Reset();
        control_.Reset();
        graph_.Reset();
    }

    HWND owner_;
    HRESULT com_;
    std::string profile_;
    bool prologuePending_ = true;
    unsigned stage_ = 0;
    Microsoft::WRL::ComPtr<IGraphBuilder> graph_;
    Microsoft::WRL::ComPtr<IMediaControl> control_;
    Microsoft::WRL::ComPtr<IMediaEvent> events_;
    Microsoft::WRL::ComPtr<IVideoWindow> video_;
    Microsoft::WRL::ComPtr<IBasicVideo> picture_;
};
