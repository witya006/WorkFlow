#include "userinterface/guicontroller/guitextboard.h"
#include "client455_text_metrics.h"
#include <algorithm>
#include <cctype>
#include <cstdio>
#include <cstring>
#include <mbstring.h>
#include <stdexcept>
#include <string>
#undef min
#undef max

namespace {
// All recovered TextBoard copy sites use the same target scratch region.
// Other target users of102DAB0 have not yet been ported to this provider.
char scratch[256]={};
const char* findText(const char* text,const char* needle){
    return reinterpret_cast<const char*>(_mbsstr(reinterpret_cast<const unsigned char*>(text),reinterpret_cast<const unsigned char*>(needle)));
}
int comparePrefix(const char* a,const char* b,unsigned bytes,bool ignoreCase){
    auto* left=reinterpret_cast<const unsigned char*>(a);auto* right=reinterpret_cast<const unsigned char*>(b);
    return ignoreCase?_mbsnbicmp(left,right,bytes):_mbsnbcmp(left,right,bytes);
}
}

void RF455_CopyGuiTextBytes8(char* destination,const char* source,unsigned capacity){
    const BYTE count=static_cast<BYTE>(capacity);
    if(!destination||!count)return;
    if(!source){destination[0]=0;return;}
    _mbsnbcpy(reinterpret_cast<unsigned char*>(destination),reinterpret_cast<const unsigned char*>(source),count-1);
    destination[count-1]=0;
}

bool RF455_ParseFontTag(const char* value,FONT_INFO& font){
    if(!value)return false;const std::string tag(value);const auto size=tag.size();
    if(size<6||tag.front()!='<'||tag.back()!='>')return false;
    std::size_t at=1;while(at<size&&tag[at]==' ')++at;
    if(at==size||comparePrefix(tag.c_str()+at,"font",4,true))return false;
    at+=4;bool color=false,style=false,pendingValue=false;
    while(at<size){
        if(tag[at]==' '){++at;continue;}
        if(pendingValue){
            // Target uses an unchecked32-byte %s buffer. Keep the supported
            // token domain and refuse overflow/non-advancing malformed tags.
            if(!color&&!style)throw std::invalid_argument("455 font tag has value without attribute");
            auto begin=at;while(begin<size&&std::isspace(static_cast<unsigned char>(tag[begin])))++begin;
            auto end=begin;while(end<size&&!std::isspace(static_cast<unsigned char>(tag[end])))++end;
            const auto token=tag.substr(begin,end-begin);
            if(token.empty()||token.size()>=32)throw std::length_error("455 font token exceeds verified32-byte domain");
            if(color){unsigned ink=0;if(std::sscanf(tag.c_str()+at,"%x",&ink)==1)font.dwColor=ink;}
            else if(!_mbsicmp(reinterpret_cast<const unsigned char*>(token.c_str()),reinterpret_cast<const unsigned char*>("R3_HAN_OUTLINE")))font.dwStyle=32;
            else if(!_mbsicmp(reinterpret_cast<const unsigned char*>(token.c_str()),reinterpret_cast<const unsigned char*>("R3_HAN_SHADOW")))font.dwStyle=16;
            pendingValue=false;at+=token.size();continue;
        }
        // Color/style flags remain set: once color appeared, later values
        // still take its branch. Attribute names themselves are case-sensitive.
        if(!color&&!comparePrefix(tag.c_str()+at,"color",5,false)){color=true;at+=5;}
        else if(!style&&!comparePrefix(tag.c_str()+at,"style",5,false)){style=true;at+=5;}
        else if(!comparePrefix(tag.c_str()+at,"=",1,false)){pendingValue=true;++at;}
        else ++at;
    }
    return true;
}

bool RF455_IsClosingFontTag(const char* value){
    if(!value)return false;const std::string tag(value);
    if(tag.size()<7||tag.front()!='<'||tag.back()!='>')return false;
    std::size_t at=1;while(at<tag.size()&&tag[at]==' ')++at;
    return at<tag.size()&&!comparePrefix(tag.c_str()+at,"/font",5,true);
}

CGUITextBoard::CGUITextBoard(){}
CGUITextBoard::~CGUITextBoard(){}
int CGUITextBoard::Stride() const{return RF455_DefaultTextHeight()+m_gap;}
int CGUITextBoard::VisibleLines() const{
    if(m_ptSize.y<=2*m_margin.y)return 0;
    const int stride=Stride();if(!stride)throw std::logic_error("TextBoard requires a live font");
    return (m_ptSize.y-2*m_margin.y)/stride;
}
void CGUITextBoard::SetViewed(WORD line){
    m_viewed=m_lines.empty()?0:static_cast<WORD>(std::min<std::size_t>(line,m_lines.size()-1));
}
void CGUITextBoard::SetMargin(int x,int y){m_margin.x=x;m_margin.y=y;SetSize(m_ptSize.x,m_ptSize.y);}
void CGUITextBoard::SetColumnGap(int gap){
    m_gap=static_cast<WORD>(gap);
    if(m_scrollbar)m_scrollbar->SetAdjustmentUnit(static_cast<WORD>(Stride()));
    SetSize(m_ptSize.x,m_ptSize.y);
}
void CGUITextBoard::AddScrollbar(CGUIScrollbar* scrollbar){
    m_scrollbar=scrollbar;
    if(scrollbar){scrollbar->SetAdjustmentUnit(static_cast<WORD>(Stride()));scrollbar->AddScrollHandler(this);}
}
void CGUITextBoard::SetBound(RECT& bound){
    SetPos(bound.left,bound.top);SetSize(bound.right-bound.left,bound.bottom-bound.top);
}
void CGUITextBoard::SetSize(LONG width,LONG height){
    const auto oldWidth=m_ptSize.x;CGUIObject::SetSize(width,height);
    if(oldWidth!=m_ptSize.x)Layout(false);
    if(!m_scrollbar){SetViewed(m_viewed);return;}
    const int visible=VisibleLines();
    if(GetTotalLineNum()<=visible)m_scrollbar->SetAmount(0,0);
    else {const LONG total=(GetTotalLineNum()-visible)*Stride();m_scrollbar->SetAmount(total,std::min(total,m_scrollbar->GetCurrentAmount()));}
    SetViewed(static_cast<WORD>(m_scrollbar->GetCurrentAmount()/Stride()));
}
void CGUITextBoard::Clear(){m_fragments.clear();m_fragmentBase=0;m_lines.clear();m_viewed=0;if(m_scrollbar)m_scrollbar->SetAmount(0,0);}
bool CGUITextBoard::GetLineStart455(WORD line,WORD& fragment,WORD& offset) const{
    if(line>=m_lines.size())return false;
    fragment=static_cast<WORD>(m_lines[line].fragment-m_fragmentBase);offset=m_lines[line].offset;return true;
}
bool CGUITextBoard::GetLineEnd455(WORD line,WORD& fragment,WORD& offset) const{
    if(line>=m_lines.size())return false;WORD nextFragment=0,nextOffset=0;
    if(GetLineStart455(static_cast<WORD>(line+1),nextFragment,nextOffset)){
        if(nextOffset){fragment=nextFragment;offset=static_cast<WORD>(nextOffset-1);}
        else {fragment=static_cast<WORD>(nextFragment-1);offset=static_cast<WORD>(m_fragments.at(fragment)->GetLength455()-1);}
    }else {fragment=static_cast<WORD>(m_fragments.size()-1);offset=static_cast<WORD>(m_fragments.at(fragment)->GetLength455()-1);}
    return true;
}
void CGUITextBoard::AddLine(WORD fragment,WORD offset){
    if(static_cast<unsigned>(m_fragmentBase)+fragment>=0xffff&&!m_lines.empty()){
        const WORD first=m_lines.front().fragment;
        for(auto& line:m_lines)line.fragment=static_cast<WORD>(line.fragment-first);
        m_fragmentBase=0;
    }
    m_lines.push_back({static_cast<WORD>(m_fragmentBase+fragment),offset});
}
void CGUITextBoard::Layout(bool append){
    unsigned first=0;int width=0;bool newline=false;
    if(append){
        if(!m_fragments.empty())first=static_cast<unsigned>(m_fragments.size()-1);
        if(!m_lines.empty()){
            WORD fragment=0,offset=0;GetLineStart455(static_cast<WORD>(m_lines.size()-1),fragment,offset);
            for(unsigned i=fragment;i<first;++i){
                auto& text=*m_fragments.at(i);const char* start=text.GetText()+offset;
                if(*start=='\n'){width+=RF455_TextWidth(start+1,static_cast<WORD>(text.GetLength455()-1));newline=true;}
                else width+=RF455_TextWidth(start);
                offset=0;
            }
        }
    }else {m_lines.clear();m_viewed=0;}
    const int available=m_ptSize.x-2*m_margin.x;if(available<=0)return;
    for(unsigned fragment=first;fragment<m_fragments.size();++fragment){
        auto& info=*m_fragments[fragment];const char* text=info.GetText();const int length=info.GetLength455();
        for(int start=0;start<length;){
            const char* end=findText(text+start,"\n");const int segment=end?static_cast<int>(end-(text+start)):length-start;
            int consumed=0;
            while(consumed<segment){
                if(width<available){
                    int count=RF455_TextFitBytes(text+start+consumed,available-width);
                    if(!count){if(!newline&&!width)break;newline=false;width=0;continue;}
                    if(!width&&!newline)AddLine(static_cast<WORD>(fragment),static_cast<WORD>(start+consumed));
                    count=std::min(count,segment-consumed);
                    width+=RF455_TextWidth(text+start+consumed,static_cast<WORD>(count));consumed+=count;
                }else if(width==available){if(!newline&&!width)break;newline=false;width=0;}
                else width=0;
            }
            start+=segment;
            if(end){AddLine(static_cast<WORD>(fragment),static_cast<WORD>(end-text));newline=true;width=0;++start;}
        }
    }
    while(m_lines.size()>m_limit){
        if(m_lines.size()<=1)break;
        const auto firstLine=m_lines[0],nextLine=m_lines[1];
        for(unsigned i=firstLine.fragment;i<nextLine.fragment;++i){
            if(m_fragments.empty())throw std::logic_error("TextBoard retention outside owned fragments");
            m_fragments.pop_front();++m_fragmentBase;
        }
        m_lines.pop_front();
    }
}
void CGUITextBoard::InsertText(char* text){FONT_INFO font;InsertFragment(text,&font,FALSE);}
void CGUITextBoard::InsertText(char* text,FONT_INFO* font){InsertFragment(text,font,FALSE);}
void CGUITextBoard::InsertText(CGUITextInfo* text,BOOL adjustView){if(text)InsertFragment(text->GetText(),text->GetFont(),adjustView);}
void CGUITextBoard::InsertFragment(char* text,FONT_INFO* font,BOOL adjustView){
    if(!text||!*text)return;
    if(!font)throw std::invalid_argument("TextBoard requires FONT_INFO");
    if(m_fragments.size()>=0xffff)throw std::length_error("TextBoard WORD fragment index domain exceeded");
    std::unique_ptr<CGUITextInfo> entry(new CGUITextInfo);entry->SetText(text);entry->SetFont(font);m_fragments.push_back(std::move(entry));Layout(true);
    if(!m_scrollbar){SetViewed(m_viewed);return;}
    const int visible=VisibleLines();
    if(GetTotalLineNum()>visible){
        m_scrollbar->SetTotalAmount((GetTotalLineNum()-visible)*Stride());
        if(m_autoScroll){ScrollToBottom455();return;}
        if(IsShow()&&adjustView==TRUE){if(GetTotalLineNum()!=m_limit){SetViewed(static_cast<WORD>(m_viewed+1));return;}SetViewed(m_viewed);}
    }
}
void CGUITextBoard::ScrollToBottom455(){
    if(!m_scrollbar)return;
    m_scrollbar->SetCurrentAmount(m_scrollbar->GetTotalAmount());SetViewed(static_cast<WORD>(m_scrollbar->GetCurrentAmount()/Stride()));
}
void CGUITextBoard::ScrollEvent(_scroll_event&){if(m_scrollbar)SetViewed(static_cast<WORD>(m_scrollbar->GetCurrentAmount()/Stride()));}
bool CGUITextBoard::ResizeToText455(){
    if(m_fragments.empty())return false;int maximum=0,lines=0,width=0;const char* lastNewline=nullptr;
    for(const auto& entry:m_fragments){
        const char* text=entry->GetText();const int length=entry->GetLength455();
        for(int start=0;start<length;){
            lastNewline=findText(text+start,"\n");
            if(!lastNewline){width+=RF455_TextWidth(text+start,static_cast<WORD>(length-start));break;}
            maximum=std::max(maximum,width+static_cast<int>(RF455_TextWidth(text+start,static_cast<WORD>(lastNewline-(text+start)))));width=0;++lines;
            start=static_cast<int>(lastNewline-text)+1;
        }
    }
    maximum=std::max(maximum,width);if(width||lastNewline)++lines;
    SetSize(maximum+2*m_margin.x,lines*Stride()+2*m_margin.y);return true;
}
void CGUITextBoard::InsertFormatted455(char* value,FONT_INFO* base){
    if(!value)return;if(!base)throw std::invalid_argument("Formatted TextBoard requires FONT_INFO");
    const std::string input(value);const int length=static_cast<int>(input.size());int search=0,start=0;
    while(search<length){
        const char* source=findText(input.c_str()+search,"<");int span=source?static_cast<int>(source-input.c_str())-start:length-start;
        if(!source)search+=span;FONT_INFO font=*base;
        if(source&&!span){
            const char* end=findText(source,">");
            if(!end){++search;continue;}
            span=static_cast<int>(end-source)+1;RF455_CopyGuiTextBytes8(scratch,source,span+1);search=static_cast<int>(end-input.c_str())+1;
            if(!RF455_ParseFontTag(scratch,font))continue;
            const int contentStart=search;source=findText(input.c_str()+search,"<");end=source?findText(source,">"):nullptr;
            if(end){
                RF455_CopyGuiTextBytes8(scratch,source,static_cast<unsigned>(end-source)+2);search=static_cast<int>(end-input.c_str())+1;
                if(RF455_IsClosingFontTag(scratch)){
                    RF455_CopyGuiTextBytes8(scratch,input.c_str()+contentStart,static_cast<unsigned>(source-input.c_str()-contentStart)+1);
                    InsertFragment(scratch,&font,FALSE);start=search;span=0;
                }else continue;
            }
        }
        if(span){RF455_CopyGuiTextBytes8(scratch,input.c_str()+start,span+1);InsertFragment(scratch,&font,FALSE);start+=span;}
    }
}
BOOL CGUITextBoard::DrawLine(WORD line,int x,int y,BYTE alpha){
    WORD lastFragment=0,lastOffset=0;
    if(!GetLineEnd455(line,lastFragment,lastOffset))return FALSE;
    return DrawLineTo455(line,x,y,lastFragment,lastOffset,alpha);
}
BOOL CGUITextBoard::DrawLineTo455(WORD line,int x,int y,WORD lastFragment,WORD lastOffset,BYTE alpha){
    WORD fragment=0,offset=0;
    if(!GetLineStart455(line,fragment,offset))return FALSE;
    const DWORD mask=0x00ffffff|(static_cast<DWORD>(alpha)<<24);int advance=0;
    if(m_highlight)Draw2DRectangle(x,y,x+m_ptSize.x,y+Stride(),m_highlightColor);
    while(fragment<=lastFragment){
        auto* info=GetFragment455(fragment);if(!info||!info->GetText())return FALSE;
        const char* text=info->GetText();const auto* font=info->GetFont();
        if(text[offset]=='\n')++offset;
        else if(fragment>=lastFragment){
            if(offset<=lastOffset){RF455_CopyGuiTextBytes8(scratch,text+offset,lastOffset-offset+2);DrawR3Hangul(x+advance,y,scratch,mask&font->dwColor,font->dwStyle);}
            return TRUE;
        }else {DrawR3Hangul(x+advance,y,const_cast<char*>(text+offset),mask&font->dwColor,font->dwStyle);advance+=RF455_TextWidth(text+offset);offset=info->GetLength455();}
        if(offset>=info->GetLength455()){++fragment;offset=0;}
    }
    return TRUE;
}
BOOL CGUITextBoard::Draw(){
    if(!IsShow())return FALSE;if(m_fragments.empty())return TRUE;
    int visible=VisibleLines();const int total=GetTotalLineNum();const int blank=m_autoScroll&&visible>total?visible-total:0;
    int y=m_ptPos.y+m_margin.y+Stride()*blank;const int x=m_ptPos.x+m_margin.x;
    if(visible+m_viewed>total)visible=total-m_viewed;
    for(int i=0;i<visible;++i){DrawLine(static_cast<WORD>(i+m_viewed),x,y,255);y+=Stride();}
    return TRUE;
}
BOOL CGUITextBoard::Draw(RECT&){return Draw();}
