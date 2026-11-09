#define RF455_LIGHTING_CONSUMERS_NO_MAIN
#include "client455_lighting_consumers_probe.cpp"
static_assert(_MAX_LAYER_NUM==7&&_MAX_MATERIALS==2048&&sizeof(_ONE_LAYER)==54&&sizeof(_R3MATERIAL)==526,"455 material capacities");
static void write133(FILE* f,const void* p,unsigned n){check(std::fwrite(p,1,n,f)==n,"fixture133 write");}
static void u32133(FILE* f,DWORD value){write133(f,&value,4);}
static void f32133(FILE* f,float value){write133(f,&value,4);}
static void dump133(const char* name,const _R3MATERIAL* records){FILE* f=std::fopen(name,"wb");check(f!=nullptr,"dump133");write133(f,records,1052);std::fclose(f);}
static int run133(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);
    FILE* file=std::fopen("seven.r3m","wb");check(file!=nullptr,"binary fixture133");f32133(file,1.1f);u32133(file,2);
    for(unsigned index=0;index<2;++index){u32133(file,index?0:7);u32133(file,index?0x20:0x10);u32133(file,index?3:0xffffffffu);f32133(file,index?2.f:1.5f);char name[128]={};std::strcpy(name,index?"sentinel":"seven");write133(file,name,128);
        if(!index)for(unsigned layer=0;layer<7;++layer){BYTE wire[46]={};const short tile=short(layer+1);const LONG surface=20+layer;const DWORD alpha=layer,argb=0x80402010+layer,flag=0x10;
            std::memcpy(wire,&tile,2);std::memcpy(wire+2,&surface,4);std::memcpy(wire+6,&alpha,4);std::memcpy(wire+10,&argb,4);std::memcpy(wire+14,&flag,4);
            for(unsigned field=0;field<14;++field){const short value=short(layer*32+field);std::memcpy(wire+18+field*2,&value,2);}write133(file,wire,46);}
    }std::fclose(file);char binaryName[]="seven.r3m";const int base=GetNowR3D3DTexCnt()-1;auto* binary=LoadSubR3M(binaryName);check(binary&&binary->m_iMatNum==2,"actual binary seven layers133");dump133("binary-materials.bin",binary);Dfree(binary);
    check(CreateDirectoryA("text",nullptr)!=0||GetLastError()==ERROR_ALREADY_EXISTS,"text fixture directory133");file=std::fopen("text/MainMaterial.mst","wb");check(file!=nullptr,"main text133");std::fputs("*MATERIAL_NUM 2 { seven 0 sentinel 1 } end\n",file);std::fclose(file);
    file=std::fopen("text/seven.mst","wb");check(file!=nullptr,"seven text133");std::fputs("layer_num 7\nsky_sun_light\nsky_night\nsky_day\nsky_rotate_y\ntexture_splatting\nshader_object 3\nlight_object 5\n",file);
    for(unsigned layer=0;layer<7;++layer)std::fprintf(file,"layer %u {\nspecular_flikering_scale %.3f\nspecular_flikering_speed %.3f\n}\n",layer,double(layer+1)*.125,1.5+double(layer)*.25);
    std::fputs("end\n",file);std::fclose(file);file=std::fopen("text/sentinel.mst","wb");check(file!=nullptr,"text sentinel133");std::fputs("layer_num 0\nend\n",file);std::fclose(file);
    char textPath[]=".\\text\\";auto* text=LoadSubMaterial(textPath);check(text&&text->m_iMatNum==2,"actual text seven layers133");dump133("text-materials.bin",text);Dfree(text);
    file=std::fopen("bad-version.r3m","wb");check(file!=nullptr,"bad fixture133");f32133(file,1.2f);u32133(file,2);std::fclose(file);DWORD handlesBefore=0,handlesAfter=0;check(GetProcessHandleCount(GetCurrentProcess(),&handlesBefore)!=0,"handles before133");
    for(unsigned i=0;i<3;++i){char name[]="bad-version.r3m";check(LoadSubR3M(name)==nullptr,"actual rejected version133");}check(GetProcessHandleCount(GetCurrentProcess(),&handlesAfter)!=0&&handlesAfter==handlesBefore,"bad versions close actual file handles133");
    ReleaseR3Engine();file=std::fopen("result.json","wb");check(file!=nullptr,"result133");std::fprintf(file,"{\"status\":\"PASS\",\"binary_materials\":2,\"text_materials\":2,\"layers\":7,\"base\":%d,\"bad_versions\":3,\"handles_before\":%u,\"handles_after\":%u,\"warnings\":%u,\"full_material_shader\":false}\n",base,handlesBefore,handlesAfter,warnings);std::fclose(file);return 0;
}
int main(){try{return run133();}catch(const std::exception& e){std::fprintf(stderr,"material133:%s\n",e.what());return 1;}}
