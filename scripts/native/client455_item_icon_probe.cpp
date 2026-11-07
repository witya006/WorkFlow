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
#include "client455_item_icon.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
template<class Draw> static unsigned capture(Draw draw,const char* name){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");draw();check(SUCCEEDED(device->EndScene()),"end");
    IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");
    FILE* f=std::fopen(name,"wb");check(f!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+view.Height;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;check(std::fwrite(row,4,640,f)==640,"write");for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(f);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static void core(){
    FILE* file=std::fopen("grade-colors.bin","rb");check(file!=nullptr,"binary-decoded oracle");DWORD expected[256];check(std::fread(expected,4,256,file)==256&&std::fgetc(file)==EOF,"all grade oracle bytes");std::fclose(file);
    CGUIItem icon;
    for(unsigned i=0;i<256;++i){icon.SetGrade455(static_cast<BYTE>(i));check(RF455_ItemGradeColor(static_cast<BYTE>(i))==expected[i]&&icon.GetGrade455()==i&&icon.GetGradeFrameColor455()==expected[i],"all BYTE grades vsbinary immediate oracle");}
    unsigned quantityCases=0;for(unsigned type:{0u,2u,7u,5u,255u})for(unsigned quantity:{0u,1u,2u,255u,256u,65535u})for(unsigned enabled:{0u,1u})for(unsigned clipped:{0u,1u}){
        const bool above=quantity>1&&((clipped?0x81u:0x85u)&(type<8?1u<<type:0));
        const bool zero=!quantity&&!type;check(RF455_ItemQuantityVisible(static_cast<BYTE>(type),static_cast<WORD>(quantity),enabled!=0,clipped!=0)==(enabled&&(above||zero)),"quantity truth table/WORD limits");++quantityCases;
    }
    check(quantityCases==120,"quantity coverage");
    for(LONG width:{-1L,0L,1L,32L,63L,64L,65L,0x7fffffffL}){icon.SetSize(width,37);check(icon.GetSizeX()==width&&icon.m_gradeFrame455.GetSizeX()==width&&icon.m_gradeFrame455.GetSizeY()==37&&icon.m_gradeFrame455.GetSpriteInfo()->wActionNo==3&&icon.m_gradeFrame455.GetSpriteInfo()->wFrameNo==(width>=64?3:2),"signed width border frame");}
    POINT pos={-11,42},size={64,48};icon.SetPos(pos);icon.SetSize(size);check(icon.m_gradeFrame455.GetPosX()==-11&&icon.m_gradeFrame455.GetPosY()==42&&icon.m_gradeFrame455.GetSizeX()==64,"POINT geometry");
    CGUIItem other;CBoardObject owner;owner.SetIndex(17);icon.SetGrade455(4);owner.SetIcon(&icon);check(icon.GetObjectIndex455()==17&&icon.UsesTypedIcon455(),"actual board binding");
    icon.SetGradeFrameColor455(0x12345678);owner.SetIndex(19);check(icon.GetObjectIndex455()==19&&icon.GetGradeFrameColor455()==0x12345678,"SetIndex updatesindexwithout recoloring");owner.RefreshIcon455();check(icon.GetGradeFrameColor455()==expected[4],"refresh independently restores bordercolor");
    std::unique_ptr<CBoardObject> clone(owner.Clone());check(clone->GetIcon()==&icon,"copy borrows same icon");clone->SetIcon(&other);clone->SetIndex(29);check(other.GetObjectIndex455()==29&&icon.GetObjectIndex455()==19,"clone rebinds independently");clone->Clear();owner.Clear();check(!clone->GetIcon()&&!owner.GetIcon(),"clear detaches icons");
    CGUIItem copied;copied.SetData(&icon);check(copied.UsesTypedIcon455()&&copied.GetObjectIndex455()==19&&copied.GetGrade455()==4&&copied.GetGradeFrameColor455()==expected[4],"source SetData copiesselectedtypedmetadata");
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);core();
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    const auto before=GetDmallocSize();auto* atlas=gSpriteMgr.GetTargetSprite455(8);auto* frame=gSpriteMgr.GetTargetSprite455(6);check(atlas&&frame&&atlas->GetMaxActions()==1&&atlas->GetMaxFrames(0)==40&&frame->GetMaxFrames(3)==4,"actual455sprites");check(gSpriteMgr.GetTargetSprite455(8)==atlas&&gSpriteMgr.GetTargetSprite455(6)==frame&&!gSpriteMgr.GetTargetSprite455(55)&&!gSpriteMgr.GetTargetSprite455(7),"cacheidentity/missingimage");
    CGUIItem icon;icon.SetIconType455(0);icon.SetGrade455(3);icon.SetPos(32,32);icon.SetSize(64,64);icon.Show(TRUE);icon.SetNum(1);SPRITE_INFO reference={atlas,1,0};icon.SetSpriteInfo(&reference);icon.SetSize(64,64);
    const unsigned grid=capture([&](){for(unsigned i=0;i<12;++i){icon.SetPos(24+80*(i%6),24+80*(i/6));icon.SetGrade455(static_cast<BYTE>(i));SPRITE_INFO cell={atlas,static_cast<WORD>(i),0};icon.SetSpriteInfo(&cell);const LONG side=i<6?32:64;icon.SetSize(side,side);check(icon.Draw()!=0,"grade grid");}},"icons-grades.bgra");check(grid>1000,"visible gradegrid");
    icon.SetPos(32,32);icon.SetSpriteInfo(&reference);icon.SetSize(64,64);icon.SetGrade455(3);icon.SetNum(1);
    const unsigned full=capture([&](){check(icon.Draw()!=0,"full");},"icons-full.bgra");
    icon.ShowGradeFrame455(FALSE);const unsigned noBorder=capture([&](){check(icon.Draw()!=0,"no border");},"icons-no-border.bgra");check(full>0&&noBorder>0,"actual icon pixels");icon.ShowGradeFrame455(TRUE);
    icon.SetARGB(0x80443322);icon.SetUsable(FALSE);capture([&](){check(icon.Draw()!=0,"unusable");},"icons-unusable.bgra");check(icon.GetARGB()==0x80666666,"unusable tint preservesalpha");icon.SetUsable(TRUE);icon.SetARGB(0xffffffff);
    RECT clip={40,40,80,80};const unsigned cropped=capture([&](){check(icon.Draw(clip)!=0,"clip");},"icons-clipped.bgra");check(cropped>0&&cropped<full,"actual clipped pixels");
    icon.SetNum(65535);capture([&](){check(icon.Draw()!=0,"WORDquantity");},"icons-quantity.bgra");icon.DrawItemNum(FALSE);capture([&](){check(icon.Draw()!=0,"disabledquantity");},"icons-quantity-hidden.bgra");
    icon.Show(FALSE);check(capture([&](){check(icon.Draw()==0,"hidden return");},"icons-hidden.bgra")==0,"hiddenimage gate");icon.Show(TRUE);icon.RemoveSpriteInfo();check(capture([&](){check(icon.Draw()!=0,"noimage return");},"icons-no-image.bgra")==0,"noimage skipsgrade andquantity");
    gSpriteMgr.UnloadTargetSprites455();check(GetDmallocSize()==before,"spriteallocator returnsbaseline");atlas=gSpriteMgr.GetTargetSprite455(8);check(atlas&&atlas->GetMaxFrames(0)==40,"actualreload");gSpriteMgr.UnloadTargetSprites455();check(GetDmallocSize()==before,"reload allocatorbalance");
    R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");std::fprintf(out,"{\"status\":\"PASS\",\"grade_byte_values\":256,\"quantity_boundary_cases\":120,\"signed_width_cases\":8,\"actual_board_icon_index\":true,\"actual_sprite_ID6_ID8\":true,\"grade_border_not_caption\":true,\"actual_GPU_frames\":9,\"grid_pixels\":%u,\"full_pixels\":%u,\"no_border_pixels\":%u,\"clip_pixels\":%u,\"sprite_allocator_balanced\":true,\"automatic_item_atlas_factory\":false,\"full_GUIItem\":false,\"full_client\":false}\n",grid,full,noBorder,cropped);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Item icon:%s\n",error.what());return 1;}}
