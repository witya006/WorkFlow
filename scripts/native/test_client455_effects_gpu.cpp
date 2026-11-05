#include "Character.h"
#include <cstdio>
#include <cstring>
#include <vector>

#define G_REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"EFF GPU failure line%d\n",__LINE__);return 1;}}while(0)
template<class T>static T get(const void* p,unsigned n){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+n,sizeof(v));return v;}
template<class T>static void put(void* p,unsigned n,T v){std::memcpy(static_cast<unsigned char*>(p)+n,&v,sizeof(v));}
static bool file(const char* name,const void* data,std::size_t size){FILE* f=std::fopen(name,"wb");if(!f)return false;const bool ok=std::fwrite(data,1,size,f)==size;std::fclose(f);return ok;}
static std::vector<unsigned char> pixels(IDirect3DDevice9* d){
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;std::vector<unsigned char> out;if(FAILED(d->GetRenderTarget(0,&target)))return out;D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    if(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)) && SUCCEEDED(d->GetRenderTargetData(target,memory))){D3DLOCKED_RECT lock={};if(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY))){out.resize(desc.Width*desc.Height*4);for(unsigned y=0;y<desc.Height;++y)std::memcpy(out.data()+4*y*desc.Width,static_cast<const unsigned char*>(lock.pBits)+y*lock.Pitch,4*desc.Width);memory->UnlockRect();}}
    if(memory)memory->Release();target->Release();return out;
}
static bool draw(ChInterface* renderer,CHARACTEROBJECT* model,IDirect3DDevice9* device){
    renderer->SetState();if(FAILED(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff101020,1,0)) || FAILED(device->BeginScene()))return false;
    float position[]={1,2,-3};renderer->DrawCharacter(model,position,0,.5f,0);renderer->FlushTransparency();return SUCCEEDED(device->EndScene());
}
int RF455_CheckEffectsGpu(ChInterface* renderer,CHARACTEROBJECT* model,IDirect3DDevice9* device){
    renderer->InitEffect(model);renderer->SetAlpha(model,1);G_REQUIRE(!model->IsHaveEffect());G_REQUIRE(draw(renderer,model,device));const auto baseline=pixels(device);G_REQUIRE(baseline.size()==256*256*4);
    unsigned char raw[176]={};put<unsigned short>(raw,0,176);raw[2]=2;std::strcpy(reinterpret_cast<char*>(raw+3),"effect.dds");std::strcpy(reinterpret_cast<char*>(raw+43),".\\tex\\");raw[63]=1;raw[81]=1;raw[82]=2;put<float>(raw,71,.5f);put<unsigned>(raw,96,17);
    const char files[]="1 gpu.eff 1\n2 gpu.eff 0\n",patterns[]="1 1 1 1 1 1 1 1 1 1\n2 2 2 2 2 2 2 2 2 2\n",items[]="ABCDEF 1 2 0 0 0 0\n",monsters[]="7 gpu.eff\n";
    G_REQUIRE(file("gpu.eff",raw,sizeof(raw)) && file("gpu-files.txt",files,sizeof(files)-1) && file("gpu-patterns.txt",patterns,sizeof(patterns)-1) && file("gpu-items.txt",items,sizeof(items)-1) && file("gpu-monsters.ini",monsters,sizeof(monsters)-1));
    char ef[]="gpu.eff",ff[]="gpu-files.txt",pf[]="gpu-patterns.txt",it[]="gpu-items.txt",mf[]="gpu-monsters.ini";
    EffectObjectManager::LoadEffect(ef);g_EffectFileList.LoadEffectFileList(ff);g_EFFMonList.LoadEffectFileList(mf);g_PatternList.LoadEffectPatternList(pf);g_EffectItemList.LoadItemListFile(it);
    G_REQUIRE(IsHaveMeshEffect(model,0xabcdef,8,0));const auto count=renderer->native.textures.end-renderer->native.textures.begin;G_REQUIRE(!RF455_GetTextureByName(&renderer->native.textures,"effect.dds"));
    SetMeshEffect(model,0xabcdef,8,0);auto* effect=RF455_FindEffect(&RF455_NormalEffects(),ef,"");G_REQUIRE(effect && get<void*>(effect->draw.data(),120));
    G_REQUIRE(renderer->native.textures.end-renderer->native.textures.begin==count+1 && model->IsHaveEffect());const auto id=get<unsigned>(model->m_pMesh[0].bytes,5123);auto* texture=RF455_GetTextureById(&renderer->native.textures,id);G_REQUIRE(texture && texture==get<void*>(effect->draw.data(),120));D3DSURFACE_DESC desc={};G_REQUIRE(SUCCEEDED(texture->GetLevelDesc(0,&desc)) && desc.Width && desc.Height);
    for(unsigned i=0;i<model->m_MaxObj;++i){auto& mesh=model->m_pMesh[i];G_REQUIRE(get<void*>(mesh.bytes,5455)==effect->draw.data() && get<void*>(mesh.bytes,5115)==texture && mesh.particleSlots()[0].m_ID==17);G_REQUIRE(get<unsigned>(mesh.bytes,5147)==RF455_EffectFactor(effect->draw.data()+176,8));if(i)G_REQUIRE(get<unsigned>(mesh.bytes,5123)==0xffffffffu);}
    SetMeshEffect(model,0xabcdef,8,1);G_REQUIRE(get<unsigned>(model->m_pMesh[0].bytes,5147)==RF455_EffectFactor(effect->draw.data()+176,36));G_REQUIRE(renderer->native.textures.end-renderer->native.textures.begin==count+1);
    G_REQUIRE(!EffectObjectManager::SetPartEffect(model,ef,9));G_REQUIRE(get<unsigned>(model->m_pMesh[0].bytes,5147)==RF455_EffectFactor(effect->draw.data()+176,9));g_EFFMonList.SetEffect(model,7);
    G_REQUIRE(draw(renderer,model,device));const auto rendered=pixels(device);G_REQUIRE(rendered.size()==baseline.size() && rendered!=baseline);unsigned changed=0;for(unsigned i=0;i<rendered.size();i+=4)changed+=get<DWORD>(rendered.data(),i)!=get<DWORD>(baseline.data(),i);G_REQUIRE(changed>100);
    G_REQUIRE(file("normal-effect-before.bgra",baseline.data(),baseline.size()) && file("normal-effect-after.bgra",rendered.data(),rendered.size()));std::fprintf(stderr,"EFF changed pixels %u texture %u x %u\n",changed,desc.Width,desc.Height);
    renderer->InitEffect(model);G_REQUIRE(!model->IsHaveEffect());for(unsigned i=0;i<model->m_MaxObj;++i){const auto& mesh=model->m_pMesh[i];G_REQUIRE(get<void*>(mesh.bytes,5455)==mesh.bytes+5163 && !get<void*>(mesh.bytes,5115) && mesh.m_Alpha==1);}
    return 0;
}
