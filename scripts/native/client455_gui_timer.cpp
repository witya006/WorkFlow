#include "client455_gui_timer.h"
#include "client455_gui_input.h"

namespace {
const double fullCircle=360.0,pi=3.1415927410125732421875,straight=180.0;
float phase(DWORD elapsed,DWORD duration){
    const std::uint64_t e=elapsed,d=duration;float result;
    __asm {
        fild qword ptr[e]
        fild qword ptr[d]
        fdivp st(1),st(0)
        fmul qword ptr[fullCircle]
        fstp dword ptr[result]
    }
    return result;
}
float tangent(float angle,double cardinal,bool reverse){
    const double distance=reverse?cardinal-double(angle):double(angle)-cardinal;float radians,result;WORD previous;const WORD defaults=0x027f;
    // Finite default CRT path87BE3D. CPU-selected SSE/exception paths remain open.
    __asm {
        fld qword ptr[distance]
        fmul qword ptr[pi]
        fdiv qword ptr[straight]
        fstp dword ptr[radians]
        fnstcw word ptr[previous]
        fldcw word ptr[defaults]
        fld dword ptr[radians]
        fptan
        fstp st(0)
        fldcw word ptr[previous]
        fstp dword ptr[result]
    }
    return result;
}
float coordinate(float tangent,LONG dimension,double origin,bool complement){
    const double extent=double(dimension)*0.5;float result;
    if(complement){__asm {
        fld1
        fsub dword ptr[tangent]
        fmul qword ptr[extent]
        fadd qword ptr[origin]
        fstp dword ptr[result]
    }}else {__asm {
        fld dword ptr[tangent]
        fmul qword ptr[extent]
        fadd qword ptr[origin]
        fstp dword ptr[result]
    }}
    return result;
}
LONG add(LONG a,LONG b){return static_cast<LONG>(DWORD(a)+DWORD(b));}
void submit(void*,const _D3DR3TLVERTEX_TEX1* vertices){Draw2DSprite(const_cast<_D3DR3TLVERTEX_TEX1*>(vertices),1,nullptr);}
}
RF455GuiTimer::RF455GuiTimer(){
    Reset455();SetMouseInput455(FALSE);
    //Ctor leaves x/y untouched,as629730. Every submitted triangle writes them.
    for(auto& v:vertices){v.color=0xa0040204;v.z=1;v.w=1;v.u=0;v.v=0;}
}
void RF455GuiTimer::Reset455(){state.duration=state.startedAt=state.elapsedOffset=state.started=0;state.remaining=0;state.angle=0;}
void RF455GuiTimer::Start455(LONG elapsed){state.startedAt=RF455_GuiInputTime();state.elapsedOffset=elapsed==-1?0:static_cast<DWORD>(elapsed);state.started=1;}
void RF455GuiTimer::Update(){
    if(!state.started)return;
    const DWORD elapsed=state.elapsedOffset+RF455_GuiInputTime()-state.startedAt;
    const LONG remaining=static_cast<LONG>(state.duration-elapsed);state.remaining=remaining>0?remaining:0;
    if(elapsed<state.duration)state.angle=phase(elapsed,state.duration);else state.started=0;
}
BOOL RF455GuiTimer::Draw(){return DrawWithSink455(submit,nullptr);}
BOOL RF455GuiTimer::Draw(RECT& clip){return DrawWithSink455(submit,nullptr,&clip);}
BOOL RF455GuiTimer::DrawWithSink455(RF455TimerTriangleSink sink,void* context,const RECT* clip){
    const LONG x=GetPosX(),y=GetPosY(),width=GetSizeX(),height=GetSizeY();
    if(clip&&(x<clip->left||add(x,width)>clip->right||y<clip->top||add(y,height)>clip->bottom))return FALSE;
    if(!IsShow()||!state.started)return FALSE;
    vertices[2].x=static_cast<float>(double(x)+double(width)*0.5);vertices[2].y=static_cast<float>(double(y)+double(height)*0.5);
    const float a=state.angle;
    if(a<45){vertices[0].x=coordinate(tangent(a,0,false),height,vertices[2].x,false);vertices[0].y=static_cast<float>(y);
        vertices[1].x=static_cast<float>(add(x,width));vertices[1].y=static_cast<float>(y);sink(context,vertices);}
    if(a<135){vertices[0].x=static_cast<float>(add(x,width));
        vertices[0].y=a<45?static_cast<float>(y):a<90?coordinate(tangent(a,90,true),width,y,true):coordinate(tangent(a,90,false),width,vertices[2].y,false);
        vertices[1].x=static_cast<float>(add(x,width));vertices[1].y=static_cast<float>(add(y,height));sink(context,vertices);}
    if(a<225){vertices[0].x=a<135?static_cast<float>(add(x,width)):a<180?coordinate(tangent(a,180,true),height,vertices[2].x,false):coordinate(tangent(a,180,false),height,x,true);
        vertices[0].y=static_cast<float>(add(y,height));vertices[1].x=static_cast<float>(x);vertices[1].y=static_cast<float>(add(y,height));sink(context,vertices);}
    if(a<315){vertices[0].x=static_cast<float>(x);
        vertices[0].y=a<225?static_cast<float>(add(y,height)):a<270?coordinate(tangent(a,270,true),width,vertices[2].y,false):coordinate(tangent(a,270,false),width,y,true);
        vertices[1].x=static_cast<float>(x);vertices[1].y=static_cast<float>(y);sink(context,vertices);}
    if(a<360){vertices[0].x=a<315?static_cast<float>(x):coordinate(tangent(a,360,true),height,x,true);vertices[0].y=static_cast<float>(y);
        vertices[1].x=vertices[2].x;vertices[1].y=static_cast<float>(y);sink(context,vertices);}
    return TRUE;
}
DWORD RF455_TimerLabel455(DWORD milliseconds,BYTE context,RF455TimerLabel& output){
    DWORD result=milliseconds;int x=0,y=0;float scale=0;const bool common=context==0||context==1||context==5,large=context==2||context==3;
    if(milliseconds>3600000){result=milliseconds/1000/3600;output.unit=2;output.color=0xffffffff;
        if(common){x=-27;y=24;scale=0.6f;}else if(large){x=-32;y=27;scale=0.8f;}else if(context==4){x=-33;y=24;scale=0.7f;}else return result;
    }else if(milliseconds>60000&&milliseconds<3600000){const DWORD seconds=milliseconds/1000;result=seconds/60;output.unit=1;output.color=0xffffffff;const bool wide=seconds>600;
        if(common){x=wide?-30:-27;y=24;scale=0.6f;}else if(large){x=wide?-37:-32;y=27;scale=0.8f;}else if(context==4){x=wide?-30:-27;y=24;scale=0.7f;}else return result;
    }else if(milliseconds&&milliseconds<60000){result=milliseconds/1000+1;if(milliseconds<1000)result=1;output.unit=0;const bool digit=result<10;output.color=digit?0xffff0000:0xffffff00;
        if(common){x=digit?-22:-25;y=24;scale=0.6f;}else if(large){x=digit?-27:-30;y=27;scale=0.8f;}else if(context==4){x=digit?-24:-31;y=24;scale=0.7f;}else return result;
    }else{output.unit=3;return result;}
    output.offset={x,y};output.scale=scale;return result;
}
