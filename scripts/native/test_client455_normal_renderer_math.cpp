#include "client455_normal_renderer_math.h"
#include <cstdio>
#include <cstring>
#include <float.h>
#include <xmmintrin.h>
static float capturedAngle;static unsigned rotations,multiplies;static float position[3]={3,5,7};
static void* WINAPI rotate(void* out,float value){capturedAngle=value;++rotations;std::memset(out,0,64);auto* m=static_cast<float*>(out);m[0]=m[5]=m[10]=m[15]=1;return out;}
static void* WINAPI multiply(void* out,const void* left,const void* right){++multiplies;return out;}
static unsigned bits(float f){unsigned out;std::memcpy(&out,&f,4);return out;}
#define M_REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Normal renderer math line%d\n",__LINE__);return 1;}}while(0)
int main(int argc,char** argv){
    if(argc!=3)return 2;FILE* file=std::fopen(argv[1],"rb");M_REQUIRE(file);char magic[4];unsigned version,angles,boxes;
    M_REQUIRE(std::fread(magic,4,1,file)==1 && !std::memcmp(magic,"NW45",4) && std::fread(&version,4,1,file)==1 && version==1 && std::fread(&angles,4,1,file)==1 && std::fread(&boxes,4,1,file)==1);
    const unsigned saved=_control87(0,0),mxcsr=_mm_getcsr();auto control=[](unsigned p,unsigned mode){const unsigned rc[]={_RC_NEAR,_RC_DOWN,_RC_UP,_RC_CHOP};_clearfp();_control87(_MCW_EM|(p==24?_PC_24:p==53?_PC_53:_PC_64)|rc[mode],_MCW_EM|_MCW_PC|_MCW_RC);};
    RF455NormalTransformApi api={rotate,{nullptr,multiply}};
    for(unsigned i=0;i<angles;++i){unsigned p,mode;float angle,expected,world[16],unscaled[16];M_REQUIRE(std::fread(&p,4,1,file)==1 && std::fread(&mode,4,1,file)==1 && std::fread(&angle,4,1,file)==1 && std::fread(&expected,4,1,file)==1);control(p,mode);rotations=multiplies=0;
        RF455_BuildNormalCharacterWorld(world,unscaled,position,angle,2,&api);if(bits(capturedAngle)!=bits(expected))std::fprintf(stderr,"angle case%u PC%u RC%u actual%08x expected%08x\n",i,p,mode,bits(capturedAngle),bits(expected));M_REQUIRE(bits(capturedAngle)==bits(expected) && rotations==2 && multiplies==4);M_REQUIRE(world[0]==2 && unscaled[0]==1 && world[12]==3 && world[13]==7 && world[14]==5 && !std::memcmp(world+12,unscaled+12,12));}
    for(unsigned i=0;i<boxes;++i){unsigned p,mode,expected;float low[3],high[3],plane[6][4]={};M_REQUIRE(std::fread(&p,4,1,file)==1 && std::fread(&mode,4,1,file)==1 && std::fread(low,12,1,file)==1 && std::fread(high,12,1,file)==1 && std::fread(plane,16,1,file)==1 && std::fread(&expected,4,1,file)==1);control(p,mode);M_REQUIRE(RF455_IsNormalModelBoxVisible(low,high,plane)==static_cast<int>(expected));}
    _clearfp();_control87(saved,_MCW_EM|_MCW_PC|_MCW_RC);_mm_setcsr(mxcsr);M_REQUIRE(std::fgetc(file)==EOF);std::fclose(file);file=std::fopen(argv[2],"wb");M_REQUIRE(file);std::fprintf(file,"{\"status\":\"PASS\",\"angle_cases\":%u,\"box_cases\":%u,\"fp_modes\":12}\n",angles,boxes);std::fclose(file);return 0;
}
