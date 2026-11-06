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
#include "userinterface/guicontroller/guiscrollbar.h"
#include "mainapp.h"
#include "client455_gui_input.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstddef>
#include <stdexcept>
#include <vector>
#include <utility>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
#define FIELD(Tag,TypeName,Class,member) struct Tag{using Type=TypeName Class::*;friend Type access(Tag);};template struct MemberAccess<Tag,&Class::member>;
FIELD(SpriteMember,CSpriteMgr,CMainApp,m_cSpriteMgr)
FIELD(ScreenMember,CGUIScreen,CMainApp,m_cScreen)
struct QueueCreate{using Type=void(*)(WORD);friend Type access(QueueCreate);};struct QueueProcess{using Type=void(*)();friend Type access(QueueProcess);};struct MouseClear{using Type=void(*)();friend Type access(MouseClear);};
struct Load{using Type=BOOL(CMainApp::*)();friend Type access(Load);};struct Unload{using Type=BOOL(CMainApp::*)();friend Type access(Unload);};
template struct MemberAccess<QueueCreate,&CGUIObject::CreateEventQueue>;template struct MemberAccess<QueueProcess,&CGUIObject::EventProcess>;template struct MemberAccess<MouseClear,&CGUIObject::ClearMouseEventBuffer>;template struct MemberAccess<Load,&CMainApp::LoadData>;template struct MemberAccess<Unload,&CMainApp::UnloadData>;
static void check(bool value,const char* why){if(!value)throw std::runtime_error(why);}
struct Row{WORD id;CGUIObject* source;DWORD value;};
struct Observer:IMouseObserver,IMouseMotionObserver,IKeyObserver,IFocusObserver455,IValueObserver455{
    std::vector<Row> rows;
    void MouseEvent(_mouse_event& e){rows.push_back({e.id,e.source,0});}void MouseMotionEvent(_mouse_motion_event& e){rows.push_back({e.id,e.source,0});}
    void KeyEvent(_key_event& e){rows.push_back({e.id,e.source,e.key});}void FocusEvent455(_focus_event455& e){rows.push_back({e.id,e.source,0});}void ValueEvent455(_value_event455& e){rows.push_back({e.id,e.source,e.value});}
    void clear(){rows.clear();}bool has(WORD id)const{for(auto& r:rows)if(r.id==id)return true;return false;}
};
struct Popup:CGUIObject{unsigned closes=0;void CloseMouseModal455()override{++closes;}};
static DWORD now=100;static unsigned queries=0;static SHORT control=0,alt=0;static std::vector<int> keyQueries;
static DWORD replayTime(){++queries;return now;}static SHORT replayKey(int key){keyQueries.push_back(key);return key==VK_CONTROL?control:alt;}
static void drain(){access(QueueProcess{})();}
static BOOL frame(CGUIObject& object,LONG x,LONG y,DWORD buttons){gMouse.x=x;gMouse.y=y;gMouse.z=0;gMouse.button=buttons;gMouseDev.Update();access(MouseClear{})();const BOOL result=object.InputProc();drain();return result;}
static void setup(CGUIObject& object,int x,int y){object.SetPos(x,y);object.SetSize(30,30);object.Show(TRUE);object.Active();}
static void bind(CGUIObject& object,Observer& observer){object.AddMouseEventHandler(&observer);object.AddMouseMotionEventHandler(&observer);object.AddKeyEventHandler(&observer);object.AddFocusHandler455(&observer);}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);check(sizeof(_event_queue_data)==36&&offsetof(_event_queue_data,byKeyCode)==10&&offsetof(_event_queue_data,nValue455)==32,"target event wire layout");
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D init");g_pUiSpriteMgr=&(g_MainApp.*access(SpriteMember{}));g_pUiScreen=&(g_MainApp.*access(ScreenMember{}));check((g_MainApp.*access(Load{}))()!=0,"LoadData");access(QueueCreate{})(128);
    const auto oldClock=RF455_SetGuiInputClock(replayTime);const auto oldKey=RF455_SetGuiKeyState(replayKey);
    {
        Observer events;CGUIObject a,b;setup(a,10,10);setup(b,60,10);bind(a,events);bind(b,events);
        check(frame(a,12,12,_LEFT_BUTTON_DOWN)&&queries==1&&events.has(1),"first press has one timestamp query");frame(a,12,12,0);events.clear();now=400;const auto before=queries;frame(a,12,12,_LEFT_BUTTON_DOWN);check(events.has(7)&&!events.has(8)&&queries==before+2,"doubleclick300 inclusive and two clock queries");frame(a,12,12,0);events.clear();now=401;frame(a,12,12,_LEFT_BUTTON_DOWN);check(events.has(1),"double clears sequence owner");frame(a,12,12,0);events.clear();now=702;frame(a,12,12,_LEFT_BUTTON_DOWN);check(events.has(1)&&!events.has(7),"301milliseconds starts new single");frame(a,12,12,0);
        now=0xffffff80;frame(a,12,12,_LEFT_BUTTON_DOWN);frame(a,12,12,0);events.clear();now=0xac;frame(a,12,12,_LEFT_BUTTON_DOWN);check(events.has(7),"doubleclick DWORD wrap at300");frame(a,12,12,0);events.clear();frame(a,12,12,_RIGHT_BUTTON_DOWN);check(events.has(8)&&!events.has(7)&&CGUIObject::GetRightPressed455()==&a,"right event8 and independent pressed pointer");frame(a,12,12,0);check(!CGUIObject::GetRightPressed455(),"right release clears pointer");events.clear();now=1000;frame(a,12,12,_LEFT_BUTTON_DOWN);check(events.has(1)&&!events.has(7),"right click resets left double sequence");frame(a,12,12,0);
        a.SetMouseInput455(FALSE);access(MouseClear{})();check(!a.InputProc()&&!CGUIObject::GetMouseDetectedObject(),"mouse input flag rejects selection");a.SetMouseInput455(TRUE);
        events.clear();Popup popup;setup(popup,200,10);CGUIObject::SetMouseModal455(&popup);now=1200;frame(b,62,12,_LEFT_BUTTON_DOWN);check(popup.closes==1&&!events.has(1)&&CGUIObject::GetMouseModal455()==&popup,"outside modal closes popup without underlying stroke");frame(b,62,12,0);CGUIObject::SetMouseModal455(&popup);check(popup.closes==2,"same modal replacement calls old callback");CGUIObject::SetMouseModal455(nullptr);check(popup.closes==3&&!CGUIObject::GetMouseModal455(),"modal clear invokes callback");
        CGUIContainer holder;setup(holder,0,0);holder.SetSize(150,90);check(!holder.TryFocus455(),"container defaults focus disabled");holder.Add(&a);holder.Add(&b);CGUIObject front;setup(front,10,10);holder.AddFront455(&front);check(holder.GetAddedObject(0)==&front,"front list insertion");holder.Show(FALSE);CGUIObject child;child.Show(TRUE);holder.Add(&child);check(!child.IsShow(),"Add inherits parent visibility");child.Show(TRUE);holder.Add(&child);check(child.IsShow(),"duplicate Add does not reshow");holder.Add(nullptr);holder.Remove(&child);holder.Show(TRUE);front.SetMouseInput455(FALSE);holder.SetMouseInput455(FALSE);events.clear();now=1401;frame(holder,12,12,_LEFT_BUTTON_DOWN);check(CGUIObject::GetPressedObject()==&a&&events.has(1),"container input still reaches child with parent mouse flag disabled");check(holder.Remove(&a)&&CGUIObject::GetPressedObject()==&a&&CGUIObject::GetMouseDetectedObject()==&a,"Remove retains mouse references to live objects");frame(b,62,12,0);check(!CGUIObject::GetPressedObject()&&events.has(3),"later input releases removed live object");check(!holder.Remove(nullptr)&&holder.Remove(&a),"Remove null0/nonmember1");holder.RemoveAll();
        events.clear();check(a.TryFocus455(),"eligible focus acquired");drain();check(events.has(70),"focus event70");b.Show(FALSE);check(!b.TryFocus455()&&CGUIObject::GetFocusedObject()==&a,"invalid focus candidate preserves old pointer");drain();check(events.has(71)&&a.IsFocused455(),"failed candidate emitted old blur before eligibility");b.Show(TRUE);check(b.TryFocus455(),"new focus");drain();check(CGUIObject::GetFocusedObject()==&b,"new focus pointer");b.DisableFocus();drain();check(!CGUIObject::GetFocusedObject(),"DisableFocus kills eligible focus");a.TryFocus455();drain();a.Show(FALSE);a.KillFocus455();check(CGUIObject::GetFocusedObject()==&a,"hidden focused object leaves stale pointer per predicate");a.Show(TRUE);a.KillFocus455();drain();check(!CGUIObject::GetFocusedObject(),"shown focus kill clears pointer");
        a.TryFocus455();drain();events.clear();a.MsgProc(nullptr,WM_KEYDOWN,'A',0);a.MsgProc(nullptr,WM_CHAR,'A',0);a.MsgProc(nullptr,WM_KEYDOWN,'B',0);drain();check(events.rows.size()==2&&events.rows[0].value=='A'&&events.rows[1].value=='B',"queue retains different keys but dedups same key");
        events.clear();control=static_cast<SHORT>(0x8000);keyQueries.clear();a.MsgProc(nullptr,WM_KEYDOWN,'C',0);drain();check(events.rows.empty()&&keyQueries==std::vector<int>{VK_CONTROL},"Ctrl filtering short circuits Alt");control=0;alt=static_cast<SHORT>(0x8000);a.MsgProc(nullptr,WM_CHAR,'C',0);drain();check(events.rows.empty(),"Alt filters character");alt=0;
        for(auto pair:{std::pair<int,const char*>{16,"QWERTYUIOP"},{30,"ASDFGHJKL"},{44,"ZXCVBNM"}})for(int i=0;pair.second[i];++i)check(RF455_ProcessKeyScan((pair.first+i)<<16)==pair.second[i],"PROCESSKEY fixed QWERTY scan table");check(RF455_ProcessKeyScan(26<<16)==255&&RF455_ProcessKeyScan(0x40100000)==255,"unmapped/full-high-half scans returnFF");a.MsgProc(nullptr,WM_KEYDOWN,229,16<<16);a.MsgProc(nullptr,WM_CHAR,229,0x40100000);drain();check(events.rows.size()==2&&events.rows[0].value=='Q'&&events.rows[1].value==255,"PROCESSKEY actual queued byte conversion");
        a.Disable();events.clear();a.MsgProc(nullptr,WM_CHAR,'D',0);drain();check(events.has(20),"disabled-but-focused key still uses focus predicate");a.Enable();a.KillFocus455();drain();keyQueries.clear();check(a.MsgProc(nullptr,WM_CHAR,'E',0)==0&&keyQueries.empty(),"unfocused key skips OS key query");
        Observer second;events.clear();_event_queue_data queued;queued.pSource=&a;queued.pEventHandler=static_cast<IValueObserver455*>(&events);queued.wEventID=80;queued.nValue455=1;CGUIObject::SendEvent(queued);queued.pEventHandler=static_cast<IValueObserver455*>(&second);queued.nValue455=2;CGUIObject::SendEvent(queued);queued.byKeyCode=1;queued.nValue455=3;CGUIObject::SendEvent(queued);queued.pEventHandler=static_cast<IFocusObserver455*>(&events);queued.wEventID=79;CGUIObject::SendEvent(queued);queued.pEventHandler=nullptr;queued.wEventID=90;CGUIObject::SendEvent(queued);drain();check(events.rows.size()==2&&events.rows[0].value==1&&events.rows[1].id==79&&second.rows.size()==1&&second.rows[0].value==3,"focus/value dispatch and source/id/key dedup ignores handler/value");
        gMouse.button=_MIDDLE_BUTTON_DOWN;gMouseDev.Update();check(gMouseDev.IsStroked(3)&&gMouseDev.IsPressed(3)&&!gMouseDev.IsPressed(R_BUTTON),"middle button device priority");gMouse.button=0;gMouseDev.Update();
        CGUIScrollbar ordinary;ordinary.SetPos(200,100);POINT arrow={10,10};ordinary.SetTopArrowSize(arrow);ordinary.SetBottomArrowSize(arrow);ordinary.SetSize(12,100);ordinary.SetAmount(20,10);ordinary.Show(TRUE);ordinary.GetTopArrow455().SoundOn(FALSE);now=2000;frame(ordinary,202,102,_LEFT_BUTTON_DOWN);check(ordinary.GetCurrentAmount()==10,"ordinary base arrow has no invented observer binding");frame(ordinary,202,102,0);
        CGUIScrollbarEX extended;extended.SetPos(250,100);extended.SetTopArrowSize(arrow);extended.SetBottomArrowSize(arrow);extended.SetSize(12,100);extended.SetAmount(20,10);extended.Show(TRUE);extended.GetTopArrow455().SoundOn(FALSE);now=2100;frame(extended,252,102,_LEFT_BUTTON_DOWN);check(extended.GetCurrentAmount()==9,"EX arrow retains explicit observer binding");frame(extended,252,102,0);
    }
    RF455_SetGuiInputClock(oldClock);RF455_SetGuiKeyState(oldKey);(g_MainApp.*access(Unload{}))();R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* result=std::fopen("result.json","wb");check(result!=nullptr,"result");std::fprintf(result,"{\"status\":\"PASS\",\"codepage\":%u,\"double7_right8\":true,\"threshold_wrap_clock\":true,\"modal_and_input_flags\":true,\"container_main_list_contracts\":true,\"focus_order_and_predicate\":true,\"key_scan_and_modifier\":true,\"key_dedup_focus_value_queue\":true,\"middle_button\":true,\"ordinary_unbound_EX_bound\":true,\"full_GUI_IME\":false,\"other_container_layers\":false,\"full_Tutorial\":false}\n",RF455_GetNormalLanguagePack()->codepage);std::fclose(result);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"GUI input: %s\n",error.what());return 1;}}
