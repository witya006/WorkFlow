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
#include "client455_board_hover.h"
#include "client455_player_status.h"
#include "client455_nuclear_aiming.h"
#include "client455_message_dispatch.h"
#include <memory>
#include <stdexcept>
#include <typeinfo>

struct RF455BoardHoverState {
    bool typed=false;
    std::unique_ptr<CBoardObject> previous{new CBoardObject};
    std::unique_ptr<CBoardObject> operation{new CBoardObject};
    ~RF455BoardHoverState(){previous.reset();operation.reset();}
};
BOOL RF455_IsOwnBoardObject455(CBoardObject* object){return object&&typeid(*object)==typeid(CBoardObject);}
bool RF455_AvatarRequiresHoverCancel(){
    auto* avatar=_GetAvatar();
    return avatar&&RF455_RequiresHoverCancelStatus(avatar->GetStatusCode455());
}
void RF455_RequireHoverCancellation(){
    // Target cancels effect/sound/position, then emits localized C1A through
    // actual center/chat/login providers, all before the item mutation.
    // Both target reads are pure. An inactive aiming owner cannot cancel:
    // avoid demanding an as-yet unwritten player status during Create_UI.
    // Pending aiming still requires the real status and message providers.
    if(_GetAvatar()&&RF455_NuclearAiming().pending&&RF455_AvatarRequiresHoverCancel())
        RF455_CancelNuclearForHover();
}
void CBoardManager::InitHover455(){m_hoverState455=new RF455BoardHoverState;}
void CBoardManager::DestroyHover455(){delete m_hoverState455;m_hoverState455=nullptr;}
BOOL CBoardManager::UsesTypedHover455()const{return m_hoverState455&&m_hoverState455->typed;}
CBoardObject* CBoardManager::PreviousHover455(){return m_hoverState455->previous.get();}
CBoardObject* CBoardManager::OperationObject455(){
    auto* object=m_hoverState455->operation.get();return object->IsEmpty()?nullptr:object;
}
void CBoardManager::SetOperationObject455(CBoardObject* source){
    if(source&&!RF455_IsOwnBoardObject455(source))throw std::logic_error("455 operation backup requires a migrated wrapper");
    m_hoverState455->typed=true;
    if(source)m_hoverState455->operation->Copy455(source);else m_hoverState455->operation->Clear();
}
void CBoardManager::ClearHoverBackups455(){m_hoverState455->previous->Clear();m_hoverState455->operation->Clear();}
CBoardObject* CBoardManager::HoverObject455(){
    if(m_pHoverObject)return m_pHoverObject;
    return UsesTypedHover455()?OperationObject455():nullptr;
}
CBoardItem* CBoardManager::LegacyHoverItem455(){
    if(RF455_IsOwnBoardObject455(m_pHoverObject))throw std::logic_error("455 shared hover cannot be cast to legacy CBoardItem");
    return static_cast<CBoardItem*>(m_pHoverObject);
}
CBoardItem* CBoardManager::LegacyDeletedHover455(){
    if(UsesTypedHover455())throw std::logic_error("455 dual hover backups require migrated payload consumers");
    return m_pDeletedHoverItem->IsEmpty()?nullptr:m_pDeletedHoverItem;
}
CBoardObject* CBoardManager::SetTypedHover455(CBoardObject* source){
    if(source&&(!RF455_IsOwnBoardObject455(source)||source==m_pHoverObject))
        throw std::logic_error("455 typed hover requires a distinct migrated wrapper");
    if(source&&(!source->GetIcon()||!source->GetIcon()->UsesTypedIcon455()))
        throw std::logic_error("455 hover requires the actual typed source icon");
    if(m_pHoverObject&&!RF455_IsOwnBoardObject455(m_pHoverObject))
        throw std::logic_error("455 mixed legacy hover replacement requires migration");
    RF455_RequireHoverCancellation();m_hoverState455->typed=true;
    if(source){
        if(m_pHoverObject){delete m_pHoverObject;m_pHoverObject=nullptr;gScreen.RemoveTypedHoverIcon455();}
        m_pHoverObject=source->Clone();
        if(!m_pHoverObject)throw std::bad_alloc();
        gScreen.AddTypedHoverIcon455(m_pHoverObject->GetIcon());
        m_pHoverObject->SetIcon(gScreen.GetObject());
        auto* item=source->GetItem455();const LONG size=item&&(item->isKind(0)||item->isKind(3)||item->isKind(4))?64:40;
        m_pHoverObject->GetIcon()->SetSize(size,size);
        if(item&&m_pHoverObject->GetIcon())m_pHoverObject->GetIcon()->SetLock455(item->header().flag21);
    }else{
        if(m_pHoverObject)m_hoverState455->previous->Copy455(m_pHoverObject);
        SetOperationObject455(nullptr);
        delete m_pHoverObject;m_pHoverObject=nullptr;
        gScreen.RemoveTypedHoverIcon455();
    }
    return m_pHoverObject;
}
BOOL CBoardManager::AddTypedBoardObject455(BYTE id,BYTE bank,BYTE slot,CBoardObject* source){
    if(!RF455_ForwardsBoardAdd455(id))return FALSE;
    auto* candidate=m_listBoard[id];if(!candidate)return FALSE;
    auto* linker=dynamic_cast<CLinkBoard*>(candidate);
    if(!linker)throw std::logic_error("455 typed board Add requires its full migrated source-board provider");
    if(!source||!source->GetItem455())return FALSE;
    linker->Add(bank,slot,source);
    //4FD660 returns0 evenafter a successful forwarded virtual Add.
    return FALSE;
}
void CGUIScreen::AddTypedHoverIcon455(CGUIItem* source){
    if(!source)return;
    if(!source->UsesTypedIcon455())throw std::logic_error("455 screen hover requires its migrated icon");
    m_cCatchedItem.SetData(source);m_cCatchedItem.DrawItemNum(TRUE);
    if(m_cCatchedItem.IsEmpty())m_cCatchedItem.SetItemID(0);
    m_cCatchedItem.Show(TRUE);
    m_cCatchedItem.SetPos(static_cast<LONG>(double(m_cMouse.GetPosX())-double(m_cCatchedItem.GetSizeX())/2.0),
                         static_cast<LONG>(double(m_cMouse.GetPosY())-double(m_cCatchedItem.GetSizeY())/2.0));
    m_cMouse.Show(FALSE);
    //The active source tooltip isreal andcleared here. Full455three-layer
    //tooltip state/producers remain separate mandatory GUI reconstruction.
    RemoveTooltip();
    for(auto* object:m_listObject){auto* window=dynamic_cast<CGUIWindow*>(object);
        if(!window)throw std::logic_error("455 screen picking list contains an unmigrated nonwindow owner");
        window->PickingObjectEvent(TRUE);}
}
void CGUIScreen::RemoveTypedHoverIcon455(){
    m_cCatchedItem.SetEmpty();m_cCatchedItem.Show(FALSE);m_cMouse.Show(TRUE);
    for(auto* object:m_listObject){auto* window=dynamic_cast<CGUIWindow*>(object);
        if(!window)throw std::logic_error("455 screen picking list contains an unmigrated nonwindow owner");
        window->PickingObjectEvent(FALSE);}
}
