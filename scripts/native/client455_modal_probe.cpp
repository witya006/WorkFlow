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
#include "userinterface/guicontroller/guimessagebox.h"
#include "userinterface/gamewindow/guichatwindow.h"
#include "mainapp.h"
#include "client455_font.h"
#include "client455_modal.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
#define FIELD(Tag,TypeName,Class,member) struct Tag{using Type=TypeName Class::*;friend Type access(Tag);};template struct MemberAccess<Tag,&Class::member>;
FIELD(SpriteMember,CSpriteMgr,CMainApp,m_cSpriteMgr)
FIELD(ScreenMember,CGUIScreen,CMainApp,m_cScreen)
FIELD(OKButton,CGUIButtonEx,CGUIDialogBox,m_uiOKButton)
FIELD(CancelButton,CGUIButtonEx,CGUIDialogBox,m_uiCancelButton)
FIELD(CloseButton,CGUIButton,CGUIDialogBox,m_uiCloseButton)
FIELD(MouseObserver,IMouseObserver*,CGUIObject,m_pMouseObserver)
FIELD(BaseBoard,CGUIObject,CGUIMessagebox,m_cBase)
FIELD(Label,CGUIText,CGUIButtonEx,m_cLabel)
struct Load{using Type=BOOL(CMainApp::*)();friend Type access(Load);};template struct MemberAccess<Load,&CMainApp::LoadData>;
struct Unload{using Type=BOOL(CMainApp::*)();friend Type access(Unload);};template struct MemberAccess<Unload,&CMainApp::UnloadData>;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
static CGUIMessagebox* show(WORD style=3,BOOL close=TRUE){
    _msgbox_create_info create;create.pMsg=const_cast<char*>("Tutorial 455");create.wDlgStyle=style;create.wUserDefinedID=0x6000;create.dwRGBA=0xb0ffffff;create.bAllowClose455=close;
    _GUIMessageBox(&create);auto* box=dynamic_cast<CGUIMessagebox*>(g_pUiScreen->GetLastDialogBox());
    check(box&&box->IsOpen()&&box->GetUserDefinedID()==0x6000&&box->GetStyleID()==style,"real modal");return box;
}
static void closeBox(CGUIDialogBox& box){CGUIObject::RemoveEvent(&box);box.Close();box.RemoveOwnerWindow();}
static unsigned capture(CGUIMessagebox& box,const char* filename){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");
    check(SUCCEEDED(device->BeginScene()),"begin");check(box.Draw()!=0,"actual modal draw");check(SUCCEEDED(device->EndScene()),"end");
    D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"GPU readback");
    D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");FILE* output=std::fopen(filename,"wb");check(output!=nullptr,"frame");unsigned changed=0;
    for(unsigned y=view.Y;y<view.Y+view.Height;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;
        std::fwrite(row,4,view.Width,output);for(unsigned x=0;x<view.Width;++x)changed+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(output);memory->UnlockRect();memory->Release();target->Release();return changed;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"real language");InitR3Engine();
    GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D init");
    g_pUiSpriteMgr=&(g_MainApp.*access(SpriteMember{}));g_pUiScreen=&(g_MainApp.*access(ScreenMember{}));
    check((g_MainApp.*access(Load{}))()!=0,"ordinary LoadData");g_pUiScreen->SetSize(640,480);
    CGUIMessagebox direct;check(!direct.GetAllowClose455(),"target base ctor starts close-disabled");
    auto* box=show();auto& ok=box->*access(OKButton{});auto& cancel=box->*access(CancelButton{});auto* pack=RF455_GetNormalLanguagePack();
    check(!std::strcmp(ok.GetLabel(),pack->get(106))&&!std::strcmp(cancel.GetLabel(),pack->get(107)),"real localized captions");
    auto* sprite=g_pUiSpriteMgr->GetSprite(SP_ID_COMMON);check(sprite!=nullptr,"real common sprite");
    check(ok.GetSizeX()==sprite->GetSpriteOrgXL(1,0)&&ok.GetSizeY()==sprite->GetSpriteOrgYL(1,0),"actual sprite dimensions");
    check(cancel.GetSizeX()==ok.GetSizeX()&&cancel.GetSizeY()==ok.GetSizeY(),"same button dimensions");
    const auto extent=RF455_MeasureLegacyText(pack->get(106));POINT labelPos={};ok.GetLabePos(labelPos);
    check(labelPos.x==(ok.GetSizeX()-extent.cx)/2&&labelPos.y==(ok.GetSizeY()-extent.cy)/2,"measured caption centering");
    check((ok.*access(Label{})).GetFont()->dwStyle==32,"caption outline");
    check(ok.GetPosX()==box->GetPosX()+box->GetSizeX()-2*ok.GetSizeX()-14&&cancel.GetPosX()==box->GetPosX()+box->GetSizeX()-ok.GetSizeX()-7,"target horizontal margins");
    check(ok.GetPosY()==box->GetPosY()+box->GetSizeY()-ok.GetSizeY()-7,"target bottom margin");
    check((box->*access(BaseBoard{})).GetARGB()==0xb0222628,"alpha preserves background color");
    unsigned states=0;for(const auto pair:std::vector<std::pair<WORD,WORD>>{{0,0},{HOVERED,1},{WORD(HOVERED|PRESSED),2},{DISABLED,3},{WORD(DISABLED|HOVERED),3}}){
        ok.SetState(pair.first);cancel.SetState(pair.first);check(ok.GetSpriteInfo()->wActionNo==1&&ok.GetSpriteInfo()->wFrameNo==pair.second&&cancel.GetSpriteInfo()->wFrameNo==pair.second,"state frame");
        check((ok.*access(Label{})).GetFont()->dwColor==((pair.first&DISABLED)?0xff797979:0xffffffff),"disabled caption priority");++states;
    }
    ok.SetState(0);cancel.SetState(0);const unsigned colored=capture(*box,"modal-normal.bgra");check(colored>100,"actual viewport pixels");
    ok.SetState(HOVERED);capture(*box,"modal-hover.bgra");ok.SetState(DISABLED);capture(*box,"modal-disabled.bgra");
    ok.SetLabel(const_cast<char*>("CustomOK"));cancel.SetLabel(const_cast<char*>("CustomCancel"));box->Open();
    check(!(ok.GetState()&DISABLED)&&!std::strcmp(ok.GetLabel(),pack->get(106))&&!std::strcmp(cancel.GetLabel(),"CustomCancel"),"Open resets/enables OK only");
    closeBox(*box);
    box=show(4,FALSE);check(!box->GetAllowClose455()&&box->MsgProc(nullptr,WM_CHAR,VK_ESCAPE,0)==0&&box->GetResultMsg()==MSG_NONE,"blocked Escape");
    box->MsgProc(nullptr,WM_KEYDOWN,VK_RETURN,0);check(box->GetResultMsg()==MSG_OK,"Enter regardless close flag");closeBox(*box);
    box=show(3);check(box->GetAllowClose455(),"pooled close permission reset");box->MsgProc(nullptr,WM_CHAR,VK_ESCAPE,0);check(box->GetResultMsg()==MSG_CLOSE,"Escape result3");closeBox(*box);
    for(unsigned key:{unsigned('y'),unsigned('Y'),unsigned('n'),unsigned('N')}){
        box=show(3);box->MsgProc(nullptr,WM_CHAR,key,0);check(box->GetResultMsg()==((key=='y'||key=='Y')?MSG_OK:MSG_CANCEL),"YN results");closeBox(*box);
    }
    for(unsigned index=0;index<3;++index){
        box=show(3);CGUIObject* source=index==0?static_cast<CGUIObject*>(&(box->*access(OKButton{}))):
            index==1?static_cast<CGUIObject*>(&(box->*access(CancelButton{}))):static_cast<CGUIObject*>(&(box->*access(CloseButton{})));
        check((source->*access(MouseObserver{}))==static_cast<IMouseObserver*>(box),"real button mouse observer binding");
        _mouse_event event={source,MOUSE_CLICKED,0,0};box->MouseEvent(event);
        check(box->GetResultMsg()==index+1,"real mouse result1/2/3");closeBox(*box);
    }
    box=show(4);box->MsgProc(nullptr,WM_CHAR,'y',0);check(box->GetResultMsg()==MSG_NONE,"YN not accepted for OK style");closeBox(*box);
    {CGUIChatWindow chat;auto* previous=g_pUiChatWindow;g_pUiChatWindow=&chat;auto* input=chat.GetInputField();
        box=show(3);input->Show(TRUE);input->Active();input->EnableFocus();input->SetFocus();check(RF455_ModalChatInputFocused(),"real chat-input focus provider");
        box->MsgProc(nullptr,WM_CHAR,'y',0);check(box->GetResultMsg()==MSG_NONE,"focused chat suppresses YN");
        input->Show(FALSE);check(!RF455_ModalChatInputFocused(),"hidden focus not considered input");box->MsgProc(nullptr,WM_CHAR,'n',0);check(box->GetResultMsg()==MSG_CANCEL,"hidden chat allows YN");
        input->DisableFocus();g_pUiChatWindow=previous;closeBox(*box);
    }
    {auto* outer=show(3);CGUIMessagebox inner;inner.Init(4);inner.SetMsg(const_cast<char*>("Nested"));inner.SetOwnerWindow(outer);inner.SetAllowClose455(TRUE);inner.Open();
        outer->MsgProc(nullptr,WM_CHAR,VK_ESCAPE,0);check(inner.GetResultMsg()==MSG_CLOSE&&outer->GetResultMsg()==MSG_NONE,"nested dialog dispatch");closeBox(inner);closeBox(*outer);}
    _CloseAllDialogBox();(g_MainApp.*access(Unload{}))();R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"output");std::fprintf(output,"{\"status\":\"PASS\",\"real_modal_controls\":true,\"button_states\":%u,\"caption106107\":true,\"outline_and_margins\":true,\"keyboard_and_nested\":true,\"mouse_results123\":true,\"focused_chat_gate\":true,\"pool_close_permission\":true,\"open_reset_and_enable\":true,\"viewport_pixels\":%u,\"full455_text_scrollbar\":false,\"full_Tutorial\":false}\n",states,colored);std::fclose(output);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Modal: %s\n",error.what());return 1;}}
