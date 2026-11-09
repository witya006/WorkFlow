#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/board/common/cboardmanager.h"
#include "cland.h"
#include "ccamera.h"
#include "datafile.h"
#include "datatable/cresourcedatamgr.h"
#include "input/imeedit.h"
#include "gameprogress/cgameprogress.h"
#include "userinterface/spritemgr.h"
#include "mainapp.h"
#include "userinterface/gamewindow/guichatwindow.h"
#include "client455_chat_profile.h"
#include "client455_chat_reference_tables.h"
#include "client455_nation_paths.h"
#include "client455_text_metrics.h"
#include <cstdio>
#include <cstring>
#include <mbstring.h>
#include <stdexcept>

namespace {
RF455ChatProfile& profile(){auto* value=RF455_GetChatProfile();if(!value||!value->Ready())throw std::logic_error("455 chat requires real initialized MainGame profile");return *value;}
FONT_INFO font(const RF455ChatFont& value){FONT_INFO out;out.bySize=value.size;out.dwStyle=value.style;out.dwColor=value.color;out.fScale455=value.scale;return out;}
const char* newline(const char* value){return reinterpret_cast<const char*>(_mbsstr(reinterpret_cast<const unsigned char*>(value),reinterpret_cast<const unsigned char*>("\n")));}
void append(std::string& out,const char* value,std::size_t bytes){
    if(out.size()+bytes>=1024)throw std::logic_error("455 chat overflowing shared1024 buffer domain");
    char buffer[1024];std::strcpy(buffer,out.c_str());_mbsnbcat(reinterpret_cast<unsigned char*>(buffer),reinterpret_cast<const unsigned char*>(value),bytes);out=buffer;
}
}
void CGUIChatWindow::SetChatFilterKernel455(BYTE category,DWORD value,BYTE pane){
    if(category>=14)return;if(pane>=4)pane=m_chat455.currentPane;if(pane>=4)return;
    if(category==pane&&category)value=1;
    m_chat455.filters[pane][category]=value;
    // Filter-button colors, GM mode and category7 network sideeffects are still
    // separate open UI producers; this is the confirmed stored/filter kernel.
}
DWORD CGUIChatWindow::GetChatFilter455(unsigned category,unsigned pane)const{
    if(category>=14||m_chat455.currentPane>=4)return 0;if(pane==4)pane=m_chat455.currentPane;
    if(pane>=4)throw std::logic_error("455 chat filter unsafe pane domain");return m_chat455.filters[pane][category];
}
void CGUIChatWindow::InitializeChat455(const char* settings){
    const auto* nation=RF455_GetNormalNationPaths();auto* owner=RF455_GetChatProfile();
    if(!nation->configured||!owner||!owner->Load(nation->nation))throw std::runtime_error("455 chat literal country script/provider unavailable");
    m_chat455.currentPane=0;unsigned zero=0;
    for(BYTE pane=0;pane<4;++pane){const DWORD mask=GetPrivateProfileIntA("ChatMode",RF455_CHAT_KEYS[pane],0,settings);zero+=mask==0;for(BYTE category=0;category<14;++category)SetChatFilterKernel455(category,(mask&(1u<<category))!=0,pane);}
    if(zero==4){
        for(BYTE category=0;category<14;++category)SetChatFilterKernel455(category,1,0);
        for(BYTE pane=1;pane<4;++pane){for(BYTE category=0;category<14;++category)SetChatFilterKernel455(category,0,pane);SetChatFilterKernel455(5,1,pane);}
    }
    DWORD mask=GetPrivateProfileIntA("DefModeOn",RF455_CHAT_KEYS[0],0,settings);
    for(BYTE category=0;category<14;++category)if(!(mask&(1u<<category))){SetChatFilterKernel455(category,1,0);mask|=1u<<category;}
    char text[32];std::sprintf(text,"%d",static_cast<int>(mask));WritePrivateProfileStringA("DefModeOn",RF455_CHAT_KEYS[0],text,settings);m_chat455.initialized=true;
}
CGUITextBoard* CGUIChatWindow::GetChatBoard455(unsigned pane){if(pane>=4)throw std::out_of_range("455 chat pane");return &m_uiChatBoard[pane];}
bool CGUIChatWindow::WrapChat455(const char* input,int firstWidth,int indentation,std::string& out){
    const int width=m_uiChatBoard[0].GetSizeX()-2*m_uiChatBoard[0].GetMarginX();if(width<=firstWidth)return false;
    if(!input)throw std::logic_error("455 chat null wrap string domain");
    const auto length=std::strlen(input);if(length>=1024)throw std::logic_error("455 chat wrap source overflow domain");
    if(indentation==1)(void)RF455_TextWidth(""); // target measures this, but indent count stays0
    int used=firstWidth;bool first=true;out.clear();std::size_t at=0;
    while(at<length){
        const char* line=newline(input+at);const auto span=line?std::size_t(line-(input+at)):length-at;std::size_t position=0;
        while(position<span){
            if(used>=width){append(out,"\n",1);used=0;continue;}
            int count=RF455_TextFitBytes(input+at+position,width-used);
            if(!count){if(!first&&!used)break;first=false;used=0;continue;}
            if(std::size_t(count)>span-position)count=static_cast<int>(span-position);
            if(!first){append(out,"\n",1);used=0;first=true;}
            append(out,input+at+position,count);used+=RF455_TextWidth(input+at+position,static_cast<WORD>(count));position+=count;
        }
        at+=span;
        if(line){append(out,"\n",1);first=false;used=0;++at;}
    }
    return true;
}
void CGUIChatWindow::InsertText455(const char* id,const char* text,int style,int category){
    if(category>=14)return;if(category<0||style<0||style>=36)throw std::logic_error("455 chat unsafe style/category domain");
    if(!m_chat455.initialized)throw std::logic_error("455 chat requires initialized category filters");auto& styles=profile();
    std::string header="\n";int firstWidth=0,indent=1;
    if(id){
        const auto& marker=styles.Prefix(style);if(marker.length)header="\n"+std::string(marker.text)+" ";auto headerFont=font(styles.Header(style));
        for(unsigned pane=0;pane<4;++pane)if(style==26||m_chat455.filters[pane][category]){
            auto& board=m_uiChatBoard[pane];const char* value=header.c_str()+(board.GetFragmentCount455()?0:1);board.InsertStyled455(const_cast<char*>(value),&headerFont,FALSE);
        }
        firstWidth=marker.length?RF455_TextWidth(marker.text)+10:RF455_TextWidth(header.c_str()+1);
        if(category==8){indent=0;if(const char* line=newline(header.c_str()+1))firstWidth=RF455_TextWidth(line+1);}
    }
    if(text){
        char buffer[1024];const int size=std::snprintf(buffer,sizeof(buffer),"%s : %s",id,text);
        if(size<0||size>=1024)throw std::logic_error("455 chat formatted message overflow domain");
        std::string wrapped;const char* value=WrapChat455(buffer,firstWidth,indent,wrapped)?wrapped.c_str():buffer;auto bodyFont=font(styles.Body(style));
        for(unsigned pane=0;pane<4;++pane)if(style==26||m_chat455.filters[pane][category])m_uiChatBoard[pane].InsertStyled455(const_cast<char*>(value),&bodyFont,TRUE);
    }
}
void CGUIChatWindow::InsertChatRaw455(const char* text,int style,int category){
    if(category>=14)return;if(category<0||style<0||style>=36)throw std::logic_error("455 chat unsafe raw category/style domain");
    if(!m_chat455.initialized)throw std::logic_error("455 chat requires initialized category filters");auto& styles=profile();
    if(text){auto bodyFont=font(styles.Body(style));for(unsigned pane=0;pane<4;++pane)if(m_chat455.filters[pane][category])m_uiChatBoard[pane].InsertStyled455(const_cast<char*>(text),&bodyFont,TRUE);}
}
