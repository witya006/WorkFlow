#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "item/citemmgr.h"
#include "input/imeedit.h"
#include "baseheader.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "userinterface/guicontroller/guitext.h"
#include "mainapp.h"
#include "client455_font.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_text_metrics.h"
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <cwchar>
#include <stdexcept>
#include <string>
#include <vector>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
struct EarlyText {
    CGUIText label;
    EarlyText(){label.SetString(const_cast<char*>("Early text"));auto* temporary=new CGUIText;temporary->SetString(const_cast<char*>("Temporary early text"));delete temporary;}
} earlyText;
static std::string encode(const wchar_t* text,unsigned codepage){
    const int length=WideCharToMultiByte(codepage,0,text,-1,nullptr,0,nullptr,nullptr);check(length>0,"encode size");
    std::vector<char> bytes(length);check(WideCharToMultiByte(codepage,0,text,-1,bytes.data(),length,nullptr,nullptr)>0,"encode");return bytes.data();
}
static bool leadAt(const std::string& text,int index,unsigned codepage){
    for(int i=0;i<=index&&i<static_cast<int>(text.size());++i){if(IsDBCSLeadByteEx(codepage,BYTE(text[i]))){if(i==index)return true;++i;}}
    return false;
}
static unsigned capture(CGUIText& label){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");
    check(SUCCEEDED(device->BeginScene()),"begin");check(label.Draw()!=0,"actual text draw");check(SUCCEEDED(device->EndScene()),"end");
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");
    D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 viewport={};device->GetViewport(&viewport);
    check(viewport.Width==640&&viewport.Height==480,"viewport");FILE* output=std::fopen("text-frame.bgra","wb");check(output!=nullptr,"frame");unsigned colored=0;
    for(unsigned y=viewport.Y;y<viewport.Y+viewport.Height;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+viewport.X;std::fwrite(row,4,viewport.Width,output);
        for(unsigned x=0;x<viewport.Width;++x)colored+=(row[x]&0xffffff)!=0x102030;}
    std::fclose(output);memory->UnlockRect();memory->Release();target->Release();return colored;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"real language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"D3D init");
    const auto snapshot=RF455_GetNormalFontSnapshot();check(snapshot.font&&snapshot.cellHeight,"loaded default font");HDC oracle=CreateCompatibleDC(nullptr);HGDIOBJ previous=SelectObject(oracle,snapshot.font);
    SIZE earlySize={};GetTextExtentPoint32A(oracle,"Early text",10,&earlySize);check(earlyText.label.GetSizeX()==earlySize.cx&&earlyText.label.GetSizeY()==LONG(snapshot.cellHeight),"early geometry deferred until real font creation");
    const auto codepage=RF455_GetFontSettings().codepage;std::vector<std::string> samples={"","iiii","WWWW","AVATAR Wi 455",RF455_GetNormalLanguagePack()->get(106)};
    // This probe is compiled with the legacy project's source codepage. Use
    // universal escapes so the fixture is independent of that compiler locale.
    const wchar_t* sample=codepage==949?L"Wi \uac00\ub098\ub2e4 455":L"Wi \u041f\u0440\u0438\u0432\u0435\u0442 455";
    samples.push_back(encode(sample,codepage));
    std::vector<wchar_t> decoded(std::wcslen(sample)+1);
    check(MultiByteToWideChar(codepage,0,samples.back().c_str(),-1,decoded.data(),static_cast<int>(decoded.size()))>0&&std::wcscmp(decoded.data(),sample)==0,"localized fixture codepage roundtrip");
    unsigned widths=0,fits=0;
    check(RF455_TextWidth(nullptr)==0&&RF455_TextWidth("abc",0)==0&&RF455_TextFitBytes(nullptr,30)==0,"owned invalid-pointer guards");
    for(const auto& text:samples){
        SIZE expected={};GetTextExtentPoint32A(oracle,text.c_str(),static_cast<int>(text.size()),&expected);
        check(RF455_TextWidth(text.c_str())==expected.cx,"full width independent GDI oracle");
        for(unsigned count=0;count<=text.size()+1;++count){
            const auto prefix=text.substr(0,std::min<std::size_t>(count,text.size()));SIZE partial={};GetTextExtentPoint32A(oracle,prefix.c_str(),static_cast<int>(prefix.size()),&partial);
            check(RF455_TextWidth(text.c_str(),WORD(count))==partial.cx,"exact byte-prefix width including partial DBCS");++widths;
        }
        for(int limit=-1;limit<=expected.cx+2;++limit){
            int count=0;SIZE extent={};GetTextExtentExPointA(oracle,text.c_str(),static_cast<int>(text.size()),limit,&count,nullptr,&extent);
            if(count&&leadAt(text,count-1,codepage))--count;
            check(RF455_TextFitBytes(text.c_str(),limit)==count,"fit byte count/DBCS boundary independent oracle");++fits;
        }
        CGUIText label;FONT_INFO font;font.bySize=0;font.dwStyle=0;font.dwColor=0xffffffff;label.SetFont(&font);label.SetString(const_cast<char*>(text.c_str()));
        check(label.GetSizeX()==expected.cx&&label.GetSizeY()==static_cast<LONG>(snapshot.cellHeight),"actual CGUIText dimensions");
        for(DWORD style:{0x80000000U,0x40000000U,0xc0000000U}){
            font.dwStyle=style;label.SetFont(&font);label.SetString(const_cast<char*>(text.c_str()));const WORD cells=WORD(expected.cx/12);
            check(label.GetSizeX()==((style&0x40000000)?16*cells:expected.cx)&&label.GetSizeY()==((style&0x40000000)?32:LONG(snapshot.cellHeight)),"455high-style fallthrough");
        }
    }
    // Some country fonts are monospaced; the independent GDI oracle above is
    // authoritative for both proportional and fixed-width profiles.
    CGUIText label;FONT_INFO font;font.bySize=0;font.dwStyle=0;font.dwColor=0xffffffff;label.SetFont(&font);label.SetString(const_cast<char*>(samples.back().c_str()));label.SetPos(20,20);label.Show(TRUE);
    const auto width=label.GetSizeX();font.dwStyle=0x40000000;label.SetFont(&font);check(label.GetSizeX()==width,"SetFont alone does not recalculate size");font.dwStyle=0;label.SetFont(&font);
    const unsigned colored=capture(label);check(colored>10,"actual text pixels");label.SetString(nullptr);check(label.GetSizeX()==0&&label.GetSizeY()==LONG(snapshot.cellHeight),"NULL string geometry");
    SelectObject(oracle,previous);DeleteDC(oracle);
    const auto settings=RF455_GetFontSettings();const int originalHeight=RF455_DefaultTextHeight();
    RF455_ReleaseTextResources();RF455_SetFontParameters(settings.name,16,settings.height,settings.charset);check(SUCCEEDED(RF455_LoadTextResources(GetD3dDevice(),256000000)),"reload larger GDI font");
    check(RF455_GetNormalFontSnapshot().cellHeight!=snapshot.cellHeight&&RF455_DefaultTextHeight()==originalHeight,"first default-height cache retained across font reload");
    RF455_ReleaseTextResources();RF455_SetFontParameters(settings.name,settings.points,settings.height,settings.charset);check(SUCCEEDED(RF455_LoadTextResources(GetD3dDevice(),256000000)),"restore font");
    R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"output");
    std::fprintf(output,"{\"status\":\"PASS\",\"codepage\":%u,\"byte_prefix_oracle_cases\":%u,\"fit_oracle_cases\":%u,\"actual_CGUIText_geometry\":true,\"style_flag_fallthrough\":true,\"default_height_cache\":true,\"partial_DBCS_prefix\":true,\"early_geometry_after_font_ready\":true,\"localized_fixture_roundtrip\":true,\"rendered_pixels\":%u,\"full_TextBoard\":false,\"FreeType_route\":false,\"full_Tutorial\":false}\n",codepage,widths,fits,colored);std::fclose(output);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"Text metrics: %s\n",error.what());return 1;}}
