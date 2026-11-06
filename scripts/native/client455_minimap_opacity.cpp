#include "client455_minimap_opacity.h"
#include "userinterface/guicontroller/guiscrollbar.h"
#include <cstdint>
namespace {
LONG add(LONG a,LONG b){return static_cast<LONG>(static_cast<DWORD>(a)+static_cast<DWORD>(b));}
LONG sub(LONG a,LONG b){return static_cast<LONG>(static_cast<DWORD>(a)-static_cast<DWORD>(b));}
LONG aligned(LONG position,LONG extent,LONG size,int requested){
    switch(requested){case -3:return sub(add(position,extent),size);case -2:return position;case -1:return add(position,sub(extent,size)/2);default:return requested;}
}
void resizeImage(CGUIObject& object){
    auto& image=*object.GetSpriteInfo();auto* sprite=image.pSprite;
    if(sprite&&image.wActionNo<sprite->GetMaxActions()&&image.wFrameNo<sprite->GetMaxFrames(image.wActionNo)){
        const LONG width=sprite->GetSpriteOrgXL(image.wActionNo,image.wFrameNo);
        if(width)object.SetSize(width,sprite->GetSpriteOrgYL(image.wActionNo,image.wFrameNo));
    }
}
void plainImage(CGUIObject& object,CSprite* sprite,WORD frame){SPRITE_INFO image={sprite,8,frame};object.SetSpriteInfo(&image);resizeImage(object);}
void buttonImage(CGUIButton& button,CSprite* sprite,WORD normal,WORD pressed){
    SPRITE_INFO image={sprite,8,normal};button.SetSpriteInfoEx(&image);resizeImage(button);image.wFrameNo=pressed;button.SetSpriteInfoEx(PRESSED,&image);resizeImage(button);
}
}
void RF455_AlignGuiObject(CGUIObject& object,const POINT& origin,const POINT& extent,int x,int y){
    POINT position={aligned(origin.x,extent.x,object.GetSizeX(),x),aligned(origin.y,extent.y,object.GetSizeY(),y)};object.SetPos(position);
}
void RF455_ConfigureOpacityScrollbar(CGUIScrollbarEX* scrollbar,CSprite* common,BYTE style){
    if(!scrollbar)return;
    if(style==0){
        plainImage(*scrollbar,common,12);buttonImage(scrollbar->GetButton455(),common,13,14);
        buttonImage(scrollbar->GetBottomArrow455(),common,15,16);buttonImage(scrollbar->GetTopArrow455(),common,17,18);
    }else if(style==1){
        plainImage(*scrollbar,common,6);plainImage(scrollbar->GetButton455(),common,7);
        buttonImage(scrollbar->GetTopArrow455(),common,8,9);buttonImage(scrollbar->GetBottomArrow455(),common,10,11);
    }
    scrollbar->SetSize(add(add(scrollbar->GetSizeX(),scrollbar->GetTopArrow455().GetSizeX()),scrollbar->GetBottomArrow455().GetSizeX()),scrollbar->GetSizeY());
    scrollbar->SetAutoThumb455(FALSE);scrollbar->SetStyle(CGUIScrollbar::Horizontal);
}
BYTE RF455_MinimapAlphaForAmount(LONG current){
    const LONG product=static_cast<LONG>(static_cast<DWORD>(add(current,20))*255u);return static_cast<BYTE>(product/100);
}
BYTE RF455_MinimapBackgroundAlpha(BYTE alpha){return static_cast<BYTE>(static_cast<int>(static_cast<double>(alpha)*(alpha==100?0.8:0.6)));}
