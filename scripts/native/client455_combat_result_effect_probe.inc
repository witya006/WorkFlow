class CombatResultDisplay {
    static constexpr unsigned width = 640, height = 480;
    static constexpr DWORD clearColor = 0xff102030;
    LPDIRECT3DDEVICE9 device = nullptr;
    unsigned blockPixels = 0, missPixels = 0;

    unsigned draw(float step, const char* capture = nullptr) {
        R3SetLoopTime(step);
        require(SUCCEEDED(device->Clear(0, nullptr, D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER,
                                        clearColor, 1.0f, 0)), "Clear combat text frame");
        require(SUCCEEDED(device->BeginScene()), "Begin combat text frame");
        EFUtil_RenderStringMoveOut();
        require(SUCCEEDED(device->EndScene()), "End combat text frame");
        LPDIRECT3DSURFACE9 target = nullptr, surface = nullptr;
        require(SUCCEEDED(device->GetRenderTarget(0, &target)), "Combat text render target");
        D3DSURFACE_DESC desc{};
        require(SUCCEEDED(target->GetDesc(&desc)) && desc.Width >= width && desc.Height >= height &&
                (desc.Format == D3DFMT_X8R8G8B8 || desc.Format == D3DFMT_A8R8G8B8), "Combat text frame format");
        require(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width, desc.Height, desc.Format,
                                                              D3DPOOL_SYSTEMMEM, &surface, nullptr)),
                "Combat text readback surface");
        require(SUCCEEDED(device->GetRenderTargetData(target, surface)), "Read combat text frame");
        D3DLOCKED_RECT lock{};
        require(SUCCEEDED(surface->LockRect(&lock, nullptr, D3DLOCK_READONLY)), "Lock combat text frame");
        std::FILE* file = capture ? std::fopen(capture, "wb") : nullptr;
        require(!capture || file, "Save combat text frame");
        unsigned changed = 0;
        for (unsigned y = 0; y < height; ++y) {
            const auto* row = reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits) + y * lock.Pitch);
            for (unsigned x = 0; x < width; ++x)
                changed += (row[x] & 0xffffff) != (clearColor & 0xffffff);
            if (file) std::fwrite(row, sizeof(*row), width, file);
        }
        if (file) std::fclose(file);
        surface->UnlockRect();
        surface->Release();
        target->Release();
        return changed;
    }

public:
    CombatResultDisplay() {
        SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
        InitR3Engine();
        auto* state = GetR3State();
        state->mScreenXsize = width;
        state->mScreenYsize = height;
        state->mbFullScreen = FALSE;
        ForceFullScreen();
        require(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr), 0)), "Initialize ordinary text device");
        device = GetD3dDevice();
        R3SetViewPort(0, 0, width, height);
        state->mIsFog = FALSE;
        const D3DXVECTOR3 eye(0, 0, -150), focus(0, 0, 0), up(0, 1, 0);
        D3DXMatrixLookAtLH(&state->mMatView, &eye, &focus, &up);
        D3DXMatrixInverse(&state->mInvMatView, nullptr, &state->mMatView);
        D3DXMatrixPerspectiveFovLH(&state->mMatProj, 0.7f, float(width) / height, 1.0f, 1000.0f);
        D3DXMatrixMultiply(&state->mMatViewProj, &state->mMatView, &state->mMatProj);
        EFUtilFontRestoreDeviceObjects();
        RF455_PrepareTaggedAudio(state->SoundPath);
        require(InitR3SoundSystem(".\\Snd\\WaveList.spt"), "Initialize Miles for real block sound");
        SetGlobalWavVolume(0);
        state->mSoundOn = TRUE;
        require(g_MainApp.TaggedAudio455().Open(".\\Snd\\WaveList.spt", state->SoundPath), "Open tagged sounds");
    }

    ~CombatResultDisplay() {
        g_MainApp.TaggedAudio455().Close();
        ReleaseR3SoundSystem();
        EFUtilFontInvalidateDeviceObjects();
        g_MainApp.ReleaseR3D3D();
        ReleaseR3Engine();
    }

    void verifyVisible(CMonster& monster, bool block) {
        monster.SetPosition(10, 20, 0);
        require(!draw(0.0f), "No text before dispatch");
        constexpr unsigned seed = 197;
        std::srand(seed);
        const DWORD sound = 277093 + std::rand() % 2;
        std::srand(seed);
        DispatchQueuedEffects();
        require(_GetEffectInfoList()->empty(), "Normal renderer consumes queued result");
        if (block) {
            const auto wave = g_MainApp.TaggedAudio455().Inspect(sound);
            require(wave.sample && AIL_3D_sample_status(static_cast<H3DSAMPLE>(wave.sample)) == SMP_PLAYING &&
                    wave.relative[0] == 10 && wave.relative[1] == 20 && wave.relative[2] == 0,
                    "Selected real block sound is playing at the actor position");
        }
        const auto pixels = draw(0.2f, block ? "block.bgra" : "miss.bgra");
        require(pixels > 100 && draw(0.6f) > 50 && !draw(0.11f), "Combat word remains visible until its fade ends");
        if (block) blockPixels = pixels;
        else missPixels = pixels;
    }

    void verifyClipped(CMonster& monster) {
        monster.Enable(ROSF_CLIPPED);
        DispatchQueuedEffects();
        require(_GetEffectInfoList()->empty() && !draw(0.2f), "Clipped bystander block produces no text");
        monster.Disable(ROSF_CLIPPED);
    }

    void report() const {
        std::printf("{\"status\":\"PASS\",\"block_pixels\":%u,\"miss_pixels\":%u,"
                    "\"real_block_sample\":true,\"expired_pixels\":0,\"clipped_pixels\":0}\n",
                    blockPixels, missPixels);
    }
};
