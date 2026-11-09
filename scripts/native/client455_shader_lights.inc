//4558B11E0/8B2E40..8B3064,owned by the ordinary particle translation unit.
#include "client455_shader_lights.h"
#include <cstdlib>
#include <cstring>
namespace {
struct ShaderLights455 {
    int count=0;
    RF455ShaderLight* entries[101]={}; //The constructor clears the final101st slot too.
    ~ShaderLights455(){RF455_ClearShaderLights();}
} shaderLights455;
float shaderLightProduct455(float a,float b){float value;__asm{fld a
    fmul b
    fstp value}return value;}
}
int RF455_GetShaderLightCount(){return shaderLights455.count;}
RF455ShaderLight* RF455_GetShaderLight(int index){return index<0?nullptr:shaderLights455.entries[index];}
int RF455_AppendShaderLight(RF455ShaderLight* light){
    if(shaderLights455.count<=100){shaderLights455.entries[shaderLights455.count++]=light;return shaderLights455.count-1;}
    Warning("Shader light table is full","");--shaderLights455.count;return -1; //Preserve original overflow counter behavior.
}
void RF455_ClearShaderLights(){
    for(int i=0;i<shaderLights455.count;++i)if(shaderLights455.entries[i])std::free(shaderLights455.entries[i]);
    shaderLights455.count=0; //Reference leaves the old pointer slots intact.
}
RF455ShaderLight* RF455_ReadShaderLight(FILE* f){
    auto* light=new RF455ShaderLight;char token[256];std::fscanf(f,"%s",token);_strlwr(token);
    while(std::strcmp(token,"[endlight]")){
        if(!std::strcmp(token,"lightcolor"))std::fscanf(f,"%f%f%f",light->color,light->color+1,light->color+2);
        if(!std::strcmp(token,"power")||!std::strcmp(token,"radius"))std::fscanf(f,"%f",&light->radius); //Both target tokens write+4.
        std::fscanf(f,"%s",token);_strlwr(token);
    }
    return light;
}
void RF455_UpdateParticleShaderLight(int index,const float* position){
    auto* source=RF455_GetShaderLight(index);if(!source)return;auto* first=RF455_GetShaderLight(0);
    for(unsigned i=0;i<3;++i)first->color[i]=shaderLightProduct455(source->color[i],first->scale);
    std::memcpy(first->position,position,12); //8E6950 always updates destination slot0.
}
