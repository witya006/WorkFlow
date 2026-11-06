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
#include "client455_briefing_window.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_font.h"
#include "client455_text_metrics.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <string>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
#define FIELD(Tag,TypeName,Class,member) struct Tag{using Type=TypeName Class::*;friend Type access(Tag);};template struct MemberAccess<Tag,&Class::member>;
FIELD(SpriteMember,CSpriteMgr,CMainApp,m_cSpriteMgr)
FIELD(ScreenMember,CGUIScreen,CMainApp,m_cScreen)
struct Load{using Type=BOOL(CMainApp::*)();friend Type access(Load);};template struct MemberAccess<Load,&CMainApp::LoadData>;
struct Unload{using Type=BOOL(CMainApp::*)();friend Type access(Unload);};template struct MemberAccess<Unload,&CMainApp::UnloadData>;
struct QueueCreate{using Type=void(*)(WORD);friend Type access(QueueCreate);};template struct MemberAccess<QueueCreate,&CGUIObject::CreateEventQueue>;
static DWORD tick=1000;static unsigned randomQueries=0;static float delta=0;
static DWORD now(){return tick;}static float seconds(){return delta;}static int randomValue(){++randomQueries;return 0;}
static unsigned capture(CGUIObject& object,const char* filename){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");check(object.Draw()!=0,"draw");check(SUCCEEDED(device->EndScene()),"end");
    IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");
    D3DVIEWPORT9 viewport={};device->GetViewport(&viewport);check(viewport.Width==640&&viewport.Height==480,"viewport");FILE* out=std::fopen(filename,"wb");check(out!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=viewport.Y;y<viewport.Y+480;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+viewport.X;std::fwrite(row,4,640,out);for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(out);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static unsigned closingMessages(){MSG msg={};unsigned count=0;while(PeekMessageA(&msg,nullptr,0x1201,0x1201,PM_REMOVE)){if(msg.wParam!=38||(msg.lParam!=0&&msg.lParam!=1))std::fprintf(stderr,"posted source=%u value=%ld\n",unsigned(msg.wParam),long(msg.lParam));check(msg.wParam==38&&(msg.lParam==0||msg.lParam==1),"real posted UI event fields");count+=msg.lParam==1;}return count;}
static void mouseFrame(LONG x,LONG y,DWORD buttons){gMouse.x=x;gMouse.y=y;gMouse.z=0;gMouse.button=buttons;gMouseDev.Update();g_pUiScreen->InputProc();}
static void click(CGUIObject& object){const auto x=object.GetPosX()+object.GetSizeX()/2,y=object.GetPosY()+object.GetSizeY()/2;mouseFrame(x,y,0);mouseFrame(x,y,_LEFT_BUTTON_DOWN);mouseFrame(x,y,0);}
struct Spy:CGUIWindow {unsigned inputs=0,messages=0;BOOL InputProc()override{++inputs;return FALSE;}LRESULT MsgProc(HWND,UINT,WPARAM,LPARAM)override{++messages;return 0;}};
static void captureChecks(){
    Spy first,second,outsider;first.SetID(100);second.SetID(101);g_pUiScreen->Add(&first);g_pUiScreen->Add(&second);
    g_pUiScreen->SetCapture455(&outsider);check(!g_pUiScreen->GetCapture455(),"capture rejects nonmember");
    g_pUiScreen->SetCapture455(&first);g_pUiScreen->InputProc();check(first.inputs==1&&second.inputs==0&&g_dwGUIInputID==100,"capture input overrides ordinary windows even when child returnsfalse");
    g_pUiScreen->MsgProc(nullptr,WM_USER+99,0,0);check(first.messages==1&&second.messages==0,"capture message overrides ordinary windows");
    first.Show(FALSE);g_pUiScreen->MsgProc(nullptr,WM_USER+99,0,0);check(first.messages==1&&second.messages==1&&!g_pUiScreen->IsCaptureVisible455(),"hidden capture falls back visible windows");
    first.Show(TRUE);g_pUiScreen->Remove(&first);g_pUiScreen->MsgProc(nullptr,WM_USER+99,0,0);check(first.messages==2&&g_pUiScreen->GetCapture455()==&first,"remove retains pointer while object alive");
    first.Close();check(g_pUiScreen->GetCapture455()==&first&&!g_pUiScreen->IsCaptureVisible455(),"close retains hidden capture");
    g_pUiScreen->SetCapture455(nullptr);g_pUiScreen->Remove(&second);
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D");
    g_pUiSpriteMgr=&(g_MainApp.*access(SpriteMember{}));g_pUiScreen=&(g_MainApp.*access(ScreenMember{}));check((g_MainApp.*access(Load{}))()!=0,"LoadData");g_pUiScreen->SetSize(640,480);access(QueueCreate{})(128);
    auto oldTyping=RF455_SetTextTypingClock(now);auto oldAnimation=RF455_SetGuiAnimationReplay({now,seconds});auto oldBriefing=RF455_SetBriefingReplay({now,randomValue});
    captureChecks();MSG previousMessage={};while(PeekMessageA(&previousMessage,nullptr,0x1201,0x1201,PM_REMOVE)){}unsigned pageCount=0,frames=0;
    {
        RF455TutorialBriefingWindow view;auto& window=view.briefing();check(!window.GetPageCount455()&&window.GetAutoSize455(),"constructor state");view.setAutoSize(false);window.Init();window.SetID(38);g_pUiScreen->Add(&window);window.Show(FALSE);
        check(window.GetSizeX()==462&&window.GetSizeY()==207&&window.GetTyping455().GetSizeY()==143&&window.GetTyping455().GetMarginX()==25&&window.GetTyping455().GetMarginY()==15,"real Init geometry");
        RF455TutorialMessage message;message.texts.resize(1);auto& record=message.texts[0];record.font[0]=0;record.font[1]=0;const DWORD color=0xffe3e0d9;std::memcpy(record.font.data()+4,&color,4);
        const char* content="Page line01\nPage line02\nPage line03\nPage line04\nPage line05\nPage line06\nPage line07\nPage line08\nPage line09\nPage line10\nPage line11\nPage line12\nPage line13\nPage line14\nPage line15";
        record.bytes.assign(content,content+std::strlen(content));check(view.showRichMessage(message,true),"real rich provider");pageCount=window.GetPageCount455();check(pageCount>=2,"multi page text");
        check(g_pUiScreen->GetCapture455()==&window&&window.GetSizeX()==602&&window.GetPosX()==19&&window.GetPosY()==233&&window.GetTyping455().GetTypingStartTime455()==1250,"rich layout bottom40/capture/firstdelay");
        check(!window.IsReady455()&&std::strcmp(window.GetNext455().GetLabel(),RF455_GetNormalLanguagePack()->get(1059))==0,"typing label1059");capture(window,"briefing-opening.bgra");++frames;
        tick=1250;window.Update();tick=1330;window.Update();check(window.GetTyping455().GetTypingFragment455()==0&&window.GetTyping455().GetTypingOffset455()==0,"window updates typing child");tick=1410;window.Update();capture(window,"briefing-typing.bgra");++frames;
        closingMessages();click(window.GetNext455());check(window.IsReady455()&&window.GetTyping455().IsTypingFinished455()&&std::strcmp(window.GetNext455().GetLabel(),RF455_GetNormalLanguagePack()->get(106))==0&&!closingMessages(),"actual mouse queue finishes page only");capture(window,"briefing-page0.bgra");++frames;
        window.Continue455();check(window.GetPage455()==1&&!window.IsReady455()&&window.GetTyping455().GetTypingStartTime455()==tick,"next page no initialdelay");
        window.Close();tick+=100;window.Open();check(window.GetPage455()==1&&window.GetTyping455().GetTypingStartTime455()==tick-100,"open later page retains timing");
        while(window.GetPage455()+1<window.GetPageCount455()){window.Continue455();window.Continue455();}window.Continue455();capture(window,"briefing-lastpage.bgra");++frames;window.Continue455();check(closingMessages()==1,"last page posts real event");
        RF455TutorialKeyGuide keys;keys.visible=true;keys.count=2;keys.rows={{{{3,255}},{{17,3}}}};check(view.showKeyGuide(keys)&&window.GetKeys455()&&window.GetKeyFrame455().IsAddedObject(window.GetKeys455()),"actual key guide instance");capture(window,"briefing-guide.bgra");++frames;
        keys.visible=false;check(view.showKeyGuide(keys)&&!window.GetKeyFrame455().IsAddedObject(window.GetKeys455()),"hide retains widget");
        check(view.showRichMessage(message,false)&&!g_pUiScreen->GetCapture455(),"blocked board branch releases screen capture");
        window.SetAutoSize455(TRUE);CGUITextInfo text;text.SetText(const_cast<char*>("Auto size"));window.SetText455(1,&text);check(window.GetTyping455().GetSizeY()==6*(RF455_DefaultTextHeight()+5)+30&&window.GetSizeY()==window.GetTyping455().GetSizeY()+64,"six line autosize");
        window.ShowKeyFrame455(FALSE);window.SetPos(10,60);
        for(BYTE race=0;race<3;++race){tick=1000;window.ShowPortrait455(TRUE,race?2:0,static_cast<BYTE>(race*2));check(window.GetPortraitRace455()==race&&window.GetPortraitRole455()==0&&window.GetSizeX()==611&&window.GetTyping455().GetPosX()==159&&window.GetPortrait455().GetTotal455()==8,"real portrait mapping and 128cell grid");
            char frame[80];std::sprintf(frame,"briefing-portrait%u-idle.bgra",unsigned(race));capture(window,frame);++frames;
            tick=8999;const auto prior=randomQueries;window.Update();check(randomQueries==prior+1&&window.GetPortrait455().GetSpriteInfo()->wFrameNo==0,"portrait before tenth period");tick=9000;window.Update();check(window.GetPortrait455().GetSpriteInfo()->wFrameNo==1&&window.GetPortrait455().GetTotal455()==16&&window.GetPortraitStart455()==9000,"portrait switches at rand0/tenth period");
            tick=9200;delta=0.2f;window.Update();delta=0;check(window.GetPortrait455().GetFrame455()==2&&window.GetPortrait455().GetU()[0]==0.5f,"actual window advances portrait animation cells");
            std::sprintf(frame,"briefing-portrait%u-talk.bgra",unsigned(race));capture(window,frame);++frames;tick=10600;window.Update();check(window.GetPortrait455().GetSpriteInfo()->wFrameNo==0,"talk returns afterone period");
            window.ShowPortrait455(TRUE,3,race*2);check(window.GetPortraitRole455()==1,"role3");window.ShowPortrait455(TRUE,15,race*2);check(window.GetPortraitRole455()==2,"role15");
        }
        window.ShowPortrait455(TRUE,18,0);check(window.GetPortraitRole455()==255,"unmapped role retained invalid");window.ShowPortrait455(FALSE,255,255);check(window.GetSizeX()==462&&window.GetPortraitRace455()==255,"hide portrait restores462caps");
        window.Clear455();window.Continue455();check(closingMessages()==1,"empty page postsclose");g_pUiScreen->SetCapture455(&window);click(window.GetClose455());check(closingMessages()==1,"actual close button mouse queue postsclose");window.Close();check(window.GetPortraitRole455()==255,"close resets portrait IDs");g_pUiScreen->SetCapture455(nullptr);g_pUiScreen->Remove(&window);
    }
    RF455_SetTextTypingClock(oldTyping);RF455_SetGuiAnimationReplay(oldAnimation);RF455_SetBriefingReplay(oldBriefing);
    (g_MainApp.*access(Unload{}))();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");
    std::fprintf(out,"{\"status\":\"PASS\",\"actual_briefing_provider\":true,\"pages\":%u,\"frames\":%u,\"capture_input_message\":true,\"capture_removed_live_object\":true,\"typing_and_continue\":true,\"posted_close_event\":true,\"three_real_portraits\":true,\"portrait_random_timer\":true,\"actual_Tutorial_stage\":false}\n",pageCount,frames);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Briefing window: %s\n",error.what());return 1;}}
