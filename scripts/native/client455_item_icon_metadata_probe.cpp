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
#include "client455_item_icon_metadata.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <vector>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
template<class Tag,typename Tag::Type Member>struct Access{friend typename Tag::Type access(Tag){return Member;}};
struct Packs{using Type=CObjectPack* CObjectBoard::*;friend Type access(Packs);};template struct Access<Packs,&CObjectBoard::m_listItemPack>;
static FILE* oracle(const char* name,const char* magic,unsigned& count){FILE* f=std::fopen(name,"rb");check(f!=nullptr,"oracle open");char header[4];check(std::fread(header,1,4,f)==4&&!std::memcmp(header,magic,4)&&std::fread(&count,4,1,f)==1,"oracle header");return f;}
template<class Draw>static unsigned capture(Draw draw,const char* name){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");draw();check(SUCCEEDED(device->EndScene()),"end");IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");FILE* f=std::fopen(name,"wb");check(f!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+480;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;check(std::fwrite(row,4,640,f)==640,"write");for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(f);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);auto& runtime=RF455_GameItems();check(runtime.loadFiles("item.edf","nd-zh-tw.edf","quest.edf","character.edf","base.edf","zh-tw.edf"),"actual CMainApp item data owner");
    unsigned count=0,successful=0,quest=0,bounded=0;FILE* f=oracle("metadata-cases.bin","MD94",count);
    for(unsigned i=0;i<count;++i){unsigned row[9];check(std::fread(row,4,9,f)==9,"metadata row");auto* item=runtime.create(static_cast<BYTE>(row[0]),static_cast<BYTE>(row[1]),row[2]);check(item&&runtime.manager.size()==1,"real factory");bool rejected=false;
        try{const auto m=RF455_ReadBasicIconMetadata(*item);check(row[8]==0&&m.itemID==row[3]&&m.spriteID==row[4]&&m.quantity==row[5]&&m.usableLevel==row[6]&&m.grade==row[7],"real metadata vs independent EDF/instruction oracle");++successful;}
        catch(const std::out_of_range&){check(row[8]==1,"unexpected metadata extent");rejected=true;++bounded;}
        catch(const std::logic_error&){check(row[8]==2,"unexpected metadata provider refusal");rejected=true;++quest;}
        check(rejected==(row[8]!=0),"metadata refusal domain");runtime.manager.erasePrimary(&item->header());check(!runtime.manager.size(),"fresh payload release");
    }
    check(std::fgetc(f)==EOF&&count==575&&successful==566&&quest==9&&bounded==0,"metadata coverage");std::fclose(f);
    unsigned usableCount=0;f=oracle("usable-cases.bin","US94",usableCount);for(unsigned i=0;i<usableCount;++i){unsigned row[5];check(std::fread(row,4,5,f)==5,"usable row");check(RF455_IconUsable455(row[0],static_cast<BYTE>(row[1]),static_cast<BYTE>(row[2]),static_cast<BYTE>(row[3]))==(row[4]!=0),"race-user BYTE/level oracle");}check(std::fgetc(f)==EOF&&usableCount==520,"usable coverage");std::fclose(f);
    auto* sf=runtime.create(1,1,0);bool refused=false;try{RF455_ReadBasicIconMetadata(*sf);}catch(const std::logic_error&){refused=true;}check(refused,"SF dedicated metadata provider explicit");runtime.manager.erasePrimary(&sf->header());
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");const auto before=GetDmallocSize();unsigned realPixels=0,updatedPixels=0;
    {
        CGUIInventoryBoard window;CLinkBoard container;container.Create(6,1,20);check(container.AddPack(0),"actual owner pack");auto& pack=(container.*access(Packs{}))[0];std::vector<std::unique_ptr<CBoardObject>> originals;
        unsigned samples=0;f=oracle("metadata-samples.bin","MS94",samples);check(samples==16,"sample count");
        for(unsigned i=0;i<samples;++i){unsigned row[3];check(std::fread(row,4,3,f)==3,"sample row");auto* payload=runtime.create(static_cast<BYTE>(row[0]),static_cast<BYTE>(row[1]),row[2]);std::unique_ptr<CBoardObject> original(new CBoardObject);original->SetItem455(payload);auto* clone=original->Clone();check(clone&&pack.Add(static_cast<BYTE>(i),clone)&&payload->header().references==2,"actual source clone/pack ownership");const auto m=RF455_ReadBasicIconMetadata(*payload);
            check(window.TakeInItem455(static_cast<BYTE>(i),clone,0),"actual inventory owner handoff");auto* icon=window.GetItem(static_cast<WORD>(i));check(icon&&clone->GetIcon()==icon&&icon->GetObjectIndex455()==clone->GetIndex()&&icon->GetItemID()==m.itemID&&icon->GetSpriteID()==m.spriteID&&icon->GetNum()==m.quantity&&icon->GetGrade455()==m.grade&&icon->IsUsable()==RF455_IconUsable455(m.itemID,0,255,icon->GetUsableLevel()),"actual linked icon metadata");icon->SetPos(24+64*(i%8),24+64*(i/8));icon->Show(TRUE);originals.push_back(std::move(original));
        }
        check(std::fgetc(f)==EOF,"sample extent");std::fclose(f);auto draw=[&](){for(unsigned i=0;i<16;++i)if(auto* icon=window.GetItem(static_cast<WORD>(i)))check(icon->Draw()!=0,"real inventory icon draw");};realPixels=capture(draw,"metadata-real-items.bgra");check(realPixels>1000,"real inventory pixels");
        BYTE changedSlot=255;for(BYTE i=0;i<16;++i){auto* value=dynamic_cast<RF455BasicItem*>(pack.GetObject(i)->GetItem455());const auto kind=value->rawMetadata().data[88];if(kind>=1&&kind<=10){changedSlot=i;break;}}check(changedSlot!=255,"equipment sample for grade/level boundaries");
        auto* wrapper=pack.GetObject(changedSlot);auto* basic=dynamic_cast<RF455BasicItem*>(wrapper->GetItem455());auto* state=const_cast<unsigned char*>(basic->recordBytes().data);auto* data=const_cast<unsigned char*>(basic->rawMetadata().data);auto* icon=window.GetItem(changedSlot);const BYTE oldQuantity=state[92],oldGrade=data[152],oldLevel=data[172];DWORD oldID=0;std::memcpy(&oldID,data+72,4);
        state[92]=0;check(!window.TakeInItem455(changedSlot,wrapper,0)&&window.GetItem(changedSlot)==icon&&icon->GetNum()==oldQuantity,"quantity0 rejects without replacing icon");state[92]=255;data[152]=11;data[172]=255;icon->SetUsableLevel(12);check(window.TakeInItem455(changedSlot,wrapper,0)&&icon->GetNum()==255&&icon->GetGrade455()==11&&icon->GetUsableLevel()==12,"BYTEquantity/grade/sticky requiredFF");updatedPixels=capture(draw,"metadata-updated-item.bgra");check(updatedPixels>0,"changed metadata draw");
        const DWORD invalid=0xffffffff;std::memcpy(data+72,&invalid,4);check(window.TakeInItem455(changedSlot,wrapper,0)&&!window.GetItem(changedSlot)&&!wrapper->GetIcon(),"invalid itemID keeps window success but detaches icon");state[92]=oldQuantity;data[152]=oldGrade;data[172]=oldLevel;std::memcpy(data+72,&oldID,4);check(window.TakeInItem455(changedSlot,wrapper,0),"restore real metadata");
        check(!window.TakeInItem455(20,wrapper,0)&&!window.TakeInItem455(255,wrapper,0)&&!window.TakeInItem455(0,nullptr,0),"slot/null boundaries");
        {CBoardObject other;other.SetItem455(runtime.create(1,1,0));check(!window.TakeInItem455(0,&other,0),"inventory rejects SF payload kind");}
        check(window.TakeInItemFields455(19,oldID,RF455_ReadBasicIconMetadata(*wrapper->GetItem455()).spriteID,0,255,0)&&window.GetItem(19)&&window.GetItem(19)->GetNum()==0&&window.TakeOutItem(19,0),"raw inventory core allows quantity0;parent payload handoff rejects it");
        for(unsigned i=0;i<16;++i){check(window.TakeOutItem(static_cast<BYTE>(i),0)&&!window.GetItem(static_cast<WORD>(i)),"actual window takeout");check(pack.Remove(static_cast<BYTE>(i)),"actual owner clone removal");}originals.clear();check(!runtime.manager.size(),"all real payload owners freed");check(capture(draw,"metadata-empty.bgra")==0,"actual window cleared icons");
    }
    gSpriteMgr.UnloadTargetSprites455();check(GetDmallocSize()==before,"atlas allocator balance");R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");std::fprintf(out,"{\"status\":\"PASS\",\"real_metadata_cases\":566,\"Quest_refusals\":9,\"SF_refusal\":true,\"bounded_cases\":0,\"race_level_cases\":520,\"actual_inventory_icon_owners\":16,\"actual_game_data_manager\":true,\"actual_pack_clones\":true,\"BYTE_quantity_and_sticky_FF\":true,\"invalid_ID_detaches\":true,\"GPU_frames\":3,\"real_pixels\":%u,\"updated_pixels\":%u,\"all_payload_owners_released\":true,\"sprite_allocator_balanced\":true,\"ordinary_CItemBoard_Add\":false,\"full_inventory\":false,\"full_client\":false}\n",realPixels,updatedPixels);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"Item metadata:%s\n",e.what());return 1;}}
