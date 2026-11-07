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
#include "client455_item_object.h"
#include <cstdio>
#include <cstring>
#include <new>
#include <stdexcept>
#include <typeinfo>

extern CMainApp g_MainApp;
RF455ClientItems& RF455_GameItems(){return g_MainApp.Items455();}
namespace {
bool read(const char* name,std::vector<unsigned char>& out){FILE* f=std::fopen(name,"rb");if(!f)return false;
    if(std::fseek(f,0,SEEK_END)){std::fclose(f);return false;}const auto n=std::ftell(f);if(n<0){std::fclose(f);return false;}
    std::rewind(f);out.resize(static_cast<std::size_t>(n));const bool okay=std::fread(out.data(),1,out.size(),f)==out.size();std::fclose(f);return okay;}
}
bool RF455ClientItems::loadFiles(const char* item,const char* names,const char* quest,const char* character,const char* sf,const char* sfNames){
    std::vector<unsigned char> raw;
    if(!read(item,raw)||!data.loadItemEdf(raw.data(),raw.size(),true))return false;
    if(!read(names,raw)||!data.localizeItemEdf(raw.data(),raw.size()))return false;
    if(!read(quest,raw)||!data.loadQuestEdf(raw.data(),raw.size()))return false;
    if(!read(character,raw)||!data.loadCharacterEdf(raw.data(),raw.size()))return false;
    return skillForce.loadFiles(sf,sfNames);
}
CItemObject::CItemObject():m_pSharedItem455(nullptr),m_dwItemField588455(0){}
CItemObject::CItemObject(const CItemObject& source):CResObject(source),m_pSharedItem455(source.m_pSharedItem455),m_dwItemField588455(source.m_dwItemField588455){}
CItemObject::~CItemObject(){CItemObject::Clear();}
void CItemObject::Clear(){
    CObject::Clear();if(!m_pSharedItem455)return;
    auto& manager=RF455_GameItems().manager;
    // Test the primary cache before dereferencing a potentially retired payload.
    if(manager.primaryCacheEmpty())return;
    RF455BoardItemRecord release={};release.item=&m_pSharedItem455->header();
    if(RF455_ReleaseBoardItemReference(release,manager))m_pSharedItem455=nullptr;
}
void CItemObject::SetItem455(RF455ManagedItem* item){
    Clear();m_pSharedItem455=item;
    if(item){RF455_RetainItem(item->header());SetName(const_cast<char*>(item->name()));}
}
void CItemObject::RetainSharedItem455(){if(m_pSharedItem455)RF455_RetainItem(m_pSharedItem455->header());}
const void* CItemObject::GetItemData455()const{return m_pSharedItem455?reinterpret_cast<const void*>(m_pSharedItem455->header().data16):nullptr;}
CBoardObject::CBoardObject():m_bIsUsing(0),m_uiIcon(nullptr){std::memset(m_boardFields600455,0,17);}
CBoardObject::CBoardObject(const CBoardObject& source):CItemObject(source),m_bIsUsing(source.m_bIsUsing),m_uiIcon(source.m_uiIcon){std::memcpy(m_boardFields600455,source.m_boardFields600455,17);}
CBoardObject::~CBoardObject(){}
void CBoardObject::Clear(){CItemObject::Clear();SetIcon(nullptr);}
void CBoardObject::SetItem455(RF455ManagedItem* item){
    if(typeid(*this)!=typeid(CBoardObject))throw std::logic_error("455 mixed derived payload consumers have not been migrated");
    CItemObject::SetItem455(item);
    if(item){SetIndex(item->header().serial);SetServerIndex(item->header().field8);RefreshIcon455();}
}
void CBoardObject::SetIndex(DWORD index){CObject::SetIndex(index);if(m_pSharedItem455)m_pSharedItem455->header().serial=index;
    if(m_uiIcon&&(m_pSharedItem455||typeid(*this)==typeid(CBoardObject)))throw std::logic_error("455 item icon index provider is not restored");}
void CBoardObject::SetIcon(CGUIItem* icon){m_uiIcon=icon;RefreshIcon455();}
void CBoardObject::RefreshIcon455(){
    // Legacy GUIItem has neither455 object-index nor inline caption provider.
    // Do not silently claim the real icon refresh when a typed item reaches it.
    if(m_uiIcon&&(m_pSharedItem455||typeid(*this)==typeid(CBoardObject)))throw std::logic_error("455 item icon/caption owner is not restored");
}
BOOL CBoardObject::IsEqual(DWORD index){return m_dwIndex==index;}
BOOL CBoardObject::IsEqual(CBoardObject* other){if(!other)return FALSE;
    if(m_pSharedItem455||other->m_pSharedItem455)return m_pSharedItem455&&m_pSharedItem455==other->m_pSharedItem455;
    if(typeid(*this)==typeid(CBoardObject)||typeid(*other)==typeid(CBoardObject))return FALSE;
    return GetItemType()==other->GetItemType()&&m_dwIndex==other->m_dwIndex;}
CBoardObject* CBoardObject::New(){return new(std::nothrow) CBoardObject;}
CBoardObject* CBoardObject::Clone(){auto* result=new(std::nothrow) CBoardObject(*this);if(result)result->RetainSharedItem455();return result;}
void CBoardObject::BeginDelayAnimation(DWORD time){if(m_uiIcon)m_uiIcon->BeginDelayAnimation(time);}
