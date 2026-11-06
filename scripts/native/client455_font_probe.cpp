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
#include "mainapp.h"
#include "userinterface/guicontroller/guitext.h"
#include "client455_font.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include <cstdio>
#include <cstring>
#include <cwchar>
#include <vector>
extern CMainApp g_MainApp;
// Test fixture initializes the real Land member exactly as normal Create does,
// without entering the still-unported table readers. Explicit instantiation
// gives a compiler-typed member pointer;no guessed offset or changed class ABI.
template<class Tag,typename Tag::Type Member>struct MemberAccess{friend typename Tag::Type access(Tag){return Member;}};
struct LandMember{using Type=CLand CMainApp::*;friend Type access(LandMember);};
template struct MemberAccess<LandMember,&CMainApp::m_cLand>;

#define F_REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Font failure line%d\n",__LINE__);return 1;}}while(0)
static unsigned frameWidth=0,frameHeight=0;
static std::vector<unsigned char>capture(IDirect3DDevice9*d){
    IDirect3DSurface9*target=nullptr,*memory=nullptr;std::vector<unsigned char>pixels;
    if(FAILED(d->GetRenderTarget(0,&target)))return pixels;D3DSURFACE_DESC desc={};target->GetDesc(&desc);frameWidth=desc.Width;frameHeight=desc.Height;
    if(desc.Format!=D3DFMT_X8R8G8B8&&desc.Format!=D3DFMT_A8R8G8B8){target->Release();return pixels;}
    if(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr))&&SUCCEEDED(d->GetRenderTargetData(target,memory))){D3DLOCKED_RECT lock={};if(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY))){pixels.resize(desc.Width*desc.Height*4);for(unsigned y=0;y<desc.Height;++y)std::memcpy(pixels.data()+4*desc.Width*y,static_cast<BYTE*>(lock.pBits)+y*lock.Pitch,4*desc.Width);memory->UnlockRect();}}
    if(memory)memory->Release();target->Release();return pixels;
}
static int oracle(IDirect3DDevice9*d,const wchar_t*text){
    const auto&settings=RF455_GetFontSettings();RF455GdiFont font;F_REQUIRE(SUCCEEDED(font.initialize(d,settings.name,settings.charset,512,512,9)));
    const auto snapshot=font.snapshot();LOGFONTA logical={};F_REQUIRE(GetObjectA(snapshot.font,sizeof(logical),&logical)==sizeof(logical));F_REQUIRE(logical.lfCharSet==settings.charset&&logical.lfQuality==0&&logical.lfPitchAndFamily==0);
    HDC dc=CreateCompatibleDC(nullptr);BITMAPINFO info={};info.bmiHeader.biSize=40;info.bmiHeader.biWidth=512;info.bmiHeader.biHeight=-27;info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;DWORD*bits=nullptr;HBITMAP bitmap=CreateDIBSection(dc,&info,DIB_RGB_COLORS,reinterpret_cast<void**>(&bits),nullptr,0);
    HFONT expected=CreateFontIndirectA(&logical);SelectObject(dc,bitmap);SelectObject(dc,expected);SetTextColor(dc,0xffffff);SetBkColor(dc,0);SetTextAlign(dc,TA_TOP);SIZE extent={},cell={};GetTextExtentPoint32W(dc,text,static_cast<int>(std::wcslen(text)),&extent);GetTextExtentPointA(dc,"w",1,&cell);
    F_REQUIRE(snapshot.cellWidth==cell.cx&&snapshot.cellHeight==cell.cy);const auto measured=font.measure(text);F_REQUIRE(measured.cx==extent.cx&&measured.cy==extent.cy);
    F_REQUIRE(SUCCEEDED(d->BeginScene()));float p[]={20,20,.99f,1};F_REQUIRE(SUCCEEDED(font.draw(p,text,0xffffffff,0)));F_REQUIRE(SUCCEEDED(d->EndScene()));
    ExtTextOutW(dc,0,0,ETO_OPAQUE,nullptr,text,static_cast<UINT>(std::wcslen(text)),nullptr);GdiFlush();D3DLOCKED_RECT lock={};F_REQUIRE(SUCCEEDED(snapshot.texture->LockRect(0,&lock,nullptr,D3DLOCK_READONLY)));
    for(unsigned y=0;y<snapshot.cellHeight;++y){const auto*row=reinterpret_cast<const WORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch);for(int x=0;x<extent.cx;++x){const unsigned alpha=(bits[y*512+x]>>4)&15;F_REQUIRE(row[x]==(alpha?((alpha<<12)|0xfff):0));}}
    snapshot.texture->UnlockRect(0);F_REQUIRE(SUCCEEDED(d->BeginScene()));F_REQUIRE(SUCCEEDED(font.draw(p,text,0xff99ff00,0x20)));F_REQUIRE(SUCCEEDED(d->EndScene()));F_REQUIRE(font.snapshot().uploads==1&&font.snapshot().cacheHits>=9);
    font.release();DeleteObject(bitmap);DeleteDC(dc);DeleteObject(expected);d->SetTexture(0,nullptr);return 0;
}
static int runFontProbe(int argc,char**argv){
    if(argc!=2)return 200;SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    F_REQUIRE(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData());InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();F_REQUIRE((g_MainApp.*access(LandMember{})).Create());F_REQUIRE(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)));
    auto*d=GetD3dDevice();F_REQUIRE(d);auto*pack=RF455_GetNormalLanguagePack();const char*text=pack->get(0);F_REQUIRE(*text);const int count=MultiByteToWideChar(pack->codepage,0,text,-1,nullptr,0);std::vector<wchar_t>wide(count);F_REQUIRE(count&&MultiByteToWideChar(pack->codepage,0,text,-1,wide.data(),count));
    F_REQUIRE(oracle(d,wide.data())==0);
    CGUIText label;label.SetString(const_cast<char*>(text));label.SetPos(20,20);label.Show(TRUE);FONT_INFO style;style.dwColor=0xffffffff;style.dwStyle=0;label.SetFont(&style);
    F_REQUIRE(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()));F_REQUIRE(label.Draw());F_REQUIRE(SUCCEEDED(d->EndScene()));const auto actual=capture(d);F_REQUIRE(!actual.empty());
    F_REQUIRE(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()));d->SetRenderState(D3DRS_ZENABLE,FALSE);float p[]={20,20,.99f,1};F_REQUIRE(SUCCEEDED(RF455_DrawText(p,wide.data(),0xffffffff,0)));d->SetRenderState(D3DRS_ZENABLE,TRUE);F_REQUIRE(SUCCEEDED(d->EndScene()));F_REQUIRE(capture(d)==actual);
    D3DVIEWPORT9 viewport={};F_REQUIRE(SUCCEEDED(d->GetViewport(&viewport)));unsigned colored=0;for(unsigned y=viewport.Y;y<viewport.Y+viewport.Height;++y)for(unsigned x=viewport.X;x<viewport.X+viewport.Width;++x){DWORD pixel;std::memcpy(&pixel,actual.data()+4*(y*frameWidth+x),4);colored+=(pixel&0xffffff)!=0x102030;}F_REQUIRE(colored>10);
    {RF455GdiFont recycle;const auto&setting=RF455_GetFontSettings();F_REQUIRE(SUCCEEDED(recycle.initialize(d,setting.name,setting.charset,128,32,9)));const auto slots=recycle.snapshot();F_REQUIRE(SUCCEEDED(d->BeginScene()));for(unsigned i=0;i<slots.rows*slots.columns+2;++i){wchar_t value[8];std::swprintf(value,8,L"W%u",i);float at[]={1,1,.99f,1};F_REQUIRE(SUCCEEDED(recycle.draw(at,value,0xffffffff,0)));}const unsigned uploads=recycle.snapshot().uploads;float at[]={1,1,.99f,1};F_REQUIRE(SUCCEEDED(recycle.draw(at,L"W0",0xffffffff,0x400)));F_REQUIRE(recycle.snapshot().uploads==uploads+1);F_REQUIRE(SUCCEEDED(d->EndScene()));DWORD blend=1,filter=0;d->GetRenderState(D3DRS_ALPHABLENDENABLE,&blend);d->GetSamplerState(0,D3DSAMP_MINFILTER,&filter);F_REQUIRE(!blend&&filter==D3DTEXF_LINEAR);recycle.release();d->SetTexture(0,nullptr);}
    FILE*frame=std::fopen("font-frame.bgra","wb");F_REQUIRE(frame);std::fwrite(actual.data(),1,actual.size(),frame);std::fclose(frame);
    R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE*out=std::fopen(argv[1],"wb");F_REQUIRE(out);std::fprintf(out,"{\"status\":\"PASS\",\"codepage\":%u,\"width\":%u,\"height\":%u,\"real_ui_text_consumer\":true,\"wide_bridge_equal_frame\":true,\"gdi_metrics_and_atlas_equal\":true,\"unicode_cache_reused\":true,\"colored_pixels\":%u}\n",pack->codepage,frameWidth,frameHeight,colored);std::fclose(out);return 0;
}
static LONG failure(EXCEPTION_POINTERS*info){
    FILE*f=std::fopen("exception.json","wb");if(f){std::fprintf(f,"{\"code\":%lu,\"address\":%lu,\"base\":%lu,\"target\":%lu}\n",info->ExceptionRecord->ExceptionCode,reinterpret_cast<DWORD>(info->ExceptionRecord->ExceptionAddress),reinterpret_cast<DWORD>(GetModuleHandleA(nullptr)),static_cast<DWORD>(info->ExceptionRecord->ExceptionInformation[1]));std::fclose(f);}return EXCEPTION_EXECUTE_HANDLER;
}
static LONG WINAPI observeFailure(EXCEPTION_POINTERS*info){if(info->ExceptionRecord->ExceptionCode==EXCEPTION_ACCESS_VIOLATION)failure(info);return EXCEPTION_CONTINUE_SEARCH;}
int main(int argc,char**argv){AddVectoredExceptionHandler(1,observeFailure);__try{return runFontProbe(argc,argv);}__except(failure(GetExceptionInformation())){return 99;}}
