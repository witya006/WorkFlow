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
#include "userinterface/gamewindow/guiinventorywindow.h"
#include "client455_money.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
extern CMainApp g_MainApp;
static void check(bool ok,const char* text){if(!ok)throw std::runtime_error(text);}
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
#define FIELD(Tag,T,C,member) struct Tag{using Type=T C::*;friend Type access(Tag);};template struct MemberAccess<Tag,&C::member>;
FIELD(SpriteMember,CSpriteMgr,CMainApp,m_cSpriteMgr)
FIELD(ScreenMember,CGUIScreen,CMainApp,m_cScreen)
FIELD(DalantTitle,CGUIText,CGUIInventoryWindow,m_uiDalantTitle)
FIELD(GoldTitle,CGUIText,CGUIInventoryWindow,m_uiGoldTitle)
FIELD(DalantLabel,CGUIText,CGUIInventoryWindow,m_uiDalant)
FIELD(GoldLabel,CGUIText,CGUIInventoryWindow,m_uiGold)
struct Load{using Type=BOOL(CMainApp::*)();friend Type access(Load);};template struct MemberAccess<Load,&CMainApp::LoadData>;
struct Unload{using Type=BOOL(CMainApp::*)();friend Type access(Unload);};template struct MemberAccess<Unload,&CMainApp::UnloadData>;
static unsigned capture(CGUIText& a,CGUIText& b,CGUIText& c,CGUIText& d,const char* name){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(device->BeginScene()),"begin");a.Draw();b.Draw();c.Draw();d.Draw();check(SUCCEEDED(device->EndScene()),"end");
    IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc;target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr))&&SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");
    D3DLOCKED_RECT lock;check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");FILE* out=std::fopen(name,"wb");check(out!=nullptr,"capture");unsigned pixels=0;
    for(unsigned y=0;y<480;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const char*>(lock.pBits)+y*lock.Pitch);std::fwrite(row,4,640,out);for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(out);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    g_pUiSpriteMgr=&(g_MainApp.*access(SpriteMember{}));g_pUiScreen=&(g_MainApp.*access(ScreenMember{}));check((g_MainApp.*access(Load{}))()!=0,"actual fonts/UI load");
    unsigned cases=0,frames=0,pixels=0;unsigned short original;__asm fnstcw original
    {
        CAvatar avatar;check(!avatar.GetGold()&&!avatar.GetDalant(),"real Avatar constructor money zero");avatar.SetClientStage455(2);avatar.SetSkipTutorial455(0x12345678);
        CGUIInventoryWindow inventory;auto* saved=g_pUiInventWindow;g_pUiInventWindow=nullptr;avatar.SetGold(4294967297LL);avatar.SetDalant(-4294967297LL);check(avatar.GetGold()==4294967297LL&&avatar.GetDalant()==-4294967297LL,"actual64-bit Avatar optional-null UI branch");g_pUiInventWindow=&inventory;
        auto& dt=inventory.*access(DalantTitle{});auto& gt=inventory.*access(GoldTitle{});auto& dl=inventory.*access(DalantLabel{});auto& gl=inventory.*access(GoldLabel{});
        dt.GetFont()->dwColor=gt.GetFont()->dwColor=dl.GetFont()->dwColor=gl.GetFont()->dwColor=0xffe3e0d9;
        dt.Show(TRUE);gt.Show(TRUE);dl.Show(TRUE);gl.Show(TRUE);
        FILE* fixture=std::fopen("money-cases.txt","rb"),*trace=std::fopen("money-trace.txt","wb");check(fixture&&trace,"case files");unsigned mode;__int64 value;char expected[64];
        while(std::fscanf(fixture,"%u %I64d %63s",&mode,&value,expected)==3){
            const unsigned variant=cases%3;dt.SetString(const_cast<char*>(variant==0?"D":variant==1?"LONG DALANT":"LABEL"));gt.SetString(const_cast<char*>(variant==0?"LONG GOLD":variant==1?"G":"LABEL"));
            //Ordinary titles share a right column. The equal-width case also
            //distinguishes the target's <= tie branch without overlapping text.
            dt.SetPos(600-dt.GetSizeX(),100);gt.SetPos(600-gt.GetSizeX()-(variant==2?20:0),140);
            const LONG right=(dt.GetSizeX()<=gt.GetSizeX()?gt.GetPosX():dt.GetPosX())-10;
            unsigned short entered=static_cast<unsigned short>((original&~0x0c00)|(mode<<10)|0x3f);__asm fldcw entered
            char actual[64]={};RF455_FormatMoney(value,actual);check(!std::strcmp(actual,expected),"independent signed64/FP formatting oracle");
            avatar.SetDalant(value);avatar.SetGold(value);
            check(avatar.GetDalant()==value&&avatar.GetGold()==value&&inventory.GetOwnDalant()==value&&inventory.GetOwnGold()==value,"real Avatar->inventory64-bit chain");
            check(!std::strcmp(inventory.GetDalantStr(),expected)&&!std::strcmp(inventory.GetGoldStr(),expected),"real inventory money labels");
            check(dl.GetPosX()+dl.GetSizeX()==right&&gl.GetPosX()+gl.GetSizeX()==right&&dl.GetPosY()==100&&gl.GetPosY()==140,"wider title alignment and row-specific y");
            unsigned short after;__asm fnstcw after
            check(after==entered,"formatter restores x87 control word");__asm fldcw original
            std::fprintf(trace,"%u %I64d %s %ld %ld\n",mode,value,actual,long(dl.GetPosX()),long(gl.GetPosX()));++cases;
            if(mode==0&&(value==4294967297LL||value==9223372036854775807LL||value==(-9223372036854775807LL-1))){char name[40];std::sprintf(name,"money-%u.bgra",frames);pixels+=capture(dt,gt,dl,gl,name);++frames;}
        }
        std::fclose(trace);std::fclose(fixture);check(cases>=80&&frames==3&&pixels>100,"case/readback coverage");
        check(avatar.GetClientStage455()==2&&avatar.GetSkipTutorial455()==0x12345678,"money fields do not clobber stage/skip source state");
        auto* first=RF455_GetMoneyText(1234);check(!std::strcmp(first,"1,234"),"static formatter first");auto* next=RF455_GetMoneyText(5);check(first==next&&!std::strcmp(first,"5"),"shared32-byte output lifetime");RF455_FormatMoney(1,nullptr);g_pUiInventWindow=saved;
    }
    __asm fldcw original
    (g_MainApp.*access(Unload{}))();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result");
    std::fprintf(out,"{\"status\":\"PASS\",\"cases\":%u,\"rounding_modes\":4,\"real_Avatar_inventory_chain\":true,\"signed64_storage\":true,\"wider_title_alignment\":true,\"shared_text_buffer\":true,\"frames\":%u,\"colored_pixels\":%u,\"full_inventory_currency_network\":false,\"actual_Tutorial_stage\":false}\n",cases,frames,pixels);std::fclose(out);return 0;
}
int main(){try{return run();}catch(const std::exception& error){std::fprintf(stderr,"money-probe:%s\n",error.what());return 1;}}
