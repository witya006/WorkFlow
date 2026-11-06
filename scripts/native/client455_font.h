#pragma once
#include <d3d9.h>
#include <cstdint>
#include <memory>
#include <string>
#include "client455_font_settings.h"

struct RF455FontVertex {float x,y,z,rhw;DWORD color;float u,v;};
static_assert(sizeof(RF455FontVertex)==28,"455 font vertex stride");
struct RF455FontSnapshot {
    unsigned cellWidth,cellHeight,columns,rows,cacheHits,uploads;
    HFONT font;IDirect3DTexture9* texture;
};
// Source-owned GDI/Unicode route,not an overlay of the original2040byte object.
// The separate FreeType/ANSI branches remain explicit unfinished contracts.
class RF455GdiFont {
public:
    RF455GdiFont();~RF455GdiFont();
    RF455GdiFont(const RF455GdiFont&)=delete;
    RF455GdiFont&operator=(const RF455GdiFont&)=delete;
    HRESULT initialize(IDirect3DDevice9*,const char*name,unsigned charset,unsigned width,unsigned height,unsigned points);
    HRESULT draw(float position[4],const wchar_t*,DWORD color,DWORD flags,float scale=1,const float*clip=nullptr);
    SIZE measure(const wchar_t*)const;
    RF455FontSnapshot snapshot()const;
    void release();
    DWORD outline=0;
private:
    struct State;std::unique_ptr<State> state;
};
HRESULT RF455_LoadTextResources(IDirect3DDevice9*,unsigned availableMemory);
void RF455_ReleaseTextResources();
HRESULT RF455_DrawText(float position[4],const wchar_t*,DWORD,DWORD,float scale=1,const float*clip=nullptr);
HRESULT RF455_DrawLegacyText(float position[4],const char*,DWORD,DWORD,const float*clip=nullptr);
DWORD RF455_GetTextOutline();void RF455_SetTextOutline(DWORD);
