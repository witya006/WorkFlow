#include "client455_gui_tab_board.h"
#include "userinterface/spritemgr.h"
#include <algorithm>
#include <stdexcept>
#undef min
#undef max

CGUITabBoard455::~CGUITabBoard455(){Clear455();RemoveAll();}
void CGUITabBoard455::Clear455(){
    //The target deletes the group array but leaves borrowed list entries.
    //Own references must be detached before their C++ owners are released.
    //Unsafe target use-after-clear/reinitialization is not an equivalence claim.
    body.RemoveAll();groups.clear();
}
void CGUITabBoard455::Init455(BYTE count,LONG contentWidth,LONG headerHeight,LONG width,LONG height){
    Clear455();if(!count)return;
    SetSize(width,height);body.SetSize(contentWidth,height);body.SetPos(m_ptPos);
    scroll.SetPos(m_ptPos.x+m_ptSize.x-scroll.m_ptSize.x,m_ptPos.y);
    Add(&body);scroll.AddScrollHandler(this);Add(&scroll);
    for(unsigned i=0;i<count;++i){
        auto group=std::unique_ptr<Group>(new Group);auto& g=*group;
        g.root.SetSize(contentWidth,headerHeight);g.header.SetSize(contentWidth,headerHeight);g.content.SetSize(contentWidth,0);
        g.root.SetPos(body.m_ptPos.x,body.m_ptPos.y+LONG(i)*headerHeight);
        g.header.SetPos(g.root.m_ptPos);g.label.SetPos(g.root.m_ptPos);g.label.SetSize(contentWidth,headerHeight);
        g.header.AddMouseEventHandler(this);g.label.SetMouseInput455(FALSE);
        g.root.Add(&g.header);g.root.Add(&g.label);body.Add(&g.root);groups.push_back(std::move(group));
    }
}
void CGUITabBoard455::SetSize(LONG width,LONG height){
    CGUIObject::SetSize(width,height);
    RECT bounds={m_ptPos.x+width-scroll.GetSizeX(),m_ptPos.y,m_ptPos.x+width,m_ptPos.y+height};
    scroll.SetBound(bounds);RepositionScroll455();
}
void CGUITabBoard455::SetBound(RECT& bounds){SetPos(bounds.left,bounds.top);SetSize(bounds.right-bounds.left,bounds.bottom-bounds.top);}
void CGUITabBoard455::BindHeader455(CGUIObject& header,const RF455TabSprite& image){
    auto* sprite=gSpriteMgr.GetTargetSprite455(image.id);
    if(!sprite||image.action>=sprite->GetMaxActions()||image.frame>=sprite->GetMaxFrames(image.action))throw std::runtime_error("455 tab header skin missing");
    SPRITE_INFO info={sprite,image.action,image.frame};header.SetSpriteInfo(&info);
    header.SetSize(sprite->GetSpriteOrgXL(image.action,image.frame),sprite->GetSpriteOrgYL(image.action,image.frame));
}
void CGUITabBoard455::SetHeaderSprites455(const RF455TabSprite& collapsed,const RF455TabSprite& expanded){
    skin[0]=collapsed;skin[1]=expanded;for(auto& group:groups)BindHeader455(group->header,skin[0]);
}
void CGUITabBoard455::SetTitle455(BYTE index,const char* text,DWORD color){
    if(index>=groups.size())return;auto& group=*groups[index];group.label.SetString(const_cast<char*>(text));group.label.GetFont()->dwColor=color;
    group.label.SetPos(group.header.GetPosX()+(group.header.GetSizeX()-group.label.GetSizeX())/2,group.header.GetPosY()+(group.header.GetSizeY()-group.label.GetSizeY())/2);
}
BOOL CGUITabBoard455::IsOpened455(BYTE index)const{return index<groups.size()&&groups[index]->root.IsAddedObject(&groups[index]->content);}
void CGUITabBoard455::SetOpened455(BYTE index,BOOL opened){
    if(index>=groups.size()||bool(opened)==bool(IsOpened455(index)))return;auto& g=*groups[index];
    if(opened){g.content.SetPos(g.header.GetPosX(),g.header.GetPosY()+g.header.GetSizeY());g.root.Add(&g.content);BindHeader455(g.header,skin[1]);}
    else{g.root.Remove(&g.content);BindHeader455(g.header,skin[0]);}
    Reflow455();
}
void CGUITabBoard455::Reflow455(){
    if(groups.empty())throw std::domain_error("455 empty group reflow outside admitted target domain");
    for(unsigned i=0;i<groups.size();++i){
        auto& g=*groups[i];g.root.SetSize(g.header.GetSizeX(),g.header.GetSizeY()+(IsOpened455(BYTE(i))?g.content.GetSizeY():0));
        if(i){auto& p=groups[i-1]->root;g.root.SetPos(p.GetPosX(),p.GetPosY()+p.GetSizeY());}
    }
    auto& first=groups.front()->root;auto& last=groups.back()->root;
    body.SetSize(body.GetSizeX(),last.GetPosY()+last.GetSizeY()-first.GetPosY());RepositionScroll455();
}
void CGUITabBoard455::RepositionScroll455(){
    const LONG total=body.GetSizeY()-GetSizeY();scroll.SetAmount(total,std::min(total,scroll.GetCurrentAmount()));
    body.SetPos(body.GetPosX(),GetPosY()-scroll.GetCurrentAmount());
}
CGUIContainer* CGUITabBoard455::Content455(BYTE i){return i<groups.size()?&groups[i]->content:nullptr;}
CGUIContainer* CGUITabBoard455::Group455(BYTE i){return i<groups.size()?&groups[i]->root:nullptr;}
CGUIObject* CGUITabBoard455::Header455(BYTE i){return i<groups.size()?&groups[i]->header:nullptr;}
CGUIText* CGUITabBoard455::Label455(BYTE i){return i<groups.size()?&groups[i]->label:nullptr;}
void CGUITabBoard455::ScrollEvent(_scroll_event&){body.SetPos(body.GetPosX(),GetPosY()-scroll.GetCurrentAmount());}
void CGUITabBoard455::MouseEvent(_mouse_event& event){
    if(event.id!=MOUSE_STROKED)return;for(unsigned i=0;i<groups.size();++i)if(event.source==&groups[i]->header){SetOpened455(BYTE(i),!IsOpened455(BYTE(i)));return;}
}
