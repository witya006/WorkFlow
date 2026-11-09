#include "client455_font.h"
#include <d3dx9.h>
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <cwchar>
#include <vector>

namespace {
template<class T>void releaseCom(T*&p){if(p){p->Release();p=nullptr;}}
struct Entry {std::wstring text;unsigned left,right;};
struct Row {std::vector<Entry> entries;unsigned characters=0;};
void prepare(IDirect3DDevice9*d,IDirect3DTexture9*t){
    d->SetTexture(0,t);
    d->SetRenderState(D3DRS_ALPHABLENDENABLE,TRUE);
    d->SetRenderState(D3DRS_SRCBLEND,D3DBLEND_SRCALPHA);
    d->SetRenderState(D3DRS_DESTBLEND,D3DBLEND_INVSRCALPHA);
    d->SetRenderState(D3DRS_CULLMODE,D3DCULL_CCW);
    d->SetRenderState(D3DRS_FOGENABLE,FALSE);
    d->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
    d->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE);
    d->SetTextureStageState(0,D3DTSS_COLORARG2,0);
    d->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_MODULATE);
    d->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);
    d->SetTextureStageState(0,D3DTSS_ALPHAARG2,0);
    d->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE);
    d->SetTextureStageState(1,D3DTSS_ALPHAOP,D3DTOP_DISABLE);
}
RF455GdiFont fonts[3];bool loaded=false,registered=false;
void(*textReadyCallback)()=nullptr;
}
struct RF455GdiFont::State {
    IDirect3DDevice9*device=nullptr;IDirect3DTexture9*texture=nullptr;
    IDirect3DStateBlock9*blocks[2]={};
    HDC dc=nullptr;HBITMAP bitmap=nullptr;HFONT font=nullptr;DWORD*bits=nullptr;
    unsigned width=0,height=0,cellWidth=0,cellHeight=0,columns=0,nextRow=0,hits=0,uploads=0;
    std::vector<Row>rows;

    SIZE measure(const wchar_t*text,unsigned count)const{
        SIZE size={};GetTextExtentPoint32W(dc,text,count,&size);
        if(!size.cy)size.cy=cellHeight;
        return size;
    }
    Entry&cache(const wchar_t*text,unsigned count,unsigned&rowIndex){
        for(unsigned y=0;y<rows.size();++y)for(auto&entry:rows[y].entries){
            if(entry.text.size()==count&&!std::wmemcmp(entry.text.data(),text,count)){
                rowIndex=y;++hits;return entry;
            }
        }
        const auto size=measure(text,count);unsigned left=0;rowIndex=0;
        for(;rowIndex<rows.size();++rowIndex){
            auto&row=rows[rowIndex];left=row.entries.empty()?0:row.entries.back().right;
            if(width-left>=static_cast<unsigned>(size.cx)&&columns-row.characters>=count)break;
        }
        if(rowIndex==rows.size()){
            rowIndex=nextRow;nextRow=(nextRow+1)%rows.size();
            rows[rowIndex].entries.clear();rows[rowIndex].characters=0;left=0;
        }
        auto&row=rows[rowIndex];row.entries.push_back({std::wstring(text,count),left,left+size.cx});row.characters+=count;
        // 906DD0 publishes the cache entry before a possibly failed LockRect.
        ExtTextOutW(dc,0,0,ETO_OPAQUE,nullptr,text,count,nullptr);
        RECT rect={static_cast<LONG>(left),static_cast<LONG>(rowIndex*cellHeight),static_cast<LONG>(left+size.cx),static_cast<LONG>((rowIndex+1)*cellHeight)};
        D3DLOCKED_RECT lock={};
        if(SUCCEEDED(texture->LockRect(0,&lock,&rect,0))){
            for(unsigned y=0;y<cellHeight;++y){
                auto*out=reinterpret_cast<WORD*>(static_cast<BYTE*>(lock.pBits)+y*lock.Pitch);
                for(LONG x=0;x<size.cx;++x){const unsigned alpha=(bits[y*width+x]>>4)&15;out[x]=alpha?static_cast<WORD>((alpha<<12)|0xfff):0;}
            }
            texture->UnlockRect(0);++uploads;
        }
        return row.entries.back();
    }
};
RF455GdiFont::RF455GdiFont():state(new State){}
RF455GdiFont::~RF455GdiFont(){release();}
void RF455GdiFont::release(){
    auto&s=*state;
    if(s.bitmap)DeleteObject(s.bitmap);
    if(s.dc)DeleteDC(s.dc);
    if(s.font)DeleteObject(s.font);
    for(auto&block:s.blocks)releaseCom(block);
    releaseCom(s.texture);s=State{};
}
HRESULT RF455GdiFont::initialize(IDirect3DDevice9*d,const char*name,unsigned charset,unsigned width,unsigned height,unsigned points){
    release();auto&s=*state;s.device=d;s.width=width;s.height=height;
    D3DCAPS9 caps={};d->GetDeviceCaps(&caps);
    HRESULT hr=D3DXCreateTexture(d,width,height,1,0,D3DFMT_A4R4G4B4,D3DPOOL_MANAGED,&s.texture);
    if(FAILED(hr))return hr;
    for(auto&block:s.blocks)d->CreateStateBlock(D3DSBT_ALL,&block);
    for(auto&block:s.blocks){
        d->BeginStateBlock();prepare(d,s.texture);
        // Release the overwritten unused initial block;original leaks it.
        releaseCom(block);d->EndStateBlock(&block);
    }
    BITMAPINFO info={};info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);
    info.bmiHeader.biWidth=width;info.bmiHeader.biHeight=-3*static_cast<int>(points);
    info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;
    s.dc=CreateCompatibleDC(nullptr);
    s.bitmap=CreateDIBSection(s.dc,&info,DIB_RGB_COLORS,reinterpret_cast<void**>(&s.bits),nullptr,0);
    if(!s.bitmap)return E_FAIL;
    SetMapMode(s.dc,MM_TEXT);
    const int pixelHeight=MulDiv(points,GetDeviceCaps(s.dc,LOGPIXELSY),72);
    s.font=CreateFontA(-pixelHeight,0,0,0,FW_NORMAL,FALSE,FALSE,FALSE,charset,0,0,0,0,name);
    if(!s.font)return E_FAIL;
    SelectObject(s.dc,s.bitmap);SelectObject(s.dc,s.font);
    SetTextColor(s.dc,RGB(255,255,255));SetBkColor(s.dc,0);SetTextAlign(s.dc,TA_TOP);
    SIZE cell={};GetTextExtentPointA(s.dc,"w",1,&cell);
    s.cellWidth=cell.cx;s.cellHeight=cell.cy;
    if(!s.cellWidth||!s.cellHeight)return E_FAIL;
    s.columns=width/s.cellWidth;s.rows.resize(height/s.cellHeight);
    return s.columns&& !s.rows.empty()?S_OK:E_FAIL;
}
SIZE RF455GdiFont::measure(const wchar_t*text)const{return state->measure(text,static_cast<unsigned>(std::wcslen(text)));}
SIZE RF455GdiFont::measureAnsi(const char*text)const{
    SIZE size={};if(text)GetTextExtentPoint32A(state->dc,text,static_cast<int>(std::strlen(text)),&size);
    if(!size.cy)size.cy=state->cellHeight;return size;
}
int RF455GdiFont::fitAnsi(const char*text,int maximumWidth)const{
    int fit=0;SIZE size={};if(text)GetTextExtentExPointA(state->dc,text,static_cast<int>(std::strlen(text)),maximumWidth,&fit,nullptr,&size);
    return fit;
}
RF455FontSnapshot RF455GdiFont::snapshot()const{const auto&s=*state;return {s.cellWidth,s.cellHeight,s.columns,static_cast<unsigned>(s.rows.size()),s.hits,s.uploads,s.font,s.texture};}
HRESULT RF455GdiFont::draw(float position[4],const wchar_t*text,DWORD color,DWORD flags,float scale,const float*clip){
    auto&s=*state;if(!s.device||!s.texture)return E_FAIL;
    unsigned count=static_cast<unsigned>(std::wcslen(text));if(!count)return S_OK;
    std::wstring bounded;if(count>=s.columns){bounded.assign(text,s.columns-1);text=bounded.c_str();count=s.columns-1;}
    prepare(s.device,s.texture);s.device->SetFVF(324);
    if(flags&0x400){s.device->SetSamplerState(0,D3DSAMP_MINFILTER,D3DTEXF_LINEAR);s.device->SetSamplerState(0,D3DSAMP_MAGFILTER,D3DTEXF_LINEAR);}
    std::vector<RF455FontVertex>vertices;vertices.reserve(54);
    const float initialX=position[0],initialY=position[1];
    auto append=[&](float x,float y,DWORD ink){
        unsigned row=0;const auto&entry=s.cache(text,count,row);
        float u0=static_cast<float>(static_cast<double>(entry.left)/s.width),u1=static_cast<float>(static_cast<double>(entry.right)/s.width);
        float v0=static_cast<float>(static_cast<double>(row*s.cellHeight)/s.height),v1=static_cast<float>(static_cast<double>((row+1)*s.cellHeight)/s.height);
        if((flags&0x80)&&clip){const float du=u1-u0,dv=v1-v0;u1=u0+du*clip[1];u0+=du*clip[0];v1=v0+dv*clip[3];v0+=dv*clip[2];}
        const float w=static_cast<float>(s.width*(static_cast<double>(u1)-u0)*scale),h=static_cast<float>(s.height*(static_cast<double>(v1)-v0)*scale);
        const float left=x-0.5f,right=x+w-0.5f,top=y-0.5f,bottom=y+h-0.5f;
        vertices.insert(vertices.end(),{{left,bottom,position[2],position[3],ink,u0,v1},{left,top,position[2],position[3],ink,u0,v0},{right,bottom,position[2],position[3],ink,u1,v1},{right,top,position[2],position[3],ink,u1,v0},{right,bottom,position[2],position[3],ink,u1,v1},{left,top,position[2],position[3],ink,u0,v0}});
    };
    const DWORD edge=outline|(color&0xff000000);
    if(flags&0x10){append(initialX+1,initialY+1,edge);append(initialX,initialY,color);position[0]=initialX;position[1]=initialY;}
    else if(flags&0x20){for(int x=0;x<3;++x)for(int y=0;y<3;++y)if(x!=1||y!=1)append(initialX+x,initialY+y,edge);append(initialX+1,initialY+1,color);position[0]=initialX+1;position[1]=initialY+1;}
    else if(flags&1){append(initialX,initialY,color);append(initialX+1,initialY,color);position[0]=initialX+1;position[1]=initialY;}
    else append(initialX,initialY,color);
    s.device->DrawPrimitiveUP(D3DPT_TRIANGLELIST,static_cast<UINT>(vertices.size()/3),vertices.data(),28);
    s.device->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE);return S_OK;
}
HRESULT RF455_LoadTextResources(IDirect3DDevice9*d,unsigned memory){
    if(loaded)return S_OK;loaded=true;const auto&settings=RF455_GetFontSettings();
    const unsigned w=memory>100000000?1024:512,h=memory>160000000?1024:512;
    HRESULT hr=fonts[0].initialize(d,settings.name,settings.charset,w,h,settings.points);
    registered=AddFontResourceA(".\\system\\010.TTF")>0;
    const char*aux=std::strcmp(settings.name,"Tahoma")==0?settings.name:"A010";
    const auto medium=fonts[1].initialize(d,aux,settings.charset,1024,128,16);
    const auto large=fonts[2].initialize(d,aux,settings.charset,1024,512,24);
    if(SUCCEEDED(hr)&&FAILED(medium))hr=medium;if(SUCCEEDED(hr)&&FAILED(large))hr=large;
    char log[96];std::sprintf(log,"RF455 Font:GDI:%d:%ld",settings.charset,hr);OutputDebugStringA(log);
    if(SUCCEEDED(hr)&&textReadyCallback)textReadyCallback();return hr;
}
void RF455_ReleaseTextResources(){if(!loaded)return;loaded=false;for(auto&font:fonts)font.release();if(registered){RemoveFontResourceA(".\\system\\010.TTF");registered=false;}}
HRESULT RF455_DrawText(float position[4],const wchar_t*text,DWORD color,DWORD flags,float scale,const float*clip){return fonts[(flags&0x40000000)?2:((flags&0x80000000)?1:0)].draw(position,text,color,flags,scale,clip);}
HRESULT RF455_DrawLegacyText(float position[4],const char*text,DWORD color,DWORD flags,const float*clip){
    const unsigned cp=RF455_GetFontSettings().codepage;const int count=MultiByteToWideChar(cp,0,text,-1,nullptr,0);if(!count)return E_FAIL;
    std::vector<wchar_t>wide(count);MultiByteToWideChar(cp,0,text,-1,wide.data(),count);return RF455_DrawText(position,wide.data(),color,flags,1,clip);
}
DWORD RF455_GetTextOutline(){return fonts[0].outline;}
SIZE RF455_MeasureLegacyText(const char* text){
    if(!text)return {0,0};
    const unsigned cp=RF455_GetFontSettings().codepage;
    const int count=MultiByteToWideChar(cp,0,text,-1,nullptr,0);
    if(!count)return {0,0};
    std::vector<wchar_t> wide(count);MultiByteToWideChar(cp,0,text,-1,wide.data(),count);
    return fonts[0].measure(wide.data());
}
SIZE RF455_MeasureTextAnsi(const char* text){return fonts[0].measureAnsi(text);}
SIZE RF455_MeasureTextAnsiFlags(const char* text,DWORD flags){return fonts[(flags&0x40000000)?2:((flags&0x80000000)?1:0)].measureAnsi(text);}
HRESULT RF455_DrawTextAnsiScaled(float position[4],const char* text,DWORD color,DWORD flags,float scale){
    const unsigned cp=RF455_GetFontSettings().codepage;const int count=MultiByteToWideChar(cp,0,text,-1,nullptr,0);if(!count)return E_FAIL;
    std::vector<wchar_t> wide(count);MultiByteToWideChar(cp,0,text,-1,wide.data(),count);return RF455_DrawText(position,wide.data(),color,flags,scale);
}
int RF455_FitTextAnsi(const char* text,int maximumWidth){return fonts[0].fitAnsi(text,maximumWidth);}
RF455FontSnapshot RF455_GetNormalFontSnapshot(){return fonts[0].snapshot();}
RF455FontSnapshot RF455_GetFontSnapshotFlags(DWORD flags){return fonts[(flags&0x40000000)?2:((flags&0x80000000)?1:0)].snapshot();}
bool RF455_TextResourcesReady(){return loaded&&fonts[0].snapshot().font!=nullptr;}
void RF455_SetTextReadyCallback(void(*callback)()){textReadyCallback=callback;}
void RF455_SetTextOutline(DWORD value){fonts[0].outline=value&0xffffff;}
