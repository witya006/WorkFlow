//4558B11E0/8B2E40..8B3064,owned by the ordinary particle translation unit.
#include "client455_shader_lights.h"
#include <cstdlib>
#include <cstring>
#include <new>
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
RF455ShaderLight* RF455_GetShaderLight(int index) {
    if (index < 0 || index >= shaderLights455.count) return nullptr;
    return shaderLights455.entries[index];
}
int RF455_AppendShaderLight(RF455ShaderLight* light) {
    if (!light) return -1;
    if (shaderLights455.count == 101) {
        Warning("Shader light table is full", "");
        return -1;
    }
    const int index = shaderLights455.count++;
    shaderLights455.entries[index] = light;
    return index;
}
void RF455_ClearShaderLights() {
    for (int i = 0; i < shaderLights455.count; ++i) {
        delete shaderLights455.entries[i];
        shaderLights455.entries[i] = nullptr;
    }
    shaderLights455.count = 0;
}
namespace {
template<class Input>
RF455ShaderLight* readShaderLight455(Input& input) {
    RF455ShaderLight light;
    char token[256];
    while (particleToken455(input, token)) {
        _strlwr(token);
        if (std::strcmp(token,"[endlight]") == 0) return new (std::nothrow) RF455ShaderLight(light);
        if (std::strcmp(token,"lightcolor") == 0) {
            for (auto& channel : light.color)
                if (!particleFloat455(input, token, channel)) return nullptr;
        } else if ((std::strcmp(token,"power") == 0 || std::strcmp(token,"radius") == 0) &&
                   !particleFloat455(input, token, light.radius)) return nullptr;
    }
    return nullptr;
}
}
RF455ShaderLight* RF455_ReadShaderLight(FILE* file) { return readShaderLight455(file); }
RF455ShaderLight* RF455_ReadShaderLight(RF455ResourceText& input) { return readShaderLight455(input); }

void RF455_UpdateParticleShaderLight(int index,const float* position){
    auto* source=RF455_GetShaderLight(index);if(!source || !position)return;auto* first=RF455_GetShaderLight(0);
    for(unsigned i=0;i<3;++i)first->color[i]=shaderLightProduct455(source->color[i],first->scale);
    std::memcpy(first->position,position,12); //8E6950 always updates destination slot0.
}
