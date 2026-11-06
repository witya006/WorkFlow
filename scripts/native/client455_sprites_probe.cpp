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
#include "client455_sprites.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
extern CMainApp g_MainApp;
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct SpriteMember{using Type=CSpriteMgr CMainApp::*;friend Type access(SpriteMember);};
struct ScreenMember{using Type=CGUIScreen CMainApp::*;friend Type access(ScreenMember);};
struct LoadMethod{using Type=BOOL(CMainApp::*)();friend Type access(LoadMethod);};
struct UnloadMethod{using Type=BOOL(CMainApp::*)();friend Type access(UnloadMethod);};
template struct MemberAccess<SpriteMember,&CMainApp::m_cSpriteMgr>;
template struct MemberAccess<ScreenMember,&CMainApp::m_cScreen>;
template struct MemberAccess<LoadMethod,&CMainApp::LoadData>;
template struct MemberAccess<UnloadMethod,&CMainApp::UnloadData>;
#define REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Sprite failure line%d\n",__LINE__);return 1;}}while(0)
static DWORD readWord(FILE*f){DWORD value=0;return std::fread(&value,4,1,f)==1?value:0xffffffff;}
static int verify(CSprite*s,unsigned&count,unsigned&formats){
    REQUIRE(s);FILE*f=std::fopen(s->GetFileName(),"rb");REQUIRE(f);
    REQUIRE(readWord(f)==0x3f8ccccd);const DWORD actions=readWord(f);REQUIRE(actions==s->GetMaxActions());
    for(DWORD a=0;a<actions;++a){const DWORD frames=readWord(f);REQUIRE(frames==s->GetMaxFrames(a));
        for(DWORD i=0;i<frames;++i){DWORD h[6];REQUIRE(std::fread(h,4,6,f)==6);std::vector<BYTE>raw(h[5]);REQUIRE(std::fread(raw.data(),1,raw.size(),f)==raw.size());
            REQUIRE(s->GetSpriteOrgXL(a,i)==h[1]&&s->GetSpriteOrgYL(a,i)==h[2]&&s->GetSpriteXL(a,i)==h[3]&&s->GetSpriteYL(a,i)==h[4]);
            auto*texture=static_cast<IDirect3DTexture9*>(s->GetD3D8TexPtr(a,i));REQUIRE(texture);D3DSURFACE_DESC desc={};REQUIRE(SUCCEEDED(texture->GetLevelDesc(0,&desc)));
            REQUIRE(desc.Format==h[0]&&desc.Width==h[3]&&desc.Height==h[4]);D3DLOCKED_RECT lock={};REQUIRE(SUCCEEDED(texture->LockRect(0,&lock,nullptr,D3DLOCK_READONLY)));
            unsigned rows=h[4],stride=0;
            switch(h[0]){case D3DFMT_DXT1:rows/=4;stride=h[3]*2;formats|=1;break;case D3DFMT_DXT5:rows/=4;stride=h[3]*4;formats|=2;break;case D3DFMT_A8R8G8B8:stride=h[3]*4;formats|=4;break;case D3DFMT_R5G6B5:case D3DFMT_A1R5G5B5:stride=h[3]*2;formats|=8;break;default:REQUIRE(false);}
            REQUIRE(rows*stride==raw.size()&&lock.Pitch>=static_cast<int>(stride));
            for(unsigned y=0;y<rows;++y)REQUIRE(!std::memcmp(static_cast<BYTE*>(lock.pBits)+y*lock.Pitch,raw.data()+y*stride,stride));
            texture->UnlockRect(0);++count;
        }
    }
    REQUIRE(std::fgetc(f)==EOF);std::fclose(f);return 0;
}
static unsigned width=0,height=0;
static std::vector<BYTE>capture(IDirect3DDevice9*d){
    IDirect3DSurface9*target=nullptr,*memory=nullptr;std::vector<BYTE>out;
    if(FAILED(d->GetRenderTarget(0,&target)))return out;D3DSURFACE_DESC desc={};target->GetDesc(&desc);width=desc.Width;height=desc.Height;
    if((desc.Format==D3DFMT_X8R8G8B8||desc.Format==D3DFMT_A8R8G8B8)&&SUCCEEDED(d->CreateOffscreenPlainSurface(width,height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr))&&SUCCEEDED(d->GetRenderTargetData(target,memory))){D3DLOCKED_RECT lock={};if(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY))){out.resize(width*height*4);for(unsigned y=0;y<height;++y)std::memcpy(out.data()+4*width*y,static_cast<BYTE*>(lock.pBits)+y*lock.Pitch,width*4);memory->UnlockRect();}}
    if(memory)memory->Release();target->Release();return out;
}
int main(int argc,char**argv){
    if(argc!=2)return 200;SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    REQUIRE(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData());
    FILE*names=std::fopen("filenames.txt","rb");REQUIRE(names);char expected[128];unsigned n=0;
    while(std::fgets(expected,sizeof(expected),names)){expected[std::strcspn(expected,"\r\n")]=0;REQUIRE(RF455_SpriteFilename(n)&&!std::strcmp(expected,RF455_SpriteFilename(n)));char path[260];REQUIRE(RF455_SelectSpritePath(n,path,sizeof(path)));std::string local="./SpriteImage/"+std::string(RF455_GetNormalNationPaths()->folder)+"/"+expected;const DWORD attr=GetFileAttributesA(local.c_str());const std::string selected=attr==INVALID_FILE_ATTRIBUTES?"./SpriteImage/Common/"+std::string(expected):local;REQUIRE(selected==path);++n;}
    std::fclose(names);REQUIRE(n==55&&!RF455_SpriteFilename(55));char untouched[260]="untouched";REQUIRE(!RF455_SelectSpritePath(55,untouched,sizeof(untouched))&&!RF455_SelectSpritePath(255,untouched,sizeof(untouched))&&!std::strcmp(untouched,"untouched"));
    InitR3Engine();auto*state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();REQUIRE(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)));
    auto*d=GetD3dDevice();REQUIRE(d);const ULONG before=d->AddRef()-1;d->Release();
    auto&manager=g_MainApp.*access(SpriteMember{});auto&screen=g_MainApp.*access(ScreenMember{});g_pUiSpriteMgr=&manager;g_pUiScreen=&screen;
    REQUIRE((g_MainApp.*access(LoadMethod{}))()==TRUE);auto*mouse=manager.GetSprite(SP_ID_MOUSE);auto*common=manager.GetSprite(SP_ID_COMMON);REQUIRE(mouse&&common);
    REQUIRE(std::string(mouse->GetFileName())=="./SpriteImage/Common/mouse.spr");REQUIRE(std::string(common->GetFileName())=="./SpriteImage/"+std::string(RF455_GetNormalNationPaths()->folder)+"/common.spr");
    REQUIRE((g_MainApp.*access(LoadMethod{}))()==FALSE);manager.LoadSprite(SP_ID_MOUSE);manager.LoadSprite(SP_ID_COMMON);REQUIRE(manager.GetSprite(SP_ID_MOUSE)==mouse&&manager.GetSprite(SP_ID_COMMON)==common);
    unsigned count=0,formats=0;REQUIRE(verify(mouse,count,formats)==0&&verify(common,count,formats)==0);REQUIRE(count==562&&formats==15);
    REQUIRE(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()));d->SetRenderState(D3DRS_ZENABLE,FALSE);
    screen.GetMouse()->SetPos(20,20);screen.GetMouse()->Show(TRUE);REQUIRE(screen.GetMouse()->Draw());common->SetAction(0);common->SetFrame(0);common->DrawSprite(80,20);
    REQUIRE(SUCCEEDED(d->EndScene()));const auto pixels=capture(d);REQUIRE(!pixels.empty());D3DVIEWPORT9 vp={};d->GetViewport(&vp);unsigned colored=0;for(unsigned y=vp.Y;y<vp.Y+vp.Height;++y)for(unsigned x=vp.X;x<vp.X+vp.Width;++x){DWORD p;std::memcpy(&p,pixels.data()+4*(y*width+x),4);colored+=(p&0xffffff)!=0x102030;}REQUIRE(colored>10);
    FILE*frame=std::fopen("sprite-frame.bgra","wb");REQUIRE(frame);REQUIRE(std::fwrite(pixels.data(),1,pixels.size(),frame)==pixels.size());std::fclose(frame);
    d->SetTexture(0,nullptr);REQUIRE((g_MainApp.*access(UnloadMethod{}))()==TRUE);REQUIRE(!manager.GetSprite(SP_ID_MOUSE)&&!manager.GetSprite(SP_ID_COMMON));const ULONG after=d->AddRef()-1;d->Release();REQUIRE(before==after);
    g_pUiSpriteMgr=nullptr;g_pUiScreen=nullptr;R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE*out=std::fopen(argv[1],"wb");REQUIRE(out);std::fprintf(out,"{\"status\":\"PASS\",\"target_names\":55,\"frames_payload_equal\":%u,\"format_bits\":%u,\"normal_mainapp_load_data\":true,\"real_gui_mouse\":true,\"cache_reused\":true,\"device_refs_preserved\":true,\"width\":%u,\"height\":%u,\"colored_pixels\":%u}\n",count,formats,width,height,colored);std::fclose(out);return 0;
}
