#include "client455_center_messages.h"
#include "client455_font.h"
#include "r3enginekernel.h"
#include "r3d3d8.h"
#include "commonutil.h"
#include <mmsystem.h>
#include <mbstring.h>
#include <cstring>
#include <stdexcept>

namespace {
RF455CenterMessages* owner=nullptr;
constexpr DWORD flags=0x80000010;
void copyChunk(char* dest,const char* source){
    std::memset(dest,0,60);
    if(!_mbsnbcpy(reinterpret_cast<unsigned char*>(dest),reinterpret_cast<const unsigned char*>(source),59))
        throw std::logic_error("455 center messages invalid CRT multibyte copy domain");
}
SIZE measure(const char* text){
    if(!RF455_TextResourcesReady())throw std::logic_error("455 center messages require actual text resources");
    return RF455_MeasureTextAnsiFlags(text,flags);
}
float screenWidth(){return static_cast<float>(GetR3State()->mScreenXsize);}
}
RF455CenterMessages* RF455_GetCenterMessages(){return owner;}
RF455CenterMessages::RF455CenterMessages(){owner=this;}
RF455CenterMessages::~RF455CenterMessages(){Clear();owner=nullptr;}
void RF455CenterMessages::Clear(){pending.clear();active.clear();}
void RF455CenterMessages::appendActive(const char* text,DWORD color){
    RF455CenterLine line;copyChunk(line.text,text);line.color=color;line.time=timeGetTime();
    const auto size=measure(line.text);line.y=static_cast<float>(size.cy+200);
    line.x=static_cast<float>((static_cast<double>(screenWidth())-size.cx)/2.0);
    active.push_back(line);if(active.size()>3)active.pop_front();
}
void RF455CenterMessages::Add(const char* text,DWORD color){
    if(!text)throw std::logic_error("455 center messages null string domain remains open");
    auto remaining=std::strlen(text);
    if(pending.empty()&&remaining<=59){appendActive(text,color);return;}
    while(remaining){
        RF455CenterChunk chunk;copyChunk(chunk.text,text);chunk.color=color;
        const auto used=std::strlen(chunk.text);
        if(!used)throw std::logic_error("455 center messages zero-progress malformed multibyte input");
        pending.push_back(chunk);remaining-=used;text+=used;
    }
}
void RF455CenterMessages::FrameMove(){FrameMoveAt(timeGetTime(),R3GetLoopTime());}
void RF455CenterMessages::FrameMoveAt(DWORD now,float loopTime){
    const float factor=static_cast<float>(static_cast<double>(loopTime)*4.5);
    if(!pending.empty()&&(active.empty()||now-active.back().time>500||pending.size()>5)){
        appendActive(pending.front().text,pending.front().color);pending.pop_front();
    }
    unsigned index=0;
    for(auto it=active.rbegin();it!=active.rend();++it,++index){
        auto& line=*it;const auto size=measure(line.text);
        const float scale=index?.8f:1.0f;
        const float y=static_cast<float>(200.0-static_cast<double>(index)*size.cy);
        const float x=static_cast<float>((screenWidth()-static_cast<double>(size.cx)*scale)*.5);
        line.scale=static_cast<float>((static_cast<double>(scale)-line.scale)*factor+line.scale);
        line.y=static_cast<float>((static_cast<double>(y)-line.y)*factor+line.y);
        line.x=static_cast<float>((static_cast<double>(x)-line.x)*factor+line.x);
        const float alpha=now-line.time>=3600?0.0f:static_cast<float>(1.0-static_cast<double>(index)/3.0);
        line.alpha=static_cast<float>((static_cast<double>(alpha)-line.alpha)*factor+line.alpha);
        const DWORD alphaByte=static_cast<DWORD>(static_cast<int>(static_cast<double>(line.alpha)*255.0));
        line.color=(line.color&0xffffff)|(alphaByte<<24);
    }
    if(!active.empty()&&now-active.front().time>3600&&active.front().alpha<=.01f)active.pop_front();
}
void RF455CenterMessages::Draw()const{
    auto* device=GetD3dDevice();
    for(const auto& line:active){
        device->SetRenderState(D3DRS_ZENABLE,FALSE);
        float position[4]={static_cast<float>(static_cast<int>(line.x)),static_cast<float>(static_cast<int>(line.y)),.99f,1};
        const auto result=RF455_DrawTextAnsiScaled(position,line.text,line.color,flags,line.scale);
        device->SetRenderState(D3DRS_ZENABLE,TRUE);
        if(FAILED(result))throw std::runtime_error("455 center message actual font draw failed");
    }
}
