#include "client455_nuclear_minimap.h"
#include "userinterface/spritemgr.h"
#include "userinterface/gamewindow/etcwin/guiminimapwindow.h"
#include <cstdio>
#include <stdexcept>

namespace {
LONG add32(LONG a,LONG b){return static_cast<LONG>(static_cast<DWORD>(a)+static_cast<DWORD>(b));}
LONG subtract32(LONG a,LONG b){return static_cast<LONG>(static_cast<DWORD>(a)-static_cast<DWORD>(b));}
}
void CGUINuclearBomb455::Recalculate455(){
    const LONG width=subtract32(worldBounds.right,worldBounds.left),height=subtract32(worldBounds.bottom,worldBounds.top);
    if(width>0&&height>0){scale[0]=static_cast<float>(double(dimensions.x)/width);scale[1]=static_cast<float>(double(dimensions.y)/height);}
}
void CGUINuclearBomb455::SetMapBound455(const RECT& value){worldBounds=value;Recalculate455();}
void CGUINuclearBomb455::SetMapGeometry455(LONG width,LONG height,LONG x,LONG y){dimensions={width,height};offset={x,y};Recalculate455();}
void CGUINuclearBomb455::SetTargetPosition455(const float* point){
    if(!point)return;
    relative[0]=static_cast<float>(double(add32(offset.x,GetPosX()))+(double(point[0])-worldBounds.left)*scale[0]-double(static_cast<DWORD>(icon.GetSizeX())/2u)-GetPosX());
    relative[1]=static_cast<float>(double(add32(offset.y,GetPosY()))+(double(worldBounds.bottom)-point[2])*scale[1]-double(static_cast<DWORD>(icon.GetSizeY())/2u)-GetPosY());
    char coordinates[16]={};std::sprintf(coordinates,"%2d %2d",static_cast<int>(relative[0]/4.0)+3,static_cast<int>(relative[1]/4.0)+3);label.SetString455(coordinates);
    label.SetPos(static_cast<LONG>(double(icon.GetSizeX())+double(GetPosX())+relative[0]+14.0),static_cast<LONG>(double(GetPosY())+relative[1]-double(icon.GetSizeY())+10.0));
    background.SetPos(static_cast<LONG>(double(icon.GetSizeX())+double(GetPosX())+relative[0]),static_cast<LONG>(double(GetPosY())+relative[1]-double(icon.GetSizeY())));
    background.SetSize(static_cast<LONG>(static_cast<DWORD>(label.CellWidth455())*9u),30);
    icon.SetPos(static_cast<LONG>(double(GetPosX())+relative[0]),static_cast<LONG>(double(GetPosY())+relative[1]));
}
void CGUINuclearBomb455::Display455(){
    auto* sprite=gSpriteMgr.GetTargetSprite455(4);
    if(!sprite||sprite->GetMaxActions()<=5||sprite->GetMaxFrames(5)<=43)throw std::runtime_error("455 nuclear marker main5/43 sprite missing");
    SPRITE_INFO image={sprite,5,43};icon.SetSpriteInfo(&image);icon.SetSize(sprite->GetSpriteOrgXL(5,43),sprite->GetSpriteOrgYL(5,43));icon.Show(TRUE);Add(&icon);
    background.SetARGB(0x96000000);background.Show(TRUE);Add(&background);
    label.Configure455(1,7,3,7,9);label.Show(TRUE);Add(&label);
}
void CGUINuclearBomb455::Hide455(){Remove(&label);Remove(&background);Remove(&icon);}
void CGUINuclearBomb455::SetMouseInput455(BOOL value){
    CGUIObject::SetMouseInput455(value);
    for(int i=0;i<GetAddedObjectNum();++i)GetAddedObject(static_cast<WORD>(i))->SetMouseInput455(value);
}
BOOL CGUINuclearBomb455::Draw(){
    if(!CGUIContainer::Draw())return FALSE;
    //70BEC0: after the ordinary Draw, add5 through a BYTE. Even255 wraps to4;
    //the signed >255 branch is unreachable after the observed zero extension.
    const BYTE alpha=static_cast<BYTE>((icon.GetARGB()>>24)+5u);icon.SetARGB((icon.GetARGB()&0xffffff)|(static_cast<DWORD>(alpha)<<24));return TRUE;
}
void CGUIMiniMapWindow::InitNuclearMarkers455(){
    for(auto& marker:m_nuclearMarkers455){marker.SetPos(m_uiMiniMap.GetPosX(),m_uiMiniMap.GetPosY());marker.SetSize(m_uiMiniMap.GetSizeX(),m_uiMiniMap.GetSizeY());marker.SetMouseInput455(FALSE);marker.Show(TRUE);m_uiMiniMap.Add(&marker);}
}
void CGUIMiniMapWindow::ReleaseNuclearMarkers455(){for(auto& marker:m_nuclearMarkers455){marker.Hide455();m_uiMiniMap.Remove(&marker);}}
CGUINuclearBomb455& CGUIMiniMapWindow::NuclearMarker455(BYTE index){
    if(index>=3)throw std::out_of_range("455 nuclear marker index outside three-element owner");return m_nuclearMarkers455[index];
}
void CGUIMiniMapWindow::SetNuclearMarker455(BYTE index,BOOL show,const float* foundPosition){
    auto& marker=NuclearMarker455(index);
    if(show){if(foundPosition){marker.SetTargetPosition455(foundPosition);marker.Display455();}}
    else marker.Hide455();
}
void CGUIMiniMapWindow::SetNuclearMapGeometry455(LONG width,LONG height,LONG x,LONG y){
    m_ptRealMinimapSize={width,height};m_nuclearMapOffset455={x,y};SetPixelPerMeter();
    for(auto& marker:m_nuclearMarkers455)marker.SetMapGeometry455(width,height,x,y);
}
