#define main RF455_UnusedIconMain165
#include "client455_item_icon_probe.cpp"
#undef main
#include "userinterface/gamewindow/guiinventorywindow.h"
#include "userinterface/uiglobal.h"
extern CSpriteMgr* g_pUiSpriteMgr;
template<class Tag,typename Tag::Type Member>struct InventoryMember165{friend typename Tag::Type inventoryAccess165(Tag){return Member;}};
struct QueueCreate165{using Type=void(*)(WORD);friend Type inventoryAccess165(QueueCreate165);};
struct QueueProcess165{using Type=void(*)();friend Type inventoryAccess165(QueueProcess165);};
struct SendMouse165{using Type=void(CGUIObject::*)(WORD);friend Type inventoryAccess165(SendMouse165);};
template struct InventoryMember165<QueueCreate165,&CGUIObject::CreateEventQueue>;
template struct InventoryMember165<QueueProcess165,&CGUIObject::EventProcess>;
template struct InventoryMember165<SendMouse165,&CGUIObject::SendMouseEvent>;
struct EquipMarks165{using Type=CGUIObject(CGUIEquipWindow::*)[TOTAL_EQUIP_ITEM];friend Type inventoryAccess165(EquipMarks165);};
template struct InventoryMember165<EquipMarks165,&CGUIEquipWindow::m_uiEmptyEquipMark>;
struct EquipItems165{using Type=CGUIItem(CGUIEquipWindow::*)[TOTAL_EQUIP_ITEM];friend Type inventoryAccess165(EquipItems165);};
template struct InventoryMember165<EquipItems165,&CGUIEquipWindow::m_uiEquipItem>;
struct EquipTrade165{using Type=CGUIObject(CGUIEquipWindow::*)[TOTAL_EQUIP_ITEM];friend Type inventoryAccess165(EquipTrade165);};
template struct InventoryMember165<EquipTrade165,&CGUIEquipWindow::m_uiTradeItemMark>;
struct PackTrade165{using Type=CGUIObject(CGUIInventoryBoard::*)[TOTAL_INVENTORY];friend Type inventoryAccess165(PackTrade165);};
template struct InventoryMember165<PackTrade165,&CGUIInventoryBoard::m_uiTradeItemMark>;
struct PackUseless165{using Type=CGUIObject(CGUIInventoryBoard::*)[TOTAL_INVENTORY];friend Type inventoryAccess165(PackUseless165);};
template struct InventoryMember165<PackUseless165,&CGUIInventoryBoard::m_uiUselessSocketMark>;
struct InventoryView165:CGUIInventoryWindow {
    auto& Header(){return m_uiAniTitleBar;}auto& Title(){return m_uiTitle;}auto& Help(){return m_uiHelpButton;}
    auto& Option(){return m_uiPackOpenOption;}auto& PackButton(unsigned i){return m_uiPackButton[i];}
    auto& DalantLabel(){return m_uiDalantTitle;}auto& GoldLabel(){return m_uiGoldTitle;}auto& Dalant(){return m_uiDalant;}
};
static void frame165(const char* name,InventoryView165& inventory){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(device->BeginScene()),"begin");check(inventory.Draw()!=0,"ordinary inventory draw");for(BYTE i=0;i<2;++i){auto* pack=inventory.GetPackWindow(i);const BOOL result=pack->Draw();if(!result)std::fprintf(stderr,"PackDraw:%u show=%d pos=%ld,%ld size=%ld,%ld\n",unsigned(i),pack->IsShow(),pack->GetPosX(),pack->GetPosY(),pack->GetSizeX(),pack->GetSizeY());check(result!=0,"ordinary visible pack draw");}check(SUCCEEDED(device->EndScene()),"end");
    IDirect3DSurface9 *target=nullptr,*copy=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);check(desc.Width==800&&desc.Height==600,"canvas");check(SUCCEEDED(device->CreateOffscreenPlainSurface(800,600,desc.Format,D3DPOOL_SYSTEMMEM,&copy,nullptr))&&SUCCEEDED(device->GetRenderTargetData(target,copy)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(copy->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");FILE* out=std::fopen(name,"wb");check(out!=nullptr,"frame");for(unsigned y=0;y<600;++y)check(std::fwrite(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch,4,800,out)==800,"pixels");std::fclose(out);copy->UnlockRect();copy->Release();target->Release();
}
static int inventory165(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=800;GetR3State()->mScreenYsize=600;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    auto* device=GetD3dDevice();IDirect3DSurface9 *oldTarget=nullptr,*oldDepth=nullptr,*canvas=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&oldTarget)),"old target");device->GetDepthStencilSurface(&oldDepth);D3DSURFACE_DESC desc={};oldTarget->GetDesc(&desc);check(SUCCEEDED(device->CreateRenderTarget(800,600,desc.Format,D3DMULTISAMPLE_NONE,0,FALSE,&canvas,nullptr))&&SUCCEEDED(device->SetDepthStencilSurface(nullptr))&&SUCCEEDED(device->SetRenderTarget(0,canvas)),"owned canvas");D3DVIEWPORT9 viewport={0,0,800,600,0,1};device->SetViewport(&viewport);
    inventoryAccess165(QueueCreate165{})(256);const auto baseline=GetDmallocSize();auto* oldSprites=g_pUiSpriteMgr;g_pUiSpriteMgr=&gSpriteMgr;gSpriteMgr.LoadSprite(SP_ID_COMMON);
    auto* screen=CGUIScreen::GetSingletonPtr();const HWND oldWindow=screen->GetHWND();HWND window=CreateWindowExA(0,"STATIC","OwnInventory165",0,0,0,0,0,HWND_MESSAGE,nullptr,GetModuleHandleA(nullptr),nullptr);check(window!=nullptr,"message window");screen->SetHWND(window);const BYTE oldRace=_GetAvatarRace();
    unsigned routes=0;
    for(BYTE race=0;race<3;++race){
        _SetUIAvatarRace(2*race);InventoryView165 inventory;inventory.SetID(83);inventory.SetPos(15,20);inventory.Init();inventory.Show(FALSE);
        check(inventory.GetSizeX()==228&&inventory.GetSizeY()==395&&inventory.GetAddedObjectNum()==14,"actual inventory root/14children");check(inventory.GetARGB()==0xd8ffffff,"inventory alpha");check(inventory.Header().GetPosY()==26&&inventory.Header().GetSpriteInfo()->wActionNo==4&&inventory.Header().GetSpriteInfo()->wFrameNo==0,"actual common header");check(inventory.Help().GetPosX()==inventory.Header().GetPosX()+4,"help on left");check(!std::strcmp(inventory.DalantLabel().GetString(),RF455_GetNormalLanguagePack()->get(10+race)),"actual localized race currency");check(inventory.DalantLabel().GetPosX()+inventory.DalantLabel().GetSizeX()==15+228-16,"natural right-aligned currency");
        CGUIEquipWindow equipment;equipment.Init();check(equipment.GetAddedObjectNum()==67,"actual16equipment slots and67children");inventory.SetEquipWindow(&equipment);check(inventory.GetAddedObjectNum()==15&&equipment.GetPosY()==inventory.Header().GetPosY()+inventory.Header().GetSizeY(),"borrowed equipment owner placement");
        auto& marks=equipment.*inventoryAccess165(EquipMarks165{});auto& eqTrade=equipment.*inventoryAccess165(EquipTrade165{});auto& icons=equipment.*inventoryAccess165(EquipItems165{});
        for(BYTE i=0;i<16;++i){auto* item=&icons[i];check(item->IsEmpty()&&!equipment.GetItem(0,i),"sixteen empty owners;public target getter returns null for empty");check(item->GetSizeX()==marks[i].GetSizeX()&&marks[i].GetARGB()==0x70ffffff,"natural empty equip geometry/alpha");check(eqTrade[i].GetSizeX()==item->GetSizeX()+2&&!eqTrade[i].GetSpriteInfo()->pSprite,"trade state preserves overlay geometry");}
        check(!equipment.GetItem(0,16)&&!equipment.GetItem(0,255),"equipment slot bounds");check(inventory.AddPack(0)&&inventory.AddPack(1)&&!inventory.AddPack(0)&&!inventory.AddPack(255),"actual pack owner creation/duplicate/bounds");
        auto* firstPack=inventory.GetPackWindow(0);auto* secondPack=inventory.GetPackWindow(1);check(firstPack->GetAddedObjectNum()==83&&secondPack->GetAddedObjectNum()==83,"twenty item slots/83children each");firstPack->SetPos(260,20);secondPack->SetPos(260,220);firstPack->SetDockingBorder(CGUIWindow::NONE_BORDER);secondPack->SetDockingBorder(CGUIWindow::NONE_BORDER);
        inventory.SetOwnDalant(8589934599LL);inventory.SetOwnGold(-12345678901LL);check(!std::strcmp(inventory.GetDalantStr(),"8,589,934,599")&&!std::strcmp(inventory.GetGoldStr(),"-12,345,678,901"),"signed64bit money widgets");const LONG edge=inventory.DalantLabel().GetSizeX()>inventory.GoldLabel().GetSizeX()?inventory.DalantLabel().GetPosX():inventory.GoldLabel().GetPosX();check(inventory.Dalant().GetPosX()+inventory.Dalant().GetSizeX()==edge-10,"money relative to wider title");
        inventory.SetOpenOnlyOnePack(FALSE);inventory.Show(TRUE);equipment.Show(TRUE);firstPack->Open();secondPack->Open();check(firstPack->IsShow()&&secondPack->IsShow()&&inventory.PackButton(0).GetSpriteInfo()->wActionNo==2&&inventory.PackButton(0).GetSpriteInfo()->wFrameNo==2*race+2,"race pack states and multiple windows");
        auto& trade=*(&(firstPack->*inventoryAccess165(PackTrade165{}))[0]);auto& unusable=*(&(firstPack->*inventoryAccess165(PackUseless165{}))[0]);firstPack->SetTradeItem(0,TRUE);firstPack->SetUselessSocket(0,TRUE);check(trade.GetSizeX()==34&&unusable.GetSizeX()==34&&unusable.GetARGB()==0x90ffffff,"actual 34pixel overlays retain dimensions");equipment.SetTradeItem(0,15,TRUE);equipment.SetUselessSocket(0,15,TRUE);
        const char* frames[]={"inventory-bellato.bgra","inventory-cora.bgra","inventory-accretia.bgra"};frame165(frames[race],inventory);
        (inventory.Option().*inventoryAccess165(SendMouse165{}))(1);inventoryAccess165(QueueProcess165{})();check(inventory.IsOpenOnlyOnePack()&&!firstPack->IsShow()&&secondPack->IsShow(),"actual GUI observer toggles single-pack mode and keeps last");++routes;
        firstPack->Open();check(firstPack->IsShow()&&!secondPack->IsShow(),"opening another pack enforces single mode");inventory.Close();check(!firstPack->IsShow()&&!equipment.IsShow(),"inventory closes equipment and free pack in single mode");inventory.Open();check(firstPack->IsShow()&&equipment.IsShow(),"open restores remembered pack andequipment");
        (inventory.Help().*inventoryAccess165(SendMouse165{}))(4);inventoryAccess165(QueueProcess165{})();MSG message={};check(PeekMessageA(&message,window,0x1204,0x1204,PM_REMOVE)&&message.wParam==83&&message.lParam==0,"actual help HWND message");++routes;
        if(race==2){inventory.SetSprite();equipment.SetSprite();firstPack->SetSprite();secondPack->SetSprite();frame165("inventory-reload.bgra",inventory);}
        screen->Remove(firstPack);screen->Remove(secondPack);firstPack->RemoveAll();secondPack->RemoveAll();inventory.RemoveAll();equipment.RemoveAll();
    }
    _SetUIAvatarRace(oldRace);screen->SetHWND(oldWindow);DestroyWindow(window);device->SetTexture(0,nullptr);gSpriteMgr.UnloadSpriteAll();g_pUiSpriteMgr=oldSprites;check(GetDmallocSize()==baseline,"sprite allocator balance");device->SetRenderTarget(0,oldTarget);device->SetDepthStencilSurface(oldDepth);canvas->Release();oldTarget->Release();if(oldDepth)oldDepth->Release();R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"report");std::fprintf(out,"{\"status\":\"PASS\",\"GPU_frames\":4,\"frame_width\":800,\"frame_height\":600,\"races\":3,\"inventory_children\":14,\"equipment_slots\":16,\"equipment_children\":67,\"pack_slots\":20,\"pack_children\":83,\"actual_observer_and_message_routes\":%u,\"signed64_money\":true,\"real_stock_skins\":true,\"actual_item_payload_gameplay\":false,\"full_input_hittest\":false,\"full_settings_and_lifecycle\":false,\"full_client\":false}\n",routes);std::fclose(out);return 0;
}
int main(){try{return inventory165();}catch(const std::exception& e){std::fprintf(stderr,"Inventory165:%s\n",e.what());return 1;}}
