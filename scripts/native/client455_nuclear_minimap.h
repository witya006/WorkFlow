#pragma once
#ifndef RF455_NUCLEAR_MINIMAP_H
#define RF455_NUCLEAR_MINIMAP_H
#include "userinterface/guicontroller/guicontainer.h"
#include "client455_image_text.h"

// Source-owned CGUINuclearBomb, not an overlay of its private540-byte ABI.
// The registry/race lookup belongs to the caller. These methods implement the
// confirmed UI operations after that lookup, including missing-record retention.
class CGUINuclearBomb455:public CGUIContainer {
    RECT worldBounds={};
    POINT dimensions={},offset={};
    float scale[2]={},relative[2]={};
    CGUIImageText455 label;
    CGUIObject background,icon;
    void Recalculate455();
public:
    ~CGUINuclearBomb455(){RemoveAll();}
    void SetMapBound455(const RECT&);
    void SetMapGeometry455(LONG width,LONG height,LONG x,LONG y);
    void SetTargetPosition455(const float*);
    void Display455();
    void Hide455();
    void SetMouseInput455(BOOL enabled);
    using CGUIContainer::Draw;
    BOOL Draw()override;
    CGUIImageText455& Label455(){return label;}
    CGUIObject& Background455(){return background;}
    CGUIObject& Icon455(){return icon;}
    const float* Scale455()const{return scale;}
    const float* RelativePosition455()const{return relative;}
};
#endif
