// The runner prefixes LOGINSTATE from the compiled source; no numeric state copies.
#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "userinterface/guicontroller/guimessagebox.h"
#include "client455_font.h"
#include <wrl/client.h>
#include <stdexcept>
#include <vector>
#include <cstdio>
#include <client455_language.h>
#include <client455_nation_paths.h>

template<class Tag, typename Tag::Type Member> struct MemberAccess {
    friend typename Tag::Type access(Tag) { return Member; }
};
#define FIELD(Tag, TypeName, Class, member) struct Tag { using Type = TypeName Class::*; friend Type access(Tag); }; template struct MemberAccess<Tag, &Class::member>;
FIELD(NetworkMember, CNetworkMgr, CMainApp, m_cNetworkMgr)
FIELD(SpriteMember, CSpriteMgr, CMainApp, m_cSpriteMgr)
FIELD(ScreenMember, CGUIScreen, CMainApp, m_cScreen)
FIELD(InputMember, CInputMgr, CMainApp, m_cInputMgr)
FIELD(SendBuffer, _NET_BUFFER*, CNetProcess, m_pSendBuffer)
FIELD(ReceiveBuffer, _NET_BUFFER*, CNetProcess, m_pRecvBuffer)
FIELD(Owner, CNetWorking*, CNetProcess, m_pNetwork)
struct Active { using Type = BYTE(CNetworkMgr::*)[6]; friend Type access(Active); };
template struct MemberAccess<Active, &CNetworkMgr::m_activeServer455>;
struct Pop { using Type = void(CNetProcess::*)(WORD); friend Type access(Pop); };
template struct MemberAccess<Pop, &CNetProcess::_PopRecvMsg>;
struct Load { using Type = BOOL(CMainApp::*)(); friend Type access(Load); };
template struct MemberAccess<Load, &CMainApp::LoadData>;
struct Unload { using Type = BOOL(CMainApp::*)(); friend Type access(Unload); };
template struct MemberAccess<Unload, &CMainApp::UnloadData>;

extern LOGINSTATE g_LoginState;
extern CMainApp g_MainApp;
extern BOOL m_HaveCharacter[3];
extern void NetworkInput();
extern void EventJoinGameFunc();
FIELD(ActiveServer, char, CNetworkMgr, m_nActiveServerID)
FIELD(MessageBoard, CGUITextBoard, CGUIMessagebox, m_uiMsgBoard)

static void check(bool value, const char* why) {
    if (!value) throw std::runtime_error(why);
}
static LONG WINAPI crashReport(EXCEPTION_POINTERS* error) {
    std::fprintf(stderr, "Unhandled exception %08lx at RVA %08lx\n", error->ExceptionRecord->ExceptionCode,
        DWORD(reinterpret_cast<BYTE*>(error->ExceptionRecord->ExceptionAddress) -
              reinterpret_cast<BYTE*>(GetModuleHandleW(nullptr))));
    return EXCEPTION_EXECUTE_HANDLER;
}

static std::vector<BYTE> take(_NET_BUFFER& buffer) {
    int size = 0; bool missing = false;
    const auto* data = buffer.GetSendPoint(&size, &missing);
    if (!data || missing) return {};
    std::vector<BYTE> result(data, data + size); buffer.AddPopPos(size); return result;
}
static void push(_NET_BUFFER& buffer, const BYTE* data, std::size_t size) {
    const DWORD left = buffer.m_capacity - buffer.m_dwPushPnt;
    std::memcpy(buffer.GetPushPos(), data, size);
    if (size > left) std::memcpy(buffer.m_sMainBuffer, buffer.m_sMainBuffer + buffer.m_capacity, size - left);
    buffer.AddPushPos(static_cast<DWORD>(size));
}

static int runSelectionRejection() {
    using Microsoft::WRL::ComPtr;
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
    SetUnhandledExceptionFilter(crashReport);
    check(RF455_InitializeNationPaths() && RF455_InitializeLanguageData(), "language data");
    InitR3Engine();
    auto* state = GetR3State();
    check(state->mScreenXsize == 1920 && state->mScreenYsize == 1080, "Full HD configuration");
    const auto instance = GetModuleHandleW(nullptr);
    WNDCLASSW cls{};
    cls.lpfnWndProc = DefWindowProcW;
    cls.hInstance = instance;
    cls.lpszClassName = L"RF455SelectionRejectionProbe";
    check(RegisterClassW(&cls) != 0, "window class");
    HWND window = CreateWindowExW(0, cls.lpszClassName, cls.lpszClassName,
        WS_POPUP, 0, 0, 1920, 1080, nullptr, nullptr, instance, nullptr);
    check(window != nullptr && !IsWindowVisible(window), "hidden Full HD window");
    ComPtr<IDirect3D9> api;
    api.Attach(Direct3DCreate9(D3D_SDK_VERSION));
    D3DDISPLAYMODE desktop{};
    check(api && SUCCEEDED(api->GetAdapterDisplayMode(0, &desktop)), "adapter");
    D3DPRESENT_PARAMETERS pp{};
    pp.BackBufferWidth = 1920; pp.BackBufferHeight = 1080; pp.BackBufferCount = 1;
    pp.BackBufferFormat = desktop.Format; pp.SwapEffect = D3DSWAPEFFECT_DISCARD;
    pp.Windowed = TRUE; pp.hDeviceWindow = window;
    ComPtr<IDirect3DDevice9> device;
    check(SUCCEEDED(api->CreateDevice(0, D3DDEVTYPE_HAL, window,
        D3DCREATE_SOFTWARE_VERTEXPROCESSING, &pp, &device)), "hardware device");
    state->mIsUsedVertexShader = FALSE;
    check(SUCCEEDED(D3D_R3InitDevice(device.Get())), "engine device");
    SetViewPortArea(0, 0, 1920, 1080);
    check(SUCCEEDED(RF455_LoadTextResources(device.Get(), 200000000)), "text resources");
    std::fprintf(stderr, "Device and font ready\n");
    g_pUiSpriteMgr = &(g_MainApp.*access(SpriteMember{}));
    g_pUiScreen = &(g_MainApp.*access(ScreenMember{}));
    g_pUiInputMgr = &(g_MainApp.*access(InputMember{}));
    g_pUiSpriteMgr->Init();
    g_pUiScreen->Init();
    check((g_MainApp.*access(Load{}))() != 0, "ordinary UI resources");
    g_pUiScreen->SetSize(1920, 1080);
    std::fprintf(stderr, "UI resources ready\n");

    CAvatar avatar;
    std::unique_ptr<CAvatar[]> dummy(new CAvatar[3]);
    g_pAvatar = &avatar; g_pAvatarDummy = dummy.get();
    avatar.SetClientStage455(3); avatar.SetSkipTutorial455(1);
    dummy[0].SetSkipTutorial455(1); m_HaveCharacter[0] = TRUE;
    auto& network = g_MainApp.*access(NetworkMember{});
    auto& process = network.m_Process[0];
    g_pNetworkMgr = &network;
    network.m_pProcess[0] = &process;
    // Create() normally initializes these but also starts networking workers.
    network.SetResultOfUserRegistration(255); network.SetResultOfLogin(255);
    network.SetResultOfRequestForWorldServerList(255); network.SetResultOfSelectWorldServer(255);
    network.SetResultOfEnterTheWorldServer(255); network.SetResultOfRequestForDisconnectAccount(255);
    network.SetResultOfUserInfo(255); network.SetResultOfCharacterCreate(255);
    network.SetResultOfCharacterSelect(255); network.SetResultOfCharacterDelete(255);
    network.SetResultOfMoveOutFromServer(255); network.SetResultOfMoveIntoServer(255);
    _NET_BUFFER send, receive;
    std::vector<char> sendScratch(65536), receiveScratch(65536);
    check(send.Configure(65536, 65536, sendScratch.data()) &&
          receive.Configure(65536, 65536, receiveScratch.data()), "wire buffers");
    process.*access(SendBuffer{}) = &send; process.*access(ReceiveBuffer{}) = &receive;
    process.*access(Owner{}) = &network; process.m_nIndex = 0;
    process.m_Type.m_wSocketMaxNum = 1;
    process.m_codec455.initializeDefault(true);
    process.m_NetSocket.GetSocket(0)->m_bAccept = true;
    (network.*access(Active{}))[0] = GST_ZONE;
    network.*access(ActiveServer{}) = GST_ZONE;
    network.m_account455.zoneRequestMode = -1;
    RF455NetworkCodec peer;
    peer.initializeDefault(true);
    peer.receiveKey = process.m_codec455.sendKey;
    peer.sendKey = process.m_codec455.receiveKey;
    auto outgoing = [&]() {
        const auto wire = take(send);
        BYTE decoded[128]{}; std::size_t count = 0;
        check(!wire.empty() && peer.decode(wire.data(), wire.size(), decoded, sizeof(decoded), count),
              "decode actual outgoing packet");
        return std::vector<BYTE>(decoded, decoded + count);
    };
    auto respond = [&](BYTE result) {
        BYTE payload[22]{}; payload[0] = result; payload[2] = 42;
        BYTE wire[128]{}; std::size_t count = 0;
        check(peer.encode(0x0f01, payload, sizeof(payload), wire, sizeof(wire), count), "encode reply");
        push(receive, wire, 2); (process.*access(Pop{}))(0);
        check(network.IsSendRequestMsg(), "partial reply cannot complete request");
        push(receive, wire + 2, count - 2); (process.*access(Pop{}))(0);
        check(!network.IsSendRequestMsg() && network.GetResultOfCharacterSelect() == result,
              "actual fragmented response dispatcher");
    };
    g_LoginState = LGS_CHARACTERLOBBY;
    std::fprintf(stderr, "Network fixture ready\n");
    unsigned cases = 0;
    for (const auto expected : {std::pair<BYTE, unsigned>{72, 2779}, {74, 3732},
                                {76, 3816}, {1, 521}, {254, 521}}) {
        EventJoinGameFunc();
        std::fprintf(stderr, "Requested, response %u\n", unsigned(expected.first));
        check(g_LoginState == LGS_JOINGAME && network.IsSendRequestMsg(), "real join callback");
        check(outgoing() == std::vector<BYTE>({5, 0, 1, 14, 0}), "selected slot request");
        NetworkInput();
        check(g_LoginState == LGS_JOINGAME && take(send).empty() &&
              !g_pUiScreen->GetLastDialogBox(), "no result leaves waiting state intact");
        respond(expected.first);
        std::fprintf(stderr, "Dispatched\n");
        NetworkInput();
        check(g_LoginState == LGS_CHARACTERLOBBY, "rejection restores character selection");
        check(network.GetResultOfCharacterSelect() == CHAR_SELECT_NOT_RECIVED && take(send).empty(),
              "failure consumed once, no world handoff");
        auto* box = dynamic_cast<CGUIMessagebox*>(g_pUiScreen->GetLastDialogBox());
        check(box && box->IsOpen() && box->GetStyleID() == DLG_STYLE_OK, "ordinary error dialog");
        auto& board = box->*access(MessageBoard{});
        std::string displayed;
        for (unsigned i = 0; i < board.GetFragmentCount455(); ++i)
            displayed += board.GetFragment455(i)->GetText();
        check(displayed == RF455_GetNormalLanguagePack()->get(expected.second), "localized refusal text");
        NetworkInput();
        check(g_pUiScreen->GetLastDialogBox() == box && take(send).empty(), "no duplicate dialog or send");
        box->MsgProc(nullptr, WM_KEYDOWN, VK_RETURN, 0);
        check(box->GetResultMsg() == MSG_OK, "Enter acknowledges refusal");
        CGUIObject::RemoveEvent(box); box->Close(); box->RemoveOwnerWindow();
        check(!g_pUiScreen->GetLastDialogBox(), "refusal dismissed");
        ++cases;
    }
    EventJoinGameFunc();
    check(g_LoginState == LGS_JOINGAME && outgoing() == std::vector<BYTE>({5, 0, 1, 14, 0}),
          "retry after last rejection");
    respond(0);
    NetworkInput();
    check(g_LoginState == LGS_JOINGAME && network.IsSendRequestMsg() &&
          !g_pUiScreen->GetLastDialogBox(), "success starts existing handoff without error");
    check(outgoing() == std::vector<BYTE>({5, 0, 1, 5, 1}), "successful moveout request");
    NetworkInput();
    check(take(send).empty(), "success consumed once");

    process.*access(SendBuffer{}) = nullptr; process.*access(ReceiveBuffer{}) = nullptr;
    process.*access(Owner{}) = nullptr; g_pAvatar = nullptr; g_pAvatarDummy = nullptr;
    (g_MainApp.*access(Unload{}))(); RF455_ReleaseTextResources();
    D3D_R3DeleteDevice(); device.Reset(); DestroyWindow(window); ReleaseR3Engine();
    FILE* output = std::fopen("result.json", "wb"); check(output != nullptr, "result file");
    std::fprintf(output, "{\"status\":\"PASS\",\"rejection_cases\":%u,\"actual_network_input\":true,"
        "\"actual_fragmented_dispatch\":true,\"actual_modal_and_localization\":true,"
        "\"retry_callback\":true,\"success_moveout\":true,\"live_server\":false}\n", cases);
    std::fclose(output);
    return 0;
}

int main() {
    try { return runSelectionRejection(); }
    catch (const std::exception& error) { std::fprintf(stderr, "Selection rejection: %s\n", error.what()); return 1; }
}
