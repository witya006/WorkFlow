#include "r3d3dwrapper.h"
#include "core.h"
#include "r3enginekernel.h"
#include "Character455.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstddef>

namespace {const char* outputPath=nullptr;HRESULT requested=S_OK;}
class CreationCase:public R3D3dWrapper {
public:
    HRESULT Create(HINSTANCE) override {
        FILE* out=std::fopen(outputPath,"ab");if(!out)std::exit(90);
        std::fprintf(out,"create:%lu:%lu:%ld\n",m_dwCreationWidth,m_dwCreationHeight,m_bIsFullScreen);std::fclose(out);return requested;
    }
    void seed(){mR3Flag=0xabcdef01;}
    DWORD flag()const{return mR3Flag;}
    static void layout(){std::printf("{\"ready\":%zu,\"windowed\":%zu,\"window\":%zu,\"device\":%zu,\"state_fullscreen\":%zu,\"state_renderbits\":%zu,\"character_device\":%zu}\n",offsetof(CreationCase,m_bReady),offsetof(CreationCase,m_bWindowed),offsetof(CreationCase,m_hWnd),offsetof(CreationCase,m_pd3dDevice),offsetof(_R3ENGINE_STATE,mbFullScreen),offsetof(_R3ENGINE_STATE,mRenderBits),offsetof(CRender,native)+offsetof(RF455CharacterRenderer,device));}
};
void completed(){FILE* file=std::fopen(outputPath,"ab");if(file){std::fputs("atexit\n",file);std::fclose(file);}}
int main(int argc,char** argv){
    if(argc==2&&!std::strcmp(argv[1],"layout")){CreationCase::layout();return 0;}
    if(argc!=3)return 2;outputPath=argv[2];requested=static_cast<HRESULT>(std::strtoul(argv[1],nullptr,16));std::atexit(completed);
    auto* state=GetR3State();for(BOOL full:{FALSE,TRUE}){state->mbFullScreen=full;state->mRenderBits=16;ForceFullScreen();if(state->mRenderBits!=32||state->mbFullScreen!=full)return 3;}
    state->mbFullScreen=FALSE;state->mbStartCamera=FALSE;state->mScreenXsize=640;state->mScreenYsize=480;state->mZbufferBits=24;
    CreationCase* instance=new CreationCase;instance->seed();const auto result=instance->InitR3D3D(nullptr,0);
    FILE* out=std::fopen(outputPath,"ab");if(!out)return 4;std::fprintf(out,"after:%ld:%lu\n",result,instance->flag());std::fclose(out);delete instance;return requested!=S_OK?5:0;
}
