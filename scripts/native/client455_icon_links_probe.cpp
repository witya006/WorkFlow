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
#include "client455_icon_links.h"
#include "client455_item_icon_metadata.h"
#include "client455_nation_paths.h"
#include "client455_language.h"
#include "jmalloc.h"
#include <cstdio>
#include <cstring>
#include <stdexcept>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
template<class Tag,typename Tag::Type Member>struct Access{friend typename Tag::Type access(Tag){return Member;}};
struct Quantity{using Type=WORD CGUIItem::*;friend Type access(Quantity);};template struct Access<Quantity,&CGUIItem::m_wNum>;
static WORD quantity(CGUIItem& icon){return icon.*access(Quantity{});}
static void identity(CGUIItem& icon,DWORD index,DWORD item,BYTE type,bool typed=true){icon.SetObjectIndex455(index,typed);if(typed)icon.SetIconType455(type);else icon.SetIconType(type);icon.SetItemID(item);}
static void cpu(){
    FILE* f=std::fopen("icon-key-cases.bin","rb");check(f!=nullptr,"key oracle");char magic[4];unsigned count=0;check(std::fread(magic,1,4,f)==4&&!std::memcmp(magic,"IK95",4)&&std::fread(&count,4,1,f)==1&&count==160,"key header");CGUIItem sample;
    for(unsigned i=0;i<count;++i){unsigned row[5];check(std::fread(row,4,5,f)==5,"key row");identity(sample,row[0],row[1],static_cast<BYTE>(row[2]));const auto key=RF455_IconLinkKey(sample);check(static_cast<unsigned>(key)==row[3]&&static_cast<unsigned>(key>>32)==row[4],"binary-decoded64bit key oracle");}check(std::fgetc(f)==EOF,"key extent");std::fclose(f);
    auto& links=RF455_GameIconLinks();check(&links==&g_MainApp.IconLinks455(),"actualMainApp owner");links.clear();CGUIItem root,first,second,alias,other,missing,legacy;
    for(auto* icon:{&root,&first,&second,&missing})identity(*icon,0xf0000015,0x01234567,2);
    identity(alias,0xa0000015,0xf1234567,0xf2);identity(other,0xf0000016,0x01234567,2);other.SetUsable(7);
    check(RF455_IconLinkKey(root)==RF455_IconLinkKey(alias)&&!links.find(root),"masked identity collision/missing bucket");
    links.registerIcon(first);links.registerIcon(second);links.registerIcon(first);links.registerIcon(alias);links.registerIcon(other);const auto* group=links.find(root);
    check(group&&group->size()==4&&(*group)[0]==&first&&(*group)[1]==&second&&(*group)[2]==&first&&(*group)[3]==&alias&&links.bucketCount()==2&&links.linkCount()==5,"append order and duplicate registration");
    root.SetNum(65535);root.SetUsable(128);check(quantity(root)==65535&&quantity(first)==65535&&quantity(second)==65535&&quantity(alias)==65535&&quantity(other)==1&&quantity(missing)==1&&first.IsUsable()==128&&second.IsUsable()==128&&alias.IsUsable()==128&&other.IsUsable()==7&&missing.IsUsable()==255,"self and registered members only");
    first.SetNum(256);check(quantity(first)==256&&quantity(second)==256&&quantity(alias)==256&&quantity(root)==65535,"registered initiator doesnot update unregistered root");
    for(unsigned value:{0u,1u,255u,256u,65535u,65536u}){root.SetNum(static_cast<WORD>(value));for(auto* icon:{&root,&first,&second,&alias})check(quantity(*icon)==static_cast<WORD>(value),"WORD quantity fanout");}
    for(int value:{0,1,2,127,128,255,256,-1}){root.SetUsable(value);for(auto* icon:{&root,&first,&second,&alias})check(icon->IsUsable()==static_cast<BYTE>(value),"rawBYTE usable fanout");}
    check(links.unregisterIcon(first)&&links.find(root)->size()==3,"erase first duplicate");root.SetNum(257);check(quantity(first)==257,"remaining duplicate still receives updates");check(links.unregisterIcon(first),"erase second duplicate");root.SetNum(258);check(quantity(first)==257&&quantity(second)==258,"fully detached member stops updating");
    bool refused=false;try{links.unregisterIcon(root);}catch(const std::logic_error&){refused=true;}check(refused&&links.find(root)->size()==2,"unsafe absent-member removal explicit");
    check(links.unregisterIcon(other)&&links.find(other)&&links.find(other)->empty()&&links.bucketCount()==2,"empty bucket retained");
    alias.SetObjectIndex455(99);check(!links.unregisterIcon(alias)&&links.find(root)->size()==2,"changed identity is not automatically reindexed");root.SetNum(259);check(quantity(alias)==259,"oldbucket still owns registered pointer");alias.SetNum(260);check(quantity(second)==259,"lookup uses current identity");alias.SetObjectIndex455(0xa0000015);check(links.unregisterIcon(alias),"owner restores identity before unregister");root.SetNum(261);check(quantity(second)==261&&quantity(alias)==260,"removed alias no longer updated");check(links.unregisterIcon(second)&&links.linkCount()==0&&links.find(root)&&links.find(root)->empty(),"all links removed but bucket retained");
    refused=false;try{links.unregisterIcon(second);}catch(const std::logic_error&){refused=true;}check(refused,"unsafe emptybucket removal explicit");links.clear();check(!links.unregisterIcon(root)&&!links.bucketCount(),"missingkey removal and registry clear");
    identity(root,5,6,2);identity(first,5,6,2);identity(legacy,5,6,2,false);first.SetNum(17);first.SetUsable(9);links.registerIcon(first);legacy.SetNum(99);legacy.SetUsable(3);check(quantity(first)==17&&first.IsUsable()==9,"untypedlegacy setters retain local behavior");links.registerIcon(legacy);root.SetNum(19);check(quantity(first)==19&&quantity(legacy)==19,"registered targets receive directstores regardless legacyflag");check(links.unregisterIcon(first)&&links.unregisterIcon(legacy),"caller unregisters while members alive");links.clear();
}
template<class Draw>static unsigned capture(Draw draw,const char* name){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");draw();check(SUCCEEDED(device->EndScene()),"end");IDirect3DSurface9 *target=nullptr,*memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");FILE* f=std::fopen(name,"wb");check(f!=nullptr,"frame");unsigned pixels=0;
    for(unsigned y=view.Y;y<view.Y+480;++y){const auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;check(std::fwrite(row,4,640,f)==640,"write");for(unsigned x=0;x<640;++x)pixels+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(f);memory->UnlockRect();memory->Release();target->Release();return pixels;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);cpu();auto& runtime=RF455_GameItems();check(runtime.loadFiles("item.edf","nd-zh-tw.edf","quest.edf","character.edf","base.edf","zh-tw.edf"),"actual data owner");check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");const auto before=GetDmallocSize();unsigned beforePixels=0,afterPixels=0,detachedPixels=0;
    {
        FILE* f=std::fopen("metadata-samples.bin","rb");check(f!=nullptr,"real sample");char magic[4];unsigned n=0,row[3];check(std::fread(magic,1,4,f)==4&&!std::memcmp(magic,"MS94",4)&&std::fread(&n,4,1,f)==1&&n==16&&std::fread(row,4,3,f)==3,"sample header");std::fclose(f);
        CGUIInventoryBoard window;CBoardObject object;object.SetItem455(runtime.create(static_cast<BYTE>(row[0]),static_cast<BYTE>(row[1]),row[2]));check(window.TakeInItem455(0,&object,0),"actual inventory original");auto* root=window.GetItem(0);check(root!=nullptr,"root icon");CGUIItem first,second;first.SetData(root);second.SetData(root);CGUIItem* icons[]={root,&first,&second};
        for(unsigned i=0;i<3;++i){icons[i]->SetPos(32+130*i,40);icons[i]->SetSize(64,64);icons[i]->Show(TRUE);}auto& links=RF455_GameIconLinks();links.registerIcon(first);links.registerIcon(second);root->SetNum(1);root->SetUsable(TRUE);auto draw=[&](){for(auto* icon:icons)check(icon->Draw()!=0,"actual original/copy draw");};beforePixels=capture(draw,"links-before.bgra");check(beforePixels>100,"real image pixels");
        root->SetNum(255);root->SetUsable(FALSE);check(quantity(first)==255&&quantity(second)==255&&!first.IsUsable()&&!second.IsUsable(),"registered real copies changed");afterPixels=capture(draw,"links-propagated.bgra");check(links.unregisterIcon(first),"unregister first realcopy");root->SetNum(2);root->SetUsable(TRUE);check(quantity(first)==255&&!first.IsUsable()&&quantity(second)==2&&second.IsUsable(),"removed realcopy remains unchanged");detachedPixels=capture(draw,"links-detached.bgra");check(links.unregisterIcon(second)&&!links.linkCount(),"unregister realcopy before destruction");links.clear();check(window.TakeOutItem(0,0),"clear originalwindow");
    }
    check(runtime.manager.size()==0&&!RF455_GameIconLinks().bucketCount(),"all actual payload and graph owners cleared");gSpriteMgr.UnloadTargetSprites455();check(GetDmallocSize()==before,"spriteallocator balance");R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"output");std::fprintf(out,"{\"status\":\"PASS\",\"key_oracles\":160,\"actual_MainApp_registry\":true,\"duplicate_append_first_remove\":true,\"empty_buckets_retained\":true,\"current_identity_lookup\":true,\"WORD_quantity_rawBYTE_usable\":true,\"unregistered_original_not_a_member\":true,\"unsafe_removal_refusals\":2,\"untyped_legacy_local\":true,\"real_inventory_original\":true,\"registered_real_copies\":2,\"GPU_frames\":3,\"before_pixels\":%u,\"after_pixels\":%u,\"detached_pixels\":%u,\"all_owners_cleared\":true,\"sprite_allocator_balanced\":true,\"ordinary_Linker_Macro_registration\":false,\"full_client\":false}\n",beforePixels,afterPixels,detachedPixels);std::fclose(out);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& e){std::fprintf(stderr,"Icon links:%s\n",e.what());return 1;}}
