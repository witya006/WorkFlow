#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "client455_item_atlas.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
template<class Draw>static unsigned capture(Draw draw,const char* name){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");draw();check(SUCCEEDED(device->EndScene()),"end");
    IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");FILE* f=std::fopen(name,"wb");check(f!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+480;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;check(std::fwrite(row,4,640,f)==640,"write");for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(f);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    const auto before=GetDmallocSize();auto* item=gSpriteMgr.GetTargetSprite455(8);auto* unit=gSpriteMgr.GetTargetSprite455(19);auto* border=gSpriteMgr.GetTargetSprite455(6);check(item&&unit&&border,"realitem/unitparts/inventory sprites");
    FILE* f=std::fopen("atlas-cases.bin","rb");check(f!=nullptr,"oracle");char magic[4];unsigned count=0;check(std::fread(magic,1,4,f)==4&&!std::memcmp(magic,"AT93",4)&&std::fread(&count,4,1,f)==1,"oracle header");
    unsigned failures=0,wrapped=0;
    for(unsigned i=0;i<count;++i){unsigned row[12];check(std::fread(row,4,12,f)==12,"oracle row");const unsigned kind=row[0],id=row[1],cls=row[2];const int width=static_cast<int>(row[3]);auto* sprite=kind==0?item:kind==1?unit:border;
        if(!kind){std::uint32_t adjusted=id;std::uint8_t page=0;const bool valid=RF455_ItemAtlasPage(cls,adjusted,page);check(valid==(row[4]!=0)&&adjusted==row[5]&&page==row[6],"binary-decoded page table and ID rebasing");}
        SPRITE_INFO raw={sprite,0xaaaa,0xbbbb};const bool found=kind==0?RF455_ItemSpriteSearch455(id,cls,width,raw):kind==1?RF455_UnitPartsSearch455(id,cls,width,raw):RF455_DefaultSpriteSearch455(id,raw);
        if(found!=(row[7]!=0)||raw.pSprite!=sprite||raw.wActionNo!=row[8]||raw.wFrameNo!=row[9]){std::fprintf(stderr,"case%u/kind%u/id%u/class%x/width%d got%u,%u,%u expected%u,%u,%u\n",i,kind,id,cls,width,found,raw.wActionNo,raw.wFrameNo,row[7],row[8],row[9]);throw std::runtime_error("rawcallback vs independent geometry oracle");}
        SPRITE_INFO managed={nullptr,0xaaaa,0xbbbb};const BOOL selected=gSpriteMgr.GetTargetSpriteInfo455(kind==0?8:kind==1?19:6,id,cls,width,managed);check((selected!=0)==found&&managed.pSprite==sprite&&managed.wActionNo==row[10]&&managed.wFrameNo==row[11],"actualmanager fallbackzero on callbackfailure");failures+=!found;
        if(kind!=2&&found&&width>0){const unsigned columns=sprite->GetSpriteOrgXL()/width;wrapped+=row[5]/columns>65535;}
    }
    check(std::fgetc(f)==EOF&&count==880&&failures&&wrapped,"fixture extent and unsigned row wrap");std::fclose(f);
    SPRITE_INFO missing={nullptr,0xaaaa,0xbbbb};check(!RF455_ItemSpriteSearch455(0,0,64,missing)&&missing.wActionNo==0xaaaa&&missing.wFrameNo==0xbbbb,"missing sprite rawcallback preserves output");check(!gSpriteMgr.GetTargetSpriteInfo455(7,0,0,64,missing)&&!missing.pSprite&&missing.wActionNo==0xaaaa&&missing.wFrameNo==0xbbbb,"missingunit leaves manageroutput unchanged");
    struct Sample{unsigned type,cls,id;};const Sample samples[]={{0,0x10000,1},{0,0,1},{0,0x20d00,1},{0,0x30200,1024},{0,0x30200,2048},{1,0,1},{3,0,1},{2,0,1},{4,0,1},{6,0,1},{7,0,1},{8,0,1},{5,3,1},{0,0x80000,1},{0,0x11d00,1},{0,0x31600,1}};
    CGUIItem icon;icon.Show(TRUE);icon.SetNum(1);icon.SetUsable(TRUE);
    const unsigned grid=capture([&](){for(unsigned i=0;i<16;++i){const auto& s=samples[i];icon.SetIconType455(static_cast<BYTE>(s.type));icon.SetItemID(s.cls);icon.SetSpriteID(s.id);icon.SetPos(24+90*(i%6),24+90*(i/6));const int side=i<6?32:64;icon.SetSize(side,side);icon.SetGrade455(static_cast<BYTE>(i%12));icon.SetSprite();check(icon.GetSpriteInfo()->pSprite==(s.type==5?unit:item)&&icon.GetSizeX()==side&&icon.GetSizeY()==side,"actualGUIItem automatic sprite/size");check(icon.Draw()!=0,"automatic draw");}},"atlas-automatic.bgra");check(grid>1000,"automatic icons visible");
    icon.SetPos(32,32);icon.SetSize(64,64);icon.SetIconType455(5);icon.SetItemID(3);icon.SetSpriteID(1);icon.SetSprite();check(icon.GetSpriteInfo()->pSprite==unit&&(icon.GetSpriteInfo()->wActionNo>>8)==3,"unitparts route");const unsigned unitPixels=capture([&](){check(icon.Draw()!=0,"unit draw");},"atlas-unitparts.bgra");check(unitPixels>10,"unitparts pixels");
    icon.SetIconType455(0);icon.SetItemID(0xff00);icon.SetSpriteID(1);icon.SetSprite();check(icon.GetSpriteInfo()->pSprite==item&&icon.GetSpriteInfo()->wActionNo==0&&icon.GetSpriteInfo()->wFrameNo==0,"failedclassification keeps actual default cell");check(capture([&](){check(icon.Draw()!=0,"fallback draw");},"atlas-fallback.bgra")>10,"real fallback cell visible");
    icon.SetItemID(0xffffffff);icon.SetSprite();check(!icon.GetSpriteInfo()->pSprite&&icon.GetSizeX()==64,"emptyID early return");check(capture([&](){check(icon.Draw()!=0,"empty draw");},"atlas-empty.bgra")==0,"emptyID noimage");
    icon.RemoveSpriteInfo();gSpriteMgr.UnloadTargetSprites455();check(GetDmallocSize()==before,"all three atlas owners freed");item=gSpriteMgr.GetTargetSprite455(8);check(item&&item->GetPageNum()==40,"atlas reload");gSpriteMgr.UnloadTargetSprites455();check(GetDmallocSize()==before,"reload memory balance");R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");std::fprintf(out,"{\"status\":\"PASS\",\"atlas_cases\":%u,\"callback_failures\":%u,\"unsigned_WORD_row_wrap_cases\":%u,\"actual_manager_callback_fallback\":true,\"actual_GUIItem_SetSprite\":true,\"automatic_sample_icons\":16,\"GPU_frames\":4,\"grid_pixels\":%u,\"unitparts_pixels\":%u,\"sprite_allocator_balanced\":true,\"payload_metadata_binding\":false,\"full_GUIItem_children\":false,\"full_client\":false}\n",count,failures,wrapped,grid,unitPixels);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"Item atlas:%s\n",e.what());return 1;}}
