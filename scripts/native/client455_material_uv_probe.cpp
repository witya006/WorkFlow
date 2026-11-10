#define RF455_LIGHTING_CONSUMERS_NO_MAIN
#include "client455_lighting_consumers_probe.cpp"
#include "multilayer.h"

int main(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    InitR3Engine();FILE* file=std::fopen("result.json","wb");if(!file)return 3;
    const float previousTime=GetMultiLayerTime();SetMultiLayerTime(4.0f);bool passed=true;
    std::fputs("{\"layers\":[",file);
    for(unsigned layer=0;layer<7;++layer){
        _R3MATERIAL material={};material.m_Layer[layer].m_dwFlag=_UV_SCROLL_U;
        material.m_Layer[layer].m_sUVScrollU=256;D3DXMATRIX uv;
        const bool changed=GetTextureMatrix(&material,layer,&uv)!=0;
        const bool okay=changed&&uv._31==1.0f&&uv._32==0.0f&&uv._41==0.0f&&uv._42==0.0f;
        passed=passed&&okay;std::fprintf(file,"%s{\"layer\":%u,\"changed\":%s,\"u\":%.9g,\"v\":%.9g,\"pass\":%s}",layer?",":"",layer,changed?"true":"false",uv._31,uv._32,okay?"true":"false");
    }
    SetMultiLayerTime(previousTime);ReleaseR3Engine();std::fprintf(file,"],\"status\":\"%s\",\"material_bytes\":%u,\"layer_bytes\":%u}\n",passed?"PASS":"FAIL",unsigned(sizeof(_R3MATERIAL)),unsigned(sizeof(_ONE_LAYER)));std::fclose(file);return passed?0:2;
}
