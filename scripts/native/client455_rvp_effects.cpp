#include "Character.h"
#include "client455_rvp_effects.h"
#include "client455_resource_io.h"
#include "r3particle.h"
#include "renderparticle.h"
#include "entity.h"
#include "commonutil.h"
#include <mmsystem.h>
#include <array>
#include <cstdio>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <string>

namespace {
const D3DXMATRIX yzmat(1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1); //455BF8148
template<class T>T get(const void* base,unsigned offset){T value;std::memcpy(&value,static_cast<const unsigned char*>(base)+offset,sizeof(value));return value;}
struct ParticleSlot {
    unsigned registered=0,loaded=0,attempted=0,cycle=0,axis=1;
    float scale[3]={1,1,1};std::string name;
    CParticle particles[6];
    ~ParticleSlot(){particles[0].ReleaseParticle();particles[0].ReleaseEntity();}
};
struct EntitySlot {
    unsigned registered=0,loaded=0,attempted=0,axis=1;
    float scale[3]={},rotation[3]={};std::string name;CEntity entity;
    ~EntitySlot(){if(loaded)entity.ReleaseEntity();}
};
struct Shared {
    std::unique_ptr<RF455RvpEffects> effects;unsigned references=0;
    float scroll=0;DWORD previous=0;
};
Shared& shared(){static Shared value;return value;}
void profile(const char* file,const char* section,const char* key,const char* fallback,char* out){GetPrivateProfileStringA(section,key,fallback,out,256,file);}
void number(const char* file,const char* section,const char* key,const char* fallback,float* out){char text[256];profile(file,section,key,fallback,text);std::sscanf(text,"%f",out);}
void axis(const char* file,const char* section,unsigned* out){float value;std::memcpy(&value,out,4);number(file,section,"ABSAXIS","1",&value);std::memcpy(out,&value,4);} //target scans%f into DWORD
}
struct RF455RvpEffects::Runtime {
    std::array<std::unique_ptr<ParticleSlot>,2000> particles;
    std::array<std::unique_ptr<EntitySlot>,2000> entities;
    RF455_RpkGroup chef;
    RF455EffectFiles files;RF455EffectStore store;
    unsigned particleDefinitions=0,entityDefinitions=0,loadedParticles=0,loadedEntities=0;
    unsigned particleSelections=0,particleDraws=0,entityDraws=0;
    Runtime(){
        chef.LoadDirectory(".\\chef\\");
        readEntities(".\\chef\\real\\entity.ini");readParticles(".\\chef\\real\\particle.ini");
        const auto read=RF455_LoadEffectFileTable(&files,&store,".\\chef\\real\\unit.ini",false);
        if(read.status!=RF_EFFECT_OK&&read.status!=RF_EFFECT_MISSING)throw std::runtime_error("RVP EFF list outside accepted format");
    }
    ~Runtime(){
        //The original Chef group is process-owned. This source adapter owns its
        //indexes until the shared RVP cache is released;global owner parity open.
        if(RF455_GetResourceGroup()==&chef)RF455_SetResourceGroup(nullptr);
        for(auto& slot:particles)slot.reset();for(auto& slot:entities)slot.reset();chef.Release();
    }
    void readParticles(const char* file){
        const auto count=GetPrivateProfileIntA("PARTICLE_INFO","MAXPARTICLE",0,file);
        for(unsigned i=1;i<=count;++i){char section[32],text[256],name[256];std::sprintf(section,"PARTICLE%u",i);int index=0;
            profile(file,section,"INDEX","0",text);std::sscanf(text,"%d",&index);profile(file,section,"PARTICLE","NULL",name);
            if(static_cast<unsigned>(index)>=2000)continue;
            if(!particles[index])particles[index].reset(new ParticleSlot);
            auto& slot=*particles[index];slot.name=name;slot.registered=1;
            number(file,section,"SCALEX","1.0",&slot.scale[0]);number(file,section,"SCALEY","1.0",&slot.scale[1]);number(file,section,"SCALEZ","1.0",&slot.scale[2]);axis(file,section,&slot.axis);++particleDefinitions;
        }
    }
    void readEntities(const char* file){
        const auto count=GetPrivateProfileIntA("ENTITY_INFO","MAXENTITY",0,file);
        for(unsigned i=1;i<=count;++i){char section[32],text[256],name[256];std::sprintf(section,"ENTITY%u",i);int index=0;
            profile(file,section,"INDEX","0",text);std::sscanf(text,"%d",&index);profile(file,section,"ENTITY","NULL",name);
            if(static_cast<unsigned>(index)>=2000)continue;
            if(!entities[index])entities[index].reset(new EntitySlot);
            auto& slot=*entities[index];if(slot.registered)continue;slot.name=name;slot.registered=1;
            number(file,section,"SCALEX","1.0",&slot.scale[0]);number(file,section,"SCALEY","1.0",&slot.scale[1]);number(file,section,"SCALEZ","1.0",&slot.scale[2]);axis(file,section,&slot.axis);
            number(file,section,"ROTX","0.0",&slot.rotation[0]);number(file,section,"ROTY","0.0",&slot.rotation[1]);number(file,section,"ROTZ","0.0",&slot.rotation[2]);++entityDefinitions;
        }
    }
    CParticle* particle(unsigned id){
        if(id>=2000)throw std::out_of_range("RVP particle index outside original2000 slots");
        if(!particles[id])particles[id].reset(new ParticleSlot);auto& slot=*particles[id];
        if(!slot.loaded){
            if(slot.attempted)return nullptr;slot.attempted=1;RF455_SetResourceGroup(&chef);
            if(!slot.particles[0].LoadParticleSPT(const_cast<char*>(slot.name.c_str()),8))return nullptr;
            const float zero[3]={};slot.particles[0].InitParticle();slot.particles[0].SetParticleState(1);slot.particles[0].SetCreatePos(const_cast<float*>(zero));
            for(unsigned i=1;i<6;++i){std::memcpy(&slot.particles[i],&slot.particles[0],sizeof(CParticle));slot.particles[i].InitParticle();slot.particles[i].SetParticleState(1);slot.particles[i].SetCreatePos(const_cast<float*>(zero));}
            slot.loaded=1;++loadedParticles;
        }
        const unsigned index=slot.cycle++%6;++particleSelections;return &slot.particles[index];
    }
    CEntity* entity(unsigned id){
        if(id>=2000)throw std::out_of_range("RVP entity index outside original2000 slots");
        if(!entities[id])entities[id].reset(new EntitySlot);auto& slot=*entities[id];
        if(!slot.loaded){if(slot.attempted)return nullptr;slot.attempted=1;RF455_SetResourceGroup(&chef);
            if(!slot.entity.LoadEntity(const_cast<char*>(slot.name.c_str()),8))return nullptr;
            slot.entity.RestoreTexMem();slot.loaded=1;++loadedEntities;}
        return &slot.entity;
    }
};
RF455RvpEffects::RF455RvpEffects():runtime(new Runtime){}
RF455RvpEffects::~RF455RvpEffects(){delete runtime;}
void RF455RvpEffects::Apply(ChInterface& renderer,RF455CharacterStorage* model,unsigned id){
    const auto found=runtime->files.entries.find(id);if(found!=runtime->files.entries.end())RF455_ApplyEffectFile(&runtime->store,&renderer.native,model,found->second.file.c_str(),36);
}
void RF455RvpEffects::Draw(RF455CharacterStorage* model,D3DXMATRIX* world,unsigned color){
    auto& clock=shared();const DWORD now=timeGetTime();if(!clock.previous)clock.previous=now;
    const float delta=float(double(now-clock.previous)*double(.0005f));clock.previous=now;
    clock.scroll=float(double(delta)*30+clock.scroll);
    for(unsigned i=0;i<model->m_MaxObj;++i){auto* mesh=model->m_pMesh[i].bytes;auto* effect=get<const unsigned char*>(mesh,5455);
        if(!effect)throw std::runtime_error("RVP model has no effect record;unaccepted null domain");
        for(unsigned j=0;j<3;++j){const unsigned id=get<unsigned>(effect,220+j*16);if(!id)continue;auto* value=runtime->particle(id);if(!value)continue;
            D3DXMATRIX matrix,rotation;D3DXMatrixMultiply(&matrix,reinterpret_cast<D3DXMATRIX*>(mesh+4830),world);rotation=matrix;rotation._41=rotation._42=rotation._43=0;
            if(!value->Loop())return; //Target returns from the entire model pass.
            std::memcpy(value->mRotMat,&rotation,64);value->SetCreatePos(&matrix._41);color|=0x00ffffffu;
            DrawCParticle(value,value->mEntity,reinterpret_cast<float(*)[4]>(&matrix),color);++runtime->particleDraws;
        }
        const unsigned id=get<unsigned>(effect,268);if(!id)continue;auto* value=runtime->entity(id);if(!value)continue;
        D3DXMATRIX matrix,inverse;D3DXMatrixMultiply(&matrix,reinterpret_cast<D3DXMATRIX*>(mesh+4830),world);
        D3DXMatrixInverse(&inverse,nullptr,reinterpret_cast<const D3DXMATRIX*>(&yzmat));D3DXMatrixMultiply(&matrix,&inverse,&matrix);
        value->DrawEntity(reinterpret_cast<float(*)[4]>(&matrix),color,clock.scroll);++runtime->entityDraws;
    }
}
RF455RvpEffects& RF455_AcquireRvpEffects(){auto& value=shared();if(!value.effects)value.effects.reset(new RF455RvpEffects);++value.references;return *value.effects;}
void RF455_ReleaseRvpEffects(){auto& value=shared();if(!value.effects)return;if(value.references){--value.references;return;}value.effects.reset();} //The first release1->0 retains the cache.
RF455RvpEffectsView RF455_RvpEffectsState(){const auto& value=shared();if(!value.effects)return {false,value.references,0,0,0,0,0,0,0,value.scroll};const auto& r=*value.effects->runtime;return {true,value.references,r.particleDefinitions,r.entityDefinitions,r.loadedParticles,r.loadedEntities,r.particleSelections,r.particleDraws,r.entityDraws,value.scroll};}
