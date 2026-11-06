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
#include "userinterface/guicontroller/guitextboard.h"
#include "mainapp.h"
#include "client455_font.h"
#include "client455_language.h"
#include "client455_nation_paths.h"
#include "client455_text_metrics.h"
#include <cstdio>
#include <cstring>
#include <cwchar>
#include <mbctype.h>
#include <stdexcept>
#include <string>
#include <vector>
extern CMainApp g_MainApp;
static void check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
static char* mutableText(const char* text){return const_cast<char*>(text);}
static void start(CGUITextBoard& board,WORD line,WORD fragment,WORD offset){WORD actualFragment=0,actualOffset=0;check(board.GetLineStart455(line,actualFragment,actualOffset)&&actualFragment==fragment&&actualOffset==offset,"line marker golden");}
static std::string encode(const wchar_t* value,unsigned cp){const int count=WideCharToMultiByte(cp,0,value,-1,nullptr,0,nullptr,nullptr);check(count>0,"encode size");std::vector<char> text(count);check(WideCharToMultiByte(cp,0,value,-1,text.data(),count,nullptr,nullptr)>0,"encode");return text.data();}
static int oracle(HDC dc,const char* text,int bytes=-1){SIZE size={};check(GetTextExtentPoint32A(dc,text,bytes<0?static_cast<int>(std::strlen(text)):bytes,&size)!=0,"independent GDI extent");return size.cx;}
struct Frame {unsigned pixels=0,red=0,green=0;int firstY=480;};
static Frame capture(CGUITextBoard& board,const char* name){
    auto* device=GetD3dDevice();check(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0xff102030,1,0)),"clear");check(SUCCEEDED(device->BeginScene()),"begin");check(board.Draw()!=0,"actual TextBoard draw");check(SUCCEEDED(device->EndScene()),"end");
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;check(SUCCEEDED(device->GetRenderTarget(0,&target)),"render target");D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    check(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)),"readback surface");check(SUCCEEDED(device->GetRenderTargetData(target,memory)),"readback");D3DLOCKED_RECT lock={};check(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"lock");D3DVIEWPORT9 view={};device->GetViewport(&view);check(view.Width==640&&view.Height==480,"viewport");
    FILE* output=std::fopen(name,"wb");check(output!=nullptr,"frame output");Frame result;
    for(unsigned y=view.Y;y<view.Y+view.Height;++y){auto* row=reinterpret_cast<const DWORD*>(static_cast<const BYTE*>(lock.pBits)+y*lock.Pitch)+view.X;std::fwrite(row,4,view.Width,output);for(unsigned x=0;x<view.Width;++x){const DWORD value=row[x]&0xffffff;if(value!=0x102030){++result.pixels;if(static_cast<int>(y-view.Y)<result.firstY)result.firstY=y-view.Y;}result.red+=value==0xff0000;result.green+=value==0x00ff00;}}
    std::fclose(output);memory->UnlockRect();memory->Release();target->Release();return result;
}
static int run(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    check(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"language");InitR3Engine();GetR3State()->mScreenXsize=640;GetR3State()->mScreenYsize=480;GetR3State()->mbFullScreen=FALSE;ForceFullScreen();check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device");
    const auto snapshot=RF455_GetNormalFontSnapshot();HDC dc=CreateCompatibleDC(nullptr);HGDIOBJ previous=SelectObject(dc,snapshot.font);const int w=oracle(dc,"W"),h=snapshot.cellHeight;check(w>1&&oracle(dc,"WW")==2*w,"fixture glyph width");const unsigned cp=RF455_GetFontSettings().codepage;
    FONT_INFO font;check(sizeof(FONT_INFO)==16&&sizeof(CGUITextInfo)==28&&font.bySize==0&&font.dwStyle==0&&font.dwColor==0xffffffff&&font.fScale455==1,"typed font and text info");
    CGUITextInfo info;check(info.GetLength455()==0,"initial cached length");info.SetText(mutableText("WW"));info.GetText()[1]=0;check(info.GetLength455()==2,"cached length survives in-place edit");info.SetText(mutableText("W"));info.SetFont(nullptr);info.Clear();check(info.GetLength455()==1&&info.GetText()==nullptr,"Clear retains cached length");
    bool refused=false;try{std::string huge(0x10000,'W');info.SetText(&huge[0]);}catch(const std::length_error&){refused=true;}check(refused,"owned oversized refusal");
    char copy[300]="seed";std::string many(300,'A');RF455_CopyGuiTextBytes8(copy,many.c_str(),0);check(!std::strcmp(copy,"seed"),"BYTE zero leaves destination");RF455_CopyGuiTextBytes8(copy,many.c_str(),255);check(std::strlen(copy)==254,"BYTE254 copy");RF455_CopyGuiTextBytes8(copy,"new",256);check(std::strlen(copy)==254,"BYTE256 wraps and leaves destination");RF455_CopyGuiTextBytes8(copy,"new",257);check(!*copy,"BYTE257 capacity1");RF455_CopyGuiTextBytes8(copy,nullptr,1);RF455_CopyGuiTextBytes8(nullptr,"new",5);
    FONT_INFO parsed;parsed.dwStyle=7;check(RF455_ParseFontTag("<FONT style=R3_HAN_OUTLINE >",parsed)&&parsed.dwStyle==32,"case-insensitive font/style value");parsed.dwStyle=7;check(RF455_ParseFontTag("<font style=R3_HAN_OUTLINE>",parsed)&&parsed.dwStyle==7,"style token includes closing bracket");
    parsed=font;parsed.dwStyle=7;check(RF455_ParseFontTag("<font color=ff112233 style=R3_HAN_OUTLINE >",parsed)&&parsed.dwColor==0xff112233&&parsed.dwStyle==7,"sticky color precedence");parsed=font;check(RF455_ParseFontTag("<font style=R3_HAN_SHADOW color=ff112233 >",parsed)&&parsed.dwStyle==16&&parsed.dwColor==0xff112233,"style then color");check(RF455_IsClosingFontTag("< /FONTsuffix >")&&!RF455_IsClosingFontTag("<font>"),"closing prefix rule");refused=false;try{RF455_ParseFontTag("<font Color=ff112233 >",parsed);}catch(const std::invalid_argument&){refused=true;}check(refused,"case-sensitive unknown attribute non-advancing domain refused");
    CGUITextBoard board;board.SetSize(2*w,10*h);board.InsertText(mutableText("WWWW"));check(board.GetTotalLineNum()==2,"pixel width wraps");start(board,0,0,0);start(board,1,0,2);board.InsertText(mutableText("WW"));check(board.GetTotalLineNum()==3&&board.GetFragmentCount455()==2,"append reconstructs last line");start(board,2,1,0);
    board.Clear();board.SetSize(4*w,10*h);board.InsertText(mutableText("WW"));board.InsertText(mutableText("WW"));check(board.GetTotalLineNum()==1,"fragments share a line");WORD endFragment=0,endOffset=0;check(board.GetLineEnd455(0,endFragment,endOffset)&&endFragment==1&&endOffset==1,"line spans fragments");board.SetSize(w,10*h);check(board.GetTotalLineNum()==4,"width change fully reflows");board.SetMargin(1,0);check(board.GetTotalLineNum()==4,"margin-only does not reflow");board.SetSize(2*w+2,10*h);check(board.GetTotalLineNum()==2,"changed width reflows using current margins");start(board,1,1,0);
    board.Clear();board.SetMargin(0,0);board.SetSize(1000,10*h);board.InsertText(mutableText("W\nW\n"));check(board.GetTotalLineNum()==3,"newline and trailing empty line");start(board,0,0,0);start(board,1,0,1);start(board,2,0,3);board.Clear();board.InsertText(mutableText("\nW"));check(board.GetTotalLineNum()==1,"target leading newline marker quirk");start(board,0,0,0);
    board.Clear();board.InsertText(mutableText("W\n"));board.InsertText(mutableText("W"));check(board.GetTotalLineNum()==2,"append after newline reuses marker");start(board,1,0,1);check(board.ResizeToText455()&&board.GetSizeX()==w&&board.GetSizeY()==2*h,"unwrapped extent across fragments");
    board.Clear();board.SetSize(1,10*h);board.InsertText(mutableText("W"));check(board.GetTotalLineNum()==0&&board.GetFragmentCount455()==1,"unfittable glyph retained without invented line");board.SetSize(w,10*h);check(board.GetTotalLineNum()==1,"later width recovers retained glyph");
    const auto localized=encode(cp==949?L"\uac00\uac00":L"\u041f\u041f",cp);const int firstBytes=cp==949?2:1;const int glyphWidth=oracle(dc,localized.c_str(),firstBytes);board.Clear();board.SetSize(glyphWidth,10*h);board.InsertText(mutableText(localized.c_str()));check(board.GetTotalLineNum()==2,"localized pixel wrap");start(board,1,0,static_cast<WORD>(firstBytes));
    // Resource language and CRT multibyte state are separate providers. Prove
    // the copy helper under both explicit CRT modes, then restore ambient state.
    const int ambientMbcp=_getmbcp();const auto korean=encode(L"\uac00",949);
    check(_setmbcp(949)==0,"set DBCS oracle mode");RF455_CopyGuiTextBytes8(copy,korean.c_str(),2);check(!*copy,"DBCS copy drops partial lead");
    check(_setmbcp(1251)==0,"set SBCS oracle mode");RF455_CopyGuiTextBytes8(copy,korean.c_str(),2);check(copy[0]==korean[0]&&!copy[1],"SBCS copy preserves single byte");
    // _getmbcp() returns0 for an SBCS ANSI page too. Restoring that reported
    // value would select _MB_CP_SBCS rather than the actual initial ANSI page.
    check(_setmbcp(_MB_CP_ANSI)==0&&_getmbcp()==ambientMbcp,"restore initial systemANSI CRT mode");
    board.Clear();board.SetSize(w,10*h);board.SetLimitLineNum(2);board.InsertText(mutableText("WWWW"));check(board.GetTotalLineNum()==2&&board.GetFragmentCount455()==1,"retention inside fragment");start(board,0,0,2);board.InsertText(mutableText("WW"));check(board.GetTotalLineNum()==2&&board.GetFragmentCount455()==1&&board.GetFragmentBase455()==1,"retention releases old fragment");start(board,0,0,0);
    board.Clear();board.SetLimitLineNum(1);for(unsigned i=0;i<65536;++i)board.InsertText(mutableText("W"));check(board.GetTotalLineNum()==1&&board.GetFragmentCount455()==1&&board.GetFragmentBase455()==1,"WORD fragment index rebase atffff");start(board,0,0,0);board.Clear();board.SetLimitLineNum(0x10000);board.InsertText(mutableText("WW"));check(board.GetTotalLineNum()==1,"zero WORD limit retains one marker");
    CGUIScrollbar scrollbar;POINT arrow={12,8},bar={5,18};scrollbar.SetTopArrowSize(arrow);scrollbar.SetBottomArrowSize(arrow);scrollbar.SetBarSize(bar);scrollbar.SetSize(12,120);board.Clear();board.SetLimitLineNum(1000);board.SetSize(w,2*h);board.AddScrollbar(&scrollbar);board.SetAutoScroll(TRUE);board.InsertText(mutableText("WWWW"));check(scrollbar.GetTotalAmount()==2*h&&scrollbar.GetCurrentAmount()==2*h&&board.GetViewedLine455()==2,"scroll range and auto bottom");scrollbar.SetCurrentAmount(h);_scroll_event event={};board.ScrollEvent(event);check(board.GetViewedLine455()==1,"scroll event line position");scrollbar.SetCurrentAmount(2*h);scrollbar.SetTotalAmount(h);check(scrollbar.GetCurrentAmount()==h,"target total setter clamps previous current");board.SetSize(w,3*h);check(scrollbar.GetTotalAmount()==h&&board.GetViewedLine455()==1,"resize clamps scroll view");board.SetSize(w,10*h);check(scrollbar.GetTotalAmount()==0&&scrollbar.GetCurrentAmount()==0&&board.GetViewedLine455()==0,"resize removes scroll range");board.Clear();check(scrollbar.GetTotalAmount()==0,"clear resets scrollbar");board.AddScrollbar(nullptr);
    board.SetAutoScroll(FALSE);board.SetLimitLineNum(1000);board.SetSize(500,100);board.InsertFormatted455(mutableText("Seed"),&font);std::string wrapped(255,'A');board.InsertFormatted455(&wrapped[0],&font);check(board.GetFragmentCount455()==2&&!std::strcmp(board.GetFragment455(1)->GetText(),"Seed"),"formatted255 capacity wraps and reuses scratch");
    board.Clear();board.SetPos(20,20);board.SetSize(500,100);board.Show(TRUE);FONT_INFO red=font;red.dwColor=0xffff0000;FONT_INFO green=font;green.dwColor=0xff00ff00;board.InsertText(mutableText("WW"),&red);board.InsertText(mutableText("WW"),&green);const auto colors=capture(board,"textboard-colors.bgra");check(colors.red>0&&colors.green>0,"real multi-font fragment colors");
    board.Clear();board.InsertFormatted455(mutableText("Normal <font color=ffff0000 >red</font> <font style=R3_HAN_OUTLINE color=ff00ff00 >green</font> end"),&font);check(board.GetFragmentCount455()==5,"formatted fragment count");check(board.GetFragment455(1)->GetFont()->dwColor==0xffff0000&&board.GetFragment455(3)->GetFont()->dwColor==0xff00ff00&&board.GetFragment455(3)->GetFont()->dwStyle==32,"formatted font metadata");const auto markup=capture(board,"textboard-markup.bgra");check(markup.red>0&&markup.green>0,"actual formatted GPU text");
    board.Clear();board.SetSize(500,4*h);board.SetAutoScroll(TRUE);const auto greeting=encode(cp==949?L"Wi \uac00\ub098\ub2e4 455":L"Wi \u041f\u0440\u0438\u0432\u0435\u0442 455",cp);board.InsertText(mutableText(greeting.c_str()));const auto bottom=capture(board,"textboard-bottom.bgra");check(bottom.pixels>10&&bottom.firstY>=20+3*h&&bottom.firstY<20+4*h,"short auto-scroll text bottom alignment");
    board.SetAutoScroll(FALSE);board.SetHighlight455(TRUE,0xff202040);const auto highlight=capture(board,"textboard-highlight.bgra");check(highlight.pixels>static_cast<unsigned>(400*h),"line highlight rectangle");board.SetHighlight455(FALSE,0xffffffff);board.Clear();
    SelectObject(dc,previous);DeleteDC(dc);R3ReleaseTextTexture();g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"result");
    std::fprintf(output,"{\"status\":\"PASS\",\"codepage\":%u,\"typed_FONT_INFO16_TextInfo28\":true,\"actual_TextBoard\":true,\"pixel_wrap_and_DBCS\":true,\"fragment_line_cache\":true,\"newline_and_margin_quirks\":true,\"retention_and_WORD_rebase\":true,\"markup_and_sticky_attributes\":true,\"BYTE_copy_wrap_and_reuse\":true,\"scroll_amount_and_view\":true,\"real_GPU_fragments\":true,\"color_pixels\":%u,\"markup_pixels\":%u,\"bottom_pixels\":%u,\"ambient_crt_mbcp\":%d,\"system_acp\":%u,\"explicit_crt_dbcs_sbcs_copy\":true,\"full_scrollbar_input\":false,\"full_briefing\":false,\"full_Tutorial\":false}\n",cp,colors.pixels,markup.pixels,bottom.pixels,ambientMbcp,GetACP());std::fclose(output);return 0;
}
static LONG filter(EXCEPTION_POINTERS* info){return info->ExceptionRecord->ExceptionCode==0xe06d7363?EXCEPTION_CONTINUE_SEARCH:EXCEPTION_EXECUTE_HANDLER;}
static int guarded(){__try{return run();}__except(filter(GetExceptionInformation())){return 99;}}
int main(){try{return guarded();}catch(const std::exception& error){std::fprintf(stderr,"TextBoard: %s\n",error.what());return 1;}}
