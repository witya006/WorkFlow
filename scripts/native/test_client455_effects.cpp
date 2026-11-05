#include "Character.h"
#include <cstdio>
#include <cstring>
#include <vector>
#include <string>

#define F_REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"EFF failure line%d\n",__LINE__);return 1;}}while(0)
template<class T>static T get(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>static void put(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
static bool write(const char* path,const void* bytes,std::size_t size){FILE* f=std::fopen(path,"wb");if(!f)return false;const bool ok=std::fwrite(bytes,1,size,f)==size;std::fclose(f);return ok;}
static bool read(const char* path,std::vector<unsigned char>& bytes){FILE* f=std::fopen(path,"rb");if(!f)return false;std::fseek(f,0,SEEK_END);const long size=std::ftell(f);std::rewind(f);bytes.resize(size);const bool ok=std::fread(bytes.data(),1,size,f)==size;std::fclose(f);return ok;}
static std::vector<unsigned char> record(const char* mesh,unsigned id){
    std::vector<unsigned char> out(176);put<unsigned short>(out.data(),0,176);out[2]=2;std::strncpy(reinterpret_cast<char*>(out.data()+152),mesh,19);
    out[63]=1;out[64]=2;out[65]=3;out[66]=4;put<unsigned>(out.data(),67,0x11223344);put<float>(out.data(),71,.5f);put<float>(out.data(),75,.125f);
    for(unsigned i=79;i<84;++i)out[i]=static_cast<unsigned char>(i-77);
    for(unsigned i=0;i<4;++i){put<float>(out.data(),84+16*i,1.25f+i);put<float>(out.data(),88+16*i,-2.5f-i);put<float>(out.data(),92+16*i,3.75f+i);put<unsigned>(out.data(),96+16*i,id+i);}
    put<float>(out.data(),148,2.5f);put<unsigned>(out.data(),172,0x12345678);return out;
}
static int synthetic(){
    auto raw=record("part",17);RF455EffectStore store;auto report=RF455_ImportEffects(&store,"a.eff",raw.data(),raw.size());F_REQUIRE(report.status==RF_EFFECT_OK && report.records==1);
    auto* effect=RF455_FindEffect(&store,"a.eff","PART");F_REQUIRE(effect && !RF455_FindEffect(&store,"A.EFF","PART") && effect->mesh=="PART" && effect->file=="a.eff");
    F_REQUIRE(get<unsigned>(effect->draw.data(),156)==1 && get<unsigned>(effect->draw.data(),160)==2 && get<unsigned>(effect->draw.data(),172)==0x11223344 && get<float>(effect->draw.data(),176)==.5f && get<float>(effect->draw.data(),180)==.125f);
    F_REQUIRE(!std::memcmp(effect->draw.data()+208,raw.data()+84,64) && get<float>(effect->draw.data(),288)==2.5f && get<unsigned>(effect->draw.data(),192)==0x12345678);
    auto shortRecord=raw;shortRecord.resize(172);put<unsigned short>(shortRecord.data(),0,172);report=RF455_ImportEffects(&store,"short.eff",shortRecord.data(),shortRecord.size());F_REQUIRE(report.status==RF_EFFECT_OK && !get<unsigned>(RF455_FindEffect(&store,"short.eff","PART")->draw.data(),192));
    // strlen can terminate in a neighbouring field,as in real shipped records.
    auto boundary=record("",1);std::memset(boundary.data()+152,'x',20);put<unsigned>(boundary.data(),172,1);report=RF455_ImportEffects(&store,"cross.eff",boundary.data(),boundary.size());F_REQUIRE(report.status==RF_EFFECT_OK && store.files["cross.eff"].begin()->first.size()==21);
    auto bad=raw;put<unsigned short>(bad.data(),0,0);F_REQUIRE(RF455_ImportEffects(&store,"bad.eff",bad.data(),bad.size()).status==RF_EFFECT_FORMAT);
    put<unsigned short>(bad.data(),0,177);F_REQUIRE(RF455_ImportEffects(&store,"bad.eff",bad.data(),bad.size()).status==RF_EFFECT_FORMAT);
    bad.assign(176,0xff);put<unsigned short>(bad.data(),0,176);F_REQUIRE(RF455_ImportEffects(&store,"bad.eff",bad.data(),bad.size()).status==RF_EFFECT_NAME);
    bad=raw;bad.push_back(0);report=RF455_ImportEffects(&store,"partial.eff",bad.data(),bad.size());F_REQUIRE(report.status==RF_EFFECT_FORMAT && report.records==1 && RF455_FindEffect(&store,"partial.eff","PART"));
    auto generic=record("",33);std::vector<unsigned char> combined=generic;combined.insert(combined.end(),raw.begin(),raw.end());auto replacement=record("",44);combined.insert(combined.end(),replacement.begin(),replacement.end());report=RF455_ImportEffects(&store,"ordered.eff",combined.data(),combined.size());F_REQUIRE(report.records==3 && report.replaced==1 && store.files["ordered.eff"].size()==2);
    RF455MeshStorage meshes[2];RF455MeshAccounting accounting={};for(auto& mesh:meshes)RF455_ConstructMeshStorage(&mesh,&accounting);std::strcpy(meshes[0].m_Name,"part");std::strcpy(meshes[1].m_Name,"other");
    CHARACTEROBJECT model;RF455_ConstructCharacter(&model);model.m_MaxObj=2;model.m_pMesh=meshes;RF455CharacterRenderer owner={};
    F_REQUIRE(!model.IsHaveEffect() && !meshes[0].particleSlots());F_REQUIRE(RF455_ApplyEffectFile(&store,&owner,&model,"ordered.eff",36)==0);
    F_REQUIRE(meshes[0].particleSlots()[0].m_ID==17 && meshes[1].particleSlots()[0].m_ID==44 && meshes[0].entitySlot().m_ID==20 && model.IsHaveEffect());
    const auto before=meshes[0].particleSlots();report=RF455_ImportEffects(&store,"ordered.eff",generic.data(),generic.size());F_REQUIRE(report.replaced==1 && RF455_FindEffect(&store,"ordered.eff","PART") && meshes[0].particleSlots()==before);
    // Cached pointer branch leaves IDs alone; failed/attempted texture stays0.
    auto* cached=RF455_FindEffect(&store,"a.eff","PART");put<unsigned>(cached->draw.data(),120,0x12345678);put<unsigned>(meshes[0].bytes,5123,99);RF455_ApplyEffect(&owner,meshes,cached,8);F_REQUIRE(get<unsigned>(meshes[0].bytes,5115)==0x12345678 && get<unsigned>(meshes[0].bytes,5123)==99);
    cached->texture[0]="missing.dds";put<void*>(cached->draw.data(),120,nullptr);put<unsigned>(cached->draw.data(),56,1);RF455_ApplyEffect(&owner,meshes,cached,36);F_REQUIRE(get<unsigned>(meshes[0].bytes,5115)==0x12345678 && get<unsigned>(meshes[0].bytes,5123)==99); // Attempted miss is not retried.
    meshes[0].InitEffect();RF455_ApplyInlineEffect(&owner,meshes,36);F_REQUIRE(get<void*>(meshes[0].bytes,5455)==meshes[0].bytes+5163 && !meshes[0].IsHaveEffect() && meshes[0].m_Alpha==1 && !get<unsigned>(meshes[0].bytes,5115) && get<unsigned>(meshes[0].bytes,5123)==0xffffffffu);
    // File list duplicate/skip/missing modes use real IO and actual facade globals.
    F_REQUIRE(write("first.eff",raw.data(),raw.size()) && write("second.eff",generic.data(),generic.size()));
    const char mon[]=";comment\n1 first.eff\n1 second.eff\n1 missing.eff\n2 missing.eff\n";F_REQUIRE(write("mon.ini",mon,sizeof(mon)-1));RF455EffectFiles lists;report=RF455_LoadEffectFileTable(&lists,&store,"mon.ini",false);F_REQUIRE(report.status==RF_EFFECT_OK && report.records==1 && report.ignored==1 && report.missing==2 && lists.entries[1].file=="first.eff");
    const char item[]="3 first.eff 1\n3 second.eff 0\n4 missing.eff 1\n";F_REQUIRE(write("files.txt",item,sizeof(item)-1));report=RF455_LoadEffectFileTable(&lists,&store,"files.txt",true);F_REQUIRE(report.records==2 && report.ignored==1 && report.missing==1 && lists.entries[3].mode==1 && lists.entries.count(4));
    char monPath[]="mon.ini",filePath[]="files.txt",effPath[]="first.eff";g_EFFMonList.LoadEffectFileList(monPath);g_EffectFileList.LoadEffectFileList(filePath);EffectObjectManager::LoadEffect(effPath);F_REQUIRE(g_EFFMonList.native.entries.count(1) && g_EffectFileList.native.entries[3].mode==1);g_EFFMonList.SetEffect(nullptr,1);F_REQUIRE(!EffectObjectManager::SetPartEffect(nullptr,effPath,36));
    const auto memory=RF455_CrtMeshMemoryOps();for(auto& mesh:meshes)RF455_DestroyMeshStorage(&mesh,&memory);return 0;
}
static int math(const char* path,unsigned* cases){
    FILE* file=std::fopen(path,"rb");F_REQUIRE(file);unsigned header[2];F_REQUIRE(std::fread(header,4,2,file)==2 && !std::memcmp(header,"EFM1",4));unsigned short saved;__asm fnstcw saved
    for(unsigned i=0;i<header[1];++i){struct Case{unsigned precision,mode;int grade;float intensity;unsigned expected;} row;F_REQUIRE(std::fread(&row,1,sizeof(row),file)==sizeof(row));unsigned short control=static_cast<unsigned short>((saved&~0xf00)|((row.precision==24?0:row.precision==53?2:3)<<8)|(row.mode<<10));__asm fldcw control
        const unsigned actual=RF455_EffectFactor(&row.intensity,row.grade);unsigned short after;__asm fnstcw after
        F_REQUIRE(actual==row.expected && after==control);}
    __asm fldcw saved
    std::fclose(file);*cases=header[1];return 0;
}
int main(int argc,char** argv){
    if(argc!=4)return 2;unsigned cases=0;F_REQUIRE(math(argv[2],&cases)==0 && synthetic()==0);FILE* manifest=std::fopen(argv[1],"rb");F_REQUIRE(manifest);unsigned files=0,records=0;char path[1024];
    while(std::fgets(path,sizeof(path),manifest)){path[std::strcspn(path,"\r\n")]=0;std::vector<unsigned char> raw;F_REQUIRE(read(path,raw));std::vector<RF455EffectRecord> parsed;const auto report=RF455_ParseEffects(path,raw.data(),raw.size(),&parsed);F_REQUIRE(report.status==RF_EFFECT_OK);std::vector<unsigned char> roundtrip;for(const auto& r:parsed){const unsigned size=get<unsigned short>(r.exported.data(),0);roundtrip.insert(roundtrip.end(),r.exported.begin(),r.exported.begin()+size);}F_REQUIRE(roundtrip==raw);++files;records+=report.records;}
    std::fclose(manifest);F_REQUIRE(files==12);FILE* output=std::fopen(argv[3],"wb");F_REQUIRE(output);std::fprintf(output,"{\"status\":\"PASS\",\"real_files\":%u,\"real_records\":%u,\"lossless_roundtrip\":true,\"factor_cases\":%u,\"fp_modes\":12,\"registry_filter_slots\":true,\"file_lists\":true,\"normal_facade\":true}\n",files,records,cases);std::fclose(output);return 0;
}
