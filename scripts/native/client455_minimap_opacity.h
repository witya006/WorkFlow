#pragma once
#include <windows.h>
class CGUIObject;
class CGUIScrollbarEX;
class CSprite;
void RF455_AlignGuiObject(CGUIObject& object,const POINT& origin,const POINT& extent,int x,int y);
void RF455_ConfigureOpacityScrollbar(CGUIScrollbarEX* scrollbar,CSprite* common,BYTE style=0);
BYTE RF455_MinimapAlphaForAmount(LONG current);
BYTE RF455_MinimapBackgroundAlpha(BYTE alpha);
