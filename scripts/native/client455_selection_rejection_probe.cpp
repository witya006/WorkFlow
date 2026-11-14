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
#include <client455_selection.h>
#include "userinterface/loginwindow/guiselectcharacter.h"
#include "client455_equipment_object.h"

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
extern void EventDeleteCharacter();
enum COURSE { A_COURSE, B_COURSE, C_COURSE };
extern COURSE m_Course;
FIELD(DeleteButton, CGUIButtonEx, CGUISelectCharacter, m_cDeleteButton)
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

    // Deletion uses the real callback, transport/dispatcher and roster update.
    // This fixture never connects to a server or deletes a real character.
    network.ReceiveResponseMsg();
    g_LoginState=LGS_CHARACTERLOBBY;m_Course=A_COURSE;
    for(unsigned slot=0;slot<3;++slot){m_HaveCharacter[slot]=TRUE;dummy[slot].SetIndex(100+slot);}
    CGUISelectCharacter selection;
    _mouse_event deletionClick={};deletionClick.id=MOUSE_CLICKED;
    deletionClick.source=&(selection.*access(DeleteButton{}));
    selection.MouseEvent(deletionClick);
    auto* confirmation=selection.GetLastDialogBox();
    check(confirmation&&confirmation->GetStyleID()==DLG_STYLE_OK_CANCEL,"delete confirmation");
    confirmation->SetResultMsg(MSG_CANCEL);selection.ClosingDialogBox(confirmation);
    check(!selection.GetLastDialogBox()&&take(send).empty(),"cancel keeps roster and sends nothing");
    selection.MouseEvent(deletionClick);confirmation=selection.GetLastDialogBox();
    check(confirmation!=nullptr,"delete confirmation reopened");
    confirmation->SetResultMsg(MSG_OK);selection.ClosingDialogBox(confirmation);
    check(!selection.GetLastDialogBox(),"confirmation detached before request");
    check(outgoing()==std::vector<BYTE>({5,0,1,12,0}),"455 delete opcode and selected slot");
    EventDeleteCharacter();check(take(send).empty(),"duplicate delete request blocked");
    char malformed[2]={0,char(255)};
    check(!network.DispatchDeletedCharacter455(malformed,1)&&
          !network.DispatchDeletedCharacter455(malformed,2)&&network.IsSendRequestMsg(),
          "truncated/invalid slot cannot complete delete");
    char unrelated[2]={0,2};
    check(network.DispatchDeletedCharacter455(unrelated,2)&&network.IsSendRequestMsg(),
          "another slot response does not complete delete");
    auto deletionReply=[&](BYTE result,BYTE slot){
        BYTE payload[2]={result,slot},wire[128]{};std::size_t count=0;
        check(peer.encode(0x0d01,payload,2,wire,sizeof(wire),count),"encode delete reply");
        push(receive,wire,2);(process.*access(Pop{}))(0);
        check(network.IsSendRequestMsg(),"partial delete frame leaves request pending");
        push(receive,wire+2,count-2);(process.*access(Pop{}))(0);
        check(!network.IsSendRequestMsg()&&network.GetResultOfCharacterDelete()==result,
              "455 delete response dispatcher");
    };
    unsigned expectedDeletionMessage=0x20a;
    auto dismissResult=[&](){
        auto* box=dynamic_cast<CGUIMessagebox*>(g_pUiScreen->GetLastDialogBox());check(box!=nullptr,"delete result dialog");
        const auto* expected=RF455_GetNormalLanguagePack()->get(expectedDeletionMessage);
        check(expected&&*expected,"localized deletion record exists");
        auto& board=box->*access(MessageBoard{});std::string displayed;
        for(unsigned i=0;i<board.GetFragmentCount455();++i)displayed+=board.GetFragment455(i)->GetText();
        check(displayed==expected,"delete result uses active language pack");
        if(expectedDeletionMessage==0x20a){
            check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff152335,1,0)),"delete dialog clear");
            check(SUCCEEDED(device->BeginScene()),"delete dialog begin");box->Draw();
            check(SUCCEEDED(device->EndScene()),"delete dialog end");
            ComPtr<IDirect3DSurface9> surface;check(SUCCEEDED(device->GetRenderTarget(0,&surface)),"delete dialog target");
            using Save=HRESULT(WINAPI*)(const char*,D3DXIMAGE_FILEFORMAT,IDirect3DSurface9*,const PALETTEENTRY*,const RECT*);
            auto library=GetModuleHandleA("d3dx9_36.dll");
            auto save=library?reinterpret_cast<Save>(GetProcAddress(library,"D3DXSaveSurfaceToFileA")):nullptr;
            check(save&&SUCCEEDED(save("deletion-success.png",D3DXIFF_PNG,surface.Get(),nullptr,nullptr)),"delete dialog PNG");
        }
        CGUIObject::RemoveEvent(box);box->Close();box->RemoveOwnerWindow();
    };
    // User changes selection while the deletion reply is in flight.
    m_Course=B_COURSE;deletionReply(0,0);NetworkInput();
    check(!m_HaveCharacter[0]&&m_HaveCharacter[1]&&dummy[0].GetIndex()==ID_INVALID&&
          dummy[1].GetIndex()==101&&m_Course==B_COURSE&&g_LoginState==LGS_CHARACTERLOBBY,
          "only requested roster slot retired; other selected character survives");
    for(unsigned part=0;part<12;++part)check(dummy[0].GetEquipItem455(BYTE(part))==nullptr,"deleted equipment cleared");
    dismissResult();char duplicate[2]={0,0};
    check(network.DispatchDeletedCharacter455(duplicate,2),"duplicate reply ignored");NetworkInput();
    check(!g_pUiScreen->GetLastDialogBox()&&m_HaveCharacter[1],"duplicate does not retire another slot");
    EventDeleteCharacter();check(outgoing()==std::vector<BYTE>({5,0,1,12,1}),"second slot deletion request");
    expectedDeletionMessage=0x20b;deletionReply(CHAR_DELETE_DB_ERROR,1);NetworkInput();
    check(m_HaveCharacter[1]&&dummy[1].GetIndex()==101&&g_LoginState==LGS_CHARACTERLOBBY,
          "delete rejection preserves character and restores slots");dismissResult();
    EventDeleteCharacter();check(outgoing()==std::vector<BYTE>({5,0,1,12,1}),"retry after delete rejection");
    expectedDeletionMessage=0x20a;m_Course=static_cast<COURSE>(255);deletionReply(0,1);NetworkInput();
    check(m_Course==B_COURSE&&!m_HaveCharacter[1]&&m_HaveCharacter[2],"invalid current selection normalized on reply");
    dismissResult();m_Course=static_cast<COURSE>(255);
    check(!RF455_SelectedCharacterSlotOccupied(),"invalid selection is not occupied");
    EventDeleteCharacter();check(take(send).empty(),"invalid selection cannot send");
    m_Course=C_COURSE;EventDeleteCharacter();
    check(outgoing()==std::vector<BYTE>({5,0,1,12,2}),"last slot deletion request");
    deletionReply(0,2);NetworkInput();dismissResult();
    check(!m_HaveCharacter[0]&&!m_HaveCharacter[1]&&!m_HaveCharacter[2]&&m_Course==C_COURSE,
          "last deletion keeps a valid empty slot");
    EventDeleteCharacter();check(take(send).empty(),"empty slot cannot send");

    process.*access(SendBuffer{}) = nullptr; process.*access(ReceiveBuffer{}) = nullptr;
    process.*access(Owner{}) = nullptr; g_pAvatar = nullptr; g_pAvatarDummy = nullptr;
    (g_MainApp.*access(Unload{}))(); RF455_ReleaseTextResources();
    D3D_R3DeleteDevice(); device.Reset(); DestroyWindow(window); ReleaseR3Engine();
    FILE* output = std::fopen("result.json", "wb"); check(output != nullptr, "result file");
    std::fprintf(output, "{\"status\":\"PASS\",\"rejection_cases\":%u,\"actual_network_input\":true,"
        "\"actual_fragmented_dispatch\":true,\"actual_modal_and_localization\":true,"
        "\"retry_callback\":true,\"success_moveout\":true,\"delete_wire_and_roster\":true,"
        "\"delete_confirmation_cancel\":true,\"delete_malformed_and_stale\":true,\"live_server\":false}\n", cases);
    std::fclose(output);
    return 0;
}

int main() {
    try { return runSelectionRejection(); }
    catch (const std::exception& error) { std::fprintf(stderr, "Selection rejection: %s\n", error.what()); return 1; }
}
