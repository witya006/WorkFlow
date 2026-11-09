#pragma once
#ifndef RF455_IMAGE_TEXT_H
#define RF455_IMAGE_TEXT_H
#include "userinterface/guicontroller/guiobject.h"
#include <vector>

class CGUIImageText455:public CGUIObjectEx {
    std::vector<BYTE> glyphs;
    LONG cellWidth=0,cellHeight=0;
    float stepU=0,stepV=0;
public:
    static BYTE glyph(BYTE character,LONG cellWidth,LONG imageWidth);
    void Configure455(BYTE sprite,WORD action,WORD frame,LONG width,LONG height);
    void SetString455(const char*);
    LONG CellWidth455()const{return cellWidth;}
    LONG CellHeight455()const{return cellHeight;}
    BOOL Draw()override;
    BOOL Draw(RECT&)override;
};
#endif
