#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "userinterface/gamewindow/guiinventorywindow.h"
#include "mainapp.h"
#include "client455_gui_timer.h"
#include "client455_gui_input.h"
#include "client455_icon_links.h"
#include "client455_linker_window.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <new>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
static DWORD now=0,clockCalls=0;static bool advancing=false;
static DWORD clock455(){++clockCalls;return advancing?now++:now;}
static FILE* fixture(const char* name,const char* magic,unsigned count){FILE* f=std::fopen(name,"rb");check(f!=nullptr,"fixture");char header[4];unsigned n;check(std::fread(header,1,4,f)==4&&!std::memcmp(header,magic,4)&&std::fread(&n,4,1,f)==1&&n==count,"fixture header");return f;}
static void end(FILE* f){check(std::fgetc(f)==EOF,"fixture extent");std::fclose(f);}
static std::vector<_D3DR3TLVERTEX_TEX1> received;
static void sink(void*,const _D3DR3TLVERTEX_TEX1* p){received.insert(received.end(),p,p+3);}
static void cpu(){
    alignas(RF455GuiTimer) unsigned char bytes[sizeof(RF455GuiTimer)];std::memset(bytes,0x5a,sizeof(bytes));auto* placed=new(bytes)RF455GuiTimer;
    for(unsigned i=0;i<3;++i){unsigned x,y;std::memcpy(&x,&placed->Vertices455()[i].x,4);std::memcpy(&y,&placed->Vertices455()[i].y,4);check(x==0x5a5a5a5a&&y==x,"constructor leaves XY untouched");}
    check(!placed->IsShow()&&!placed->IsStarted455(),"timer constructor state");placed->~RF455GuiTimer();
    RF455GuiTimer timer;timer.Show(TRUE);timer.SetPos(12,34);timer.SetSize(32,38);timer.State455()={10,20,30,40,50,60};timer.Reset455();
    const RF455GuiTimerState zero={};check(!std::memcmp(&timer.State455(),&zero,sizeof(zero))&&timer.GetPosX()==12&&timer.IsShow(),"reset selected fields only");
    FILE* f=fixture("timer-states.bin","TS98",175);
    for(unsigned i=0;i<175;++i){unsigned row[8];check(std::fread(row,4,8,f)==8,"state row");now=row[1];clockCalls=0;timer.State455().duration=row[0];timer.State455().angle=123.25f;timer.Start455(static_cast<LONG>(row[2]));check(clockCalls==1&&timer.State455().elapsedOffset==row[4]&&timer.State455().startedAt==row[1],"start sentinel/raw signed offset");now=row[3];timer.Update();
        check(clockCalls==2&&timer.State455().remaining==row[5]&&timer.State455().started==row[6]&&!std::memcmp(&timer.State455().angle,&row[7],4),"175 unsigned wrap/signed remainder/state oracles");
        const auto old=timer.State455();timer.State455().started=0;const auto stopped=timer.State455();timer.Update();check(clockCalls==2&&!std::memcmp(&stopped,&timer.State455(),28),"stopped update no clock");timer.State455()=old;
    }end(f);
    f=fixture("timer-labels.bin","TL98",112);for(unsigned i=0;i<112;++i){unsigned row[8];check(std::fread(row,4,8,f)==8,"label row");RF455TimerLabel label={0x12345678,{123,456},99,1.25f};const auto value=RF455_TimerLabel455(row[0],static_cast<BYTE>(row[1]),label);
        check(value==row[2]&&label.color==row[3]&&label.offset.x==static_cast<LONG>(row[4])&&label.offset.y==static_cast<LONG>(row[5])&&label.unit==row[6]&&!std::memcmp(&label.scale,&row[7],4),"strict thresholds/context geometry/partial label writes");}end(f);
    f=fixture("timer-rays.bin","TR98",57);unsigned triangleCount=0;
    for(unsigned i=0;i<57;++i){unsigned row[6];check(std::fread(row,4,6,f)==6,"ray row");timer.SetPos(row[0],row[1]);timer.SetSize(row[2],row[3]);timer.State455().started=7;std::memcpy(&timer.State455().angle,&row[4],4);received.clear();const auto calls=clockCalls;check(timer.DrawWithSink455(sink,nullptr)==TRUE&&clockCalls==calls&&timer.IsStarted455()==7,"draw separate from clock/update/raw BOOL");check(received.size()==row[5]*3,"triangle count");triangleCount+=row[5];
        std::vector<_D3DR3TLVERTEX_TEX1> expected(received.size());check(std::fread(expected.data(),28,expected.size(),f)==expected.size(),"ray vertices");check(expected.empty()||!std::memcmp(expected.data(),received.data(),28*expected.size()),"171 triangles exact float32 fields");
    }end(f);check(triangleCount==171,"triangle domain");
    timer.SetPos(20,30);timer.SetSize(32,38);timer.State455().angle=0;timer.State455().started=1;RECT full={20,30,52,68},part={21,30,52,68};received.clear();check(timer.DrawWithSink455(sink,nullptr,&full)&&received.size()==15,"inclusive clip fit");received.clear();check(!timer.DrawWithSink455(sink,nullptr,&part)&&received.empty(),"timer partial clip fully rejected");timer.Show(FALSE);check(!timer.DrawWithSink455(sink,nullptr),"hidden timer");
    CGUIItem original,copy;original.SetObjectIndex455(8);original.SetItemID(123);original.Timer455().State455()={5000,12,77,9,1234,90};original.SetPos(44,55);original.SetSize(38,38);copy.SetPos(100,200);copy.SetData(&original);
    check(!std::memcmp(&original.Timer455().State455(),&copy.Timer455().State455(),28)&&copy.Timer455().GetPosX()==100&&copy.Timer455().GetPosY()==200&&copy.Timer455().GetSizeX()==38,"real SetData timer copy and destination position");copy.Timer455().State455().started=0;copy.SetEmpty();check(copy.Timer455().State455().remaining==1234,"empty preserves stopped remaining");copy.Timer455().State455().started=1;copy.SetEmpty();check(!std::memcmp(&copy.Timer455().State455(),&zero,28)&&copy.m_wNum==1,"empty resets running timer");
    CGUISFItem derived;derived.SetObjectIndex455(1);derived.SetPos(13,17);derived.SetSize(23,23);now=100;derived.BeginDelayAnimation(1000);now=600;derived.Update();check(derived.IsDelayAnimation()&&derived.Timer455().State455().remaining==500&&derived.Timer455().GetPosX()==13&&derived.Timer455().GetSizeX()==23,"typed derived query/update/geometry");derived.StopDelayAnimation455();
}
template<class Draw>static unsigned capture(Draw draw,const char* name){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");draw();check(SUCCEEDED(device->EndScene()),"end");IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");FILE* f=std::fopen(name,"wb");check(f!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+480;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;check(std::fwrite(row,4,640,f)==640,"write");for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}std::fclose(f);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);const auto oldClock=RF455_SetGuiInputClock(clock455);auto& runtime=RF455_GameItems();auto& links=RF455_GameIconLinks();links.clear();cpu();check(runtime.loadFiles("item.edf","nd-zh-tw.edf","quest.edf","character.edf","base.edf","zh-tw.edf"),"real metadata");check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");const auto baseline=GetDmallocSize();
    {
        CGUIInventoryBoard inventory;CBoardObject item;CLinkBoard board;board.Create(6,5,10);for(BYTE bank=0;bank<5;++bank)check(board.AddPack(bank),"pack");FILE* f=fixture("metadata-samples.bin","MS94",16);unsigned sample[3];check(std::fread(sample,4,3,f)==3,"sample");std::fclose(f);item.SetItem455(runtime.create(sample[0],sample[1],sample[2]));check(inventory.TakeInItem455(0,&item,0)&&board.Add(0,0,&item)&&board.Add(4,9,&item),"actual original plus two clone owners");
        auto* icon=item.GetIcon();auto* first=board.LinkerIcon455(0,0);auto* last=board.LinkerIcon455(4,9);links.registerIcon(*first);links.registerIcon(*icon);now=100;clockCalls=0;advancing=true;icon->BeginDelayAnimation455(60000,123);advancing=false;
        check(clockCalls==5&&icon->Timer455().State455().startedAt==104&&first->Timer455().State455().startedAt==103&&last->Timer455().State455().startedAt==102,"real registry fanout preserves duplicates/self/separate clock calls");check(links.unregisterIcon(*icon)&&links.unregisterIcon(*first),"remove explicit extra memberships");
        now=10000;icon->Update();first->Update();last->Update();check(icon->Timer455().State455().remaining==49981&&first->Timer455().State455().remaining==49980&&last->Timer455().State455().remaining==49979,"actual ordinary Update reaches each timer");check(RF455_LinkerIconDelaying455(first),"actual typed Linker query");icon->StopDelayAnimation455();check(!RF455_LinkerIconDelaying455(first)&&!last->Timer455().IsStarted455(),"actual stop fanout");
        icon->SetPos(80,80);icon->SetSize(64,64);first->SetPos(180,80);last->SetPos(280,80);icon->Show(TRUE);first->Show(TRUE);last->Show(TRUE);auto draw=[&](){check(icon->Draw()&&first->Draw()&&last->Draw(),"real typed draws");};check(capture(draw,"timer-idle.bgra")>500,"idle pixels");
        now=100;icon->BeginDelayAnimation455(60000);now=15100;icon->Update();first->Update();last->Update();check(capture(draw,"timer-45seconds.bgra")>500,"yellow timers");
        now=52100;icon->Update();first->Update();last->Update();check(capture(draw,"timer-9seconds.bgra")>500,"red timers");
        now=100;icon->BeginDelayAnimation455(120000);now=10100;icon->Update();first->Update();last->Update();check(capture(draw,"timer-minute.bgra")>500,"minute timers");
        RECT partial={82,80,144,144};check(capture([&](){icon->Draw(partial);},"timer-partial-clip.bgra")>100,"icon clipped,timer rejected");
        icon->StopDelayAnimation455();check(capture(draw,"timer-reset.bgra")>500,"reset pixels");board.Clear();item.Clear();check(!links.linkCount()&&runtime.manager.size()==0,"owners released");
    }
    links.clear();gSpriteMgr.UnloadTargetSprites455();check(GetDmallocSize()==baseline,"sprite allocator balanced");R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();RF455_SetGuiInputClock(oldClock);FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");std::fprintf(out,"{\"status\":\"PASS\",\"state_cases\":175,\"label_cases\":112,\"radial_cases\":57,\"radial_triangles\":171,\"GPU_frames\":6,\"ctor_partial_writes\":true,\"ordinary_copy_empty_update\":true,\"actual_registry_fanout\":true,\"actual_Linker_timer_query\":true,\"all_owners_released\":true,\"sprite_allocator_balanced\":true,\"full_gameplay\":false,\"full_client\":false}\n");std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){if(info->ExceptionRecord->ExceptionCode==0xe06d7363)return EXCEPTION_CONTINUE_SEARCH;std::fprintf(stderr,"exception=%08lx at ownRVA=%08lx\n",info->ExceptionRecord->ExceptionCode,DWORD(info->ExceptionRecord->ExceptionAddress)-DWORD(GetModuleHandleA(nullptr)));return EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"GUI timer:%s\n",e.what());return 1;}}
