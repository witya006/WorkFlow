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
#include "client455_icon_links.h"
#include <algorithm>
#include <stdexcept>
extern CMainApp g_MainApp;

std::uint64_t RF455_IconLinkKey(CGUIItem& icon){
    return (std::uint64_t(icon.GetItemID()&0x0fffffff)<<28)|
        (icon.GetObjectIndex455()&0x0fffffff)|(std::uint64_t(icon.GetIconType())<<60);
}
RF455IconLinks& RF455_GameIconLinks(){return g_MainApp.IconLinks455();}
void RF455IconLinks::registerIcon(CGUIItem& icon){
    //7AE520 appends even if this pointer is already registered.
    buckets[RF455_IconLinkKey(icon)].push_back(&icon);
}
bool RF455IconLinks::unregisterIcon(CGUIItem& icon){
    auto group=buckets.find(RF455_IconLinkKey(icon));if(group==buckets.end())return false;
    auto& members=group->second;auto found=std::find(members.begin(),members.end(),&icon);
    //Target erases end() here for a wrong-member/empty-bucket request. Refuse
    //that undefined domain explicitly;normal owners remove registered members.
    if(found==members.end())throw std::logic_error("455 icon unregister member is absent from an existing bucket");
    members.erase(found);return true; //Empty map buckets are deliberately retained.
}
const std::vector<CGUIItem*>* RF455IconLinks::find(CGUIItem& icon)const{
    auto found=buckets.find(RF455_IconLinkKey(icon));return found==buckets.end()?nullptr:&found->second;
}
std::size_t RF455IconLinks::linkCount()const{
    std::size_t total=0;for(const auto& group:buckets)total+=group.second.size();return total;
}
void CGUIItem::SetNum455(WORD value){
    m_wNum=value;const auto* group=RF455_GameIconLinks().find(*this);if(!group)return;
    for(auto* member:*group)if(member)member->m_wNum=value;
}
void CGUIItem::SetUsable455(BYTE value){
    m_byUsable=value;const auto* group=RF455_GameIconLinks().find(*this);if(!group)return;
    for(auto* member:*group)member->m_byUsable=value;
}
