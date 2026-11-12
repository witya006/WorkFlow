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
#include "client455_linker_window.h"
#include <cstdio>
#include <stdexcept>

namespace {
SPRITE_INFO reference(BYTE id,WORD action,WORD frame){auto* sprite=gSpriteMgr.GetTargetSprite455(id);
    if(!sprite||action>=sprite->GetMaxActions()||frame>=sprite->GetMaxFrames(action))throw std::runtime_error("455 Linker window sprite reference missing");return {sprite,action,frame};}
void image(CGUIObject& object,BYTE id,WORD action,WORD frame){auto ref=reference(id,action,frame);object.SetSpriteInfo(&ref);object.SetSize(ref.pSprite->GetSpriteOrgXL(action,frame),ref.pSprite->GetSpriteOrgYL(action,frame));}
void spriteSize(CGUIObject& object,float scale){auto* info=object.GetSpriteInfo();auto* sprite=info->pSprite;if(!sprite){object.SetSize(0,0);return;}object.SetSize(static_cast<LONG>(double(sprite->GetSpriteOrgXL(info->wActionNo,info->wFrameNo))*scale),static_cast<LONG>(double(sprite->GetSpriteOrgYL(info->wActionNo,info->wFrameNo))*scale));}
LONG metric(double value,float scale){return static_cast<LONG>(value*scale);}
LONG position(LONG origin,double offset,float scale){return static_cast<LONG>(double(origin)+offset*scale);}
void align(CGUIObject& object,CGUIObject& anchor,int vertical){const LONG x=anchor.GetPosX()+(anchor.GetSizeX()-object.GetSizeX())/2;
    const LONG y=vertical==-2?anchor.GetPosY():vertical==-3?anchor.GetPosY()+anchor.GetSizeY()-object.GetSizeY():anchor.GetPosY()+(anchor.GetSizeY()-object.GetSizeY())/2;object.SetPos(x,y);}
}
BOOL RF455_LinkerIconDelaying455(CGUIItem* icon){
    if(icon->UsesTypedIcon455())return icon->Timer455().IsStarted455();
    if(auto* legacy=dynamic_cast<CGUISFItem*>(icon))return legacy->IsDelayAnimation();
    throw std::logic_error("455 typed Linker timer and gameplay input provider is not restored");
}
CGUILinkWindow455::CGUILinkWindow455(){
    number.SetMouseInput455(FALSE);numberAnchor.SetMouseInput455(FALSE);
    for(auto& bank:banks){bank.decoration.SetMouseInput455(FALSE);bank.label.SetMouseInput455(FALSE);}
    SetName(const_cast<char*>("Linker"));
}
void CGUILinkWindow455::SetButton455(CGUIButton& button,BYTE id,WORD action,WORD normal,WORD pressed){
    auto ref=reference(id,action,normal);button.SetSpriteInfoEx(&ref);ref.wFrameNo=pressed;button.SetSpriteInfoEx(PRESSED,&ref);
}
void CGUILinkWindow455::ExpandVisual455(){SetButton455(expandButton,4,1,expanded?4:2,3);spriteSize(expandButton,scale);}
void CGUILinkWindow455::BankVisual455(BYTE index){
    auto& bank=banks[index];
    if(index==state.active){bank.row.SetSpriteInfo(nullptr);bank.row.SetARGB((bank.row.GetARGB()&0xffffff)|0xff000000);bank.label.SetSpriteInfo(nullptr);bank.pin.SetSpriteInfoEx(nullptr);}
    else {auto ref=reference(4,1,0);bank.row.SetSpriteInfo(&ref);bank.row.SetARGB((bank.row.GetARGB()&0xffffff)|0xda000000);
        bank.label.Configure455(1,7,3,7,9);SetButton455(bank.pin,4,1,5,6);spriteSize(bank.pin,scale);}
}
void CGUILinkWindow455::SetSprite(){
    for(BYTE i=0;i<5;++i){image(banks[i].row,4,1,0);image(banks[i].decoration,4,1,1);SetButton455(banks[i].pin,4,1,5,6);
        banks[i].label.Configure455(1,7,3,7,9);char text[2]={char('1'+i),0};banks[i].label.SetString455(text);banks[i].label.SetARGB(0xffcabaa6);}
    ExpandVisual455();SetButton455(allButton,4,1,7,8);SetButton455(nextButton,1,2,8,9);SetButton455(previousButton,1,2,10,11);
    number.Configure455(1,7,3,7,9);number.SetARGB(0xffcabaa6);
    if(state.active<5){char text[2]={char('1'+state.active),0};number.SetString455(text);for(BYTE i=0;i<5;++i)BankVisual455(i);}
}
void CGUILinkWindow455::Init(){
    SetSprite();
    if(!initialized){
        for(BYTE bank=0;bank<5;++bank){auto& row=banks[bank];row.pin.AddMouseEventHandler(this);row.selector.AddMouseEventHandler(this);
            row.row.Add(&row.pin);row.row.Add(&row.selector);row.row.Add(&row.label);
            for(BYTE slot=0;slot<10;++slot){auto* icon=icons.get(bank,slot);icon->AddMouseEventHandler(this);row.row.Add(icon);}
            row.row.Add(&row.decoration);row.row.SetARGB((row.row.GetARGB()&0xffffff)|0xda000000);}
        for(auto* button:{&expandButton,&allButton,&nextButton,&previousButton})button->AddMouseEventHandler(this);
        mainRow.Add(&expandButton);mainRow.Add(&allButton);mainRow.Add(&numberAnchor);mainRow.Add(&number);mainRow.Add(&nextButton);mainRow.Add(&previousButton);Add(&mainRow);initialized=TRUE;
    }
    Layout455(gScreen.GetSizeX());for(BYTE i=0;i<5;++i)SetBankFlag455(i,1);SetExpanded455(FALSE);SelectBank455(0);
}
void CGUILinkWindow455::Layout455(LONG width){
    scale=width>=1024?1.0f:static_cast<float>(double(width)/1024.0);icons.SetScale455(scale);
    mainRow.SetSize(metric(481,scale),metric(46,scale));CGUIWindow::SetSize(mainRow.GetSizeX(),GetSizeY());
    spriteSize(expandButton,scale);expandButton.SetPos(mainRow.m_ptPos);
    spriteSize(allButton,scale);allButton.SetPos(expandButton.GetPosX(),expandButton.GetPosY()+expandButton.GetSizeY());
    numberAnchor.SetSize(metric(19,scale),metric(43,scale));numberAnchor.SetPos(position(GetPosX(),22,scale),position(mainRow.GetPosY(),2,scale));
    spriteSize(nextButton,scale);spriteSize(previousButton,scale);align(number,numberAnchor,-1);align(nextButton,numberAnchor,-2);align(previousButton,numberAnchor,-3);
    for(BYTE i=0;i<5;++i){auto& bank=banks[i];bank.row.SetSize(metric(461,scale),metric(46,scale));bank.selector.SetSize(metric(20,scale),metric(22,scale));spriteSize(bank.pin,scale);spriteSize(bank.decoration,scale);
        bank.decoration.SetPos(position(bank.row.GetPosX(),40,scale),position(bank.row.GetPosY(),5,scale));bank.pin.SetPos(position(bank.row.GetPosX(),3,scale),position(bank.row.GetPosY(),2,scale));bank.selector.SetPos(position(bank.row.GetPosX(),1,scale),position(bank.row.GetPosY(),24,scale));align(bank.label,bank.selector,-1);
        for(BYTE j=0;j<10;++j){auto* icon=icons.get(i,j);icon->SetSize(metric(38,scale),metric(38,scale));icon->SetPos(position(bank.row.GetPosX(),44*j+24,scale),position(bank.row.GetPosY(),4,scale));}}
    Reflow455();
}
void CGUILinkWindow455::Reflow455(){
    int extra=0;if(expanded)for(BYTE i=0;i<5;++i)if(i!=state.active&&state.bankFlags[i])++extra;
    const POINT base=mainRow.m_ptPos;CGUIWindow::SetSize(GetSizeX(),mainRow.GetSizeY()*(extra+1));CGUIWindow::SetPos(GetPosX(),base.y-mainRow.GetSizeY()*extra);mainRow.SetPos(base.x,base.y);
    const LONG x=mainRow.GetPosX()+expandButton.GetSizeX();if(state.active<5)banks[state.active].row.SetPos(x,base.y);
    LONG y=base.y;
    for(BYTE i=0;i<5;++i){if(expanded&&state.bankFlags[i]&&i!=state.active){y-=banks[0].row.GetSizeY();banks[i].row.SetPos(x,y);Add(&banks[i].row);}else Remove(&banks[i].row);}
}
void CGUILinkWindow455::SetExpanded455(BOOL value){expanded=value!=FALSE;ExpandVisual455();Reflow455();if(value)PostUIMessage(0x50d,LPARAM(0));}
void CGUILinkWindow455::SelectBank455(BYTE value){
    if(value>=5||value==state.active)return;const BYTE previous=state.active;state.active=value;
    if(previous<5){mainRow.Remove(&banks[previous].row);BankVisual455(previous);}
    char text[2]={char('1'+value),0};number.SetString455(text);mainRow.Add(&banks[value].row,0);BankVisual455(value);Reflow455();PostUIMessage(0x50c,LPARAM(value));
}
void CGUILinkWindow455::CycleBank455(BOOL next){int candidate=int(state.active)+(next?1:4);for(int i=0;i<4&&!state.bankFlags[candidate%5];++i)candidate+=next?1:-1;
    if(candidate%5!=state.active)SelectBank455(static_cast<BYTE>(candidate%5));}
void CGUILinkWindow455::SetBankFlag455(BYTE bank,int value){if(bank>=5)return;state.bankFlags[bank]=value;BankVisual455(bank);Reflow455();}
void CGUILinkWindow455::ResetBankFlags455(){state.bankFlags.fill(1);Reflow455();}
BOOL CGUILinkWindow455::FindIcon455(CGUIObject* object,BYTE& bank,BYTE& slot){for(BYTE i=0;i<5;++i)for(BYTE j=0;j<10;++j)if(object==icons.get(i,j)){bank=i;slot=j;return TRUE;}return FALSE;}
BOOL CGUILinkWindow455::UseItem455(BYTE bank,BYTE slot){
    if(postUseRequest){UI_MOUSE_MSG data(bank,slot,0,0);return PostUIMessage(WM_BOARD_USE_OBJECT,data);}
    if(!owner)throw std::logic_error("455 Linker input requires its real board owner");
    return owner->UseShortcut455(bank,slot);
}
void CGUILinkWindow455::MouseEvent(_mouse_event& event){CGUIWindow::MouseEvent(event);DispatchMouse455(event,gScreen.ExistObject(),(GetKeyState(VK_CONTROL)&0xf000)!=0,(GetKeyState(VK_SHIFT)&0xf000)!=0,(GetKeyState(VK_MENU)&0xf000)!=0);}
void CGUILinkWindow455::DispatchMouse455(_mouse_event& event,BOOL drag,BOOL control,BOOL shift,BOOL alt){
    BYTE bank=0,slot=0;const bool found=FindIcon455(event.source,bank,slot)!=FALSE;
    if(event.id==MOUSE_STROKED){if(found){const UINT code=drag?0x502:alt?0x512:control?0x510:0x504;UI_MOUSE_MSG data(bank,slot,drag?0:1,0);PostUIMessage(code,data);}
        else for(BYTE i=0;i<5;++i)if(event.source==&banks[i].selector){if(i!=state.active)SelectBank455(i);break;}}
    else if(event.id==LMOUSE_STROKED){if(shift){if(found){UI_MOUSE_MSG data(bank,slot,0,0);PostUIMessage(0x3327,data);}}else if(!drag&&found)UseItem455(bank,slot);}
    else if(event.id==MOUSE_HOVERED){if(!drag&&found){UI_MOUSE_MSG data(bank,slot,0,0);PostUIMessage(0x501,data);}}
    else if(event.id==MOUSE_CLICKED){if(event.source==&expandButton)SetExpanded455(!expanded);else if(event.source==&nextButton)CycleBank455(TRUE);else if(event.source==&previousButton)CycleBank455(FALSE);else if(event.source==&allButton)ResetBankFlags455();
        else for(BYTE i=0;i<5;++i)if(event.source==&banks[i].pin){SetBankFlag455(i,state.bankFlags[i]==0);break;}}
}
CGUIObject* CGUILinkWindow455::Control455(unsigned kind,BYTE bank){switch(kind){case 0:return &expandButton;case 1:return &allButton;case 2:return &nextButton;case 3:return &previousButton;
    case 4:return bank<5?&banks[bank].pin:nullptr;case 5:return bank<5?&banks[bank].selector:nullptr;case 6:return bank<5?&banks[bank].row:nullptr;default:return nullptr;}}
