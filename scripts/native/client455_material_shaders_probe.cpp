#define RF455_LIGHTING_CONSUMERS_NO_MAIN
#include "client455_lighting_consumers_probe.cpp"
#include "client455_special_shaders.h"
#include "client455_character_rfs.h"
#include "client455_material_shaders.h"
#include "client455_shader_lights.h"
#include "r3lightmap.h"
#include "renderparticle.h"
struct Groups135{using Type=_BSP_MAT_GROUP* CBsp::*;friend Type access(Groups135);};template struct MemberAccess<Groups135,&CBsp::mMatGroup>;
struct Render135{using Type=void(CBsp::*)(WORD);friend Type access(Render135);};template struct MemberAccess<Render135,&CBsp::RenderMatGroup>;
struct Sample135{float vs[80],ps6[4],ps15[4],ps17[4],ps18[4];DWORD fog;bool vertex,pixel;std::array<bool,8> textures;};
static std::vector<Sample135> draws135;static std::array<IDirect3DBaseTexture9*,8> expected135;static unsigned stageCount135;
static HRESULT WINAPI observe135(IDirect3DDevice9* d,D3DPRIMITIVETYPE type,INT base,UINT low,UINT vertices,UINT start,UINT primitives){
    slot125(reinterpret_cast<void*>(originalDraw125));Sample135 s={};check(SUCCEEDED(d->GetVertexShaderConstantF(0,s.vs,20))&&SUCCEEDED(d->GetPixelShaderConstantF(6,s.ps6,1))&&SUCCEEDED(d->GetPixelShaderConstantF(15,s.ps15,1))&&SUCCEEDED(d->GetPixelShaderConstantF(17,s.ps17,1))&&SUCCEEDED(d->GetPixelShaderConstantF(18,s.ps18,1))&&SUCCEEDED(d->GetRenderState(D3DRS_FOGENABLE,&s.fog)),"real draw constant queries135");
    IDirect3DVertexShader9* vs=nullptr;IDirect3DPixelShader9* ps=nullptr;d->GetVertexShader(&vs);d->GetPixelShader(&ps);s.vertex=vs==RF455_GetSpecialShaderTables().vertices[0].program;s.pixel=ps==RF455_GetSpecialShaderTables().pixels[0].program;if(vs)vs->Release();if(ps)ps->Release();
    for(unsigned i=0;i<=stageCount135;++i){IDirect3DBaseTexture9* texture=nullptr;check(SUCCEEDED(d->GetTexture(i,&texture)),"draw texture135");s.textures[i]=texture==expected135[i];if(texture)texture->Release();}
    draws135.push_back(s);const HRESULT result=originalDraw125(d,type,base,low,vertices,start,primitives);slot125(reinterpret_cast<void*>(observe135));return result;
}
struct Hook135{Hook135(IDirect3DDevice9* d){real125=*reinterpret_cast<void***>(d);originalDraw125=reinterpret_cast<Draw125>(real125[82]);slot125(reinterpret_cast<void*>(observe135));}~Hook135(){slot125(reinterpret_cast<void*>(originalDraw125));}};
static void file135(const char* name,const char* text){FILE* f=std::fopen(name,"wb");check(f!=nullptr,"fixture135");std::fwrite(text,1,std::strlen(text),f);std::fclose(f);}
static void json135(FILE* f,const float* values,unsigned count){std::fputc('[',f);for(unsigned i=0;i<count;++i)std::fprintf(f,"%s%u",i?",":"",bits125(values[i]));std::fputc(']',f);}
static int run135(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);auto* s=GetR3State();s->mScreenXsize=640;s->mScreenYsize=480;s->mbFullScreen=FALSE;ForceFullScreen();std::strcpy(s->MapPath,".\\Map\\");std::strcpy(s->EntityPath,".\\Map\\Entity\\");check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device135");auto* d=GetD3dDevice();FILE* trace=std::fopen("material-shaders.jsonl","wb");check(trace!=nullptr,"trace135");std::setvbuf(trace,nullptr,_IONBF,0);
    unsigned cases=0,splat=0;std::array<unsigned,4> pixels={};
    {
        CCamera camera;g_pCamera=&camera;CLand land;check(land.Create()!=0,"land135");char map[]=".\\Map\\bellato\\bellato.bsp";check(land.LoadLevel(map)!=0,"real Bellato135");auto& level=*land.GetLevel();auto& bsp=*level.mBsp;auto* groups=bsp.*access(Groups135{});unsigned selected=0;
        while(selected<bsp.GetMatGroupNum()&&(groups[selected].MtlId<0||groups[selected].LgtId<0||(groups[selected].Type&(_MAT_CORONA|_MAT_GROUP_TYPE_OPPA|_MAT_Y_BILLBOARD))||!groups[selected].TriNum))++selected;
        check(selected<bsp.GetMatGroupNum(),"actual ordinary textured lightmapped BSP group135");auto& group=groups[selected];auto& material=GetMainMaterial()[group.MtlId];const auto original=material;
        std::vector<int> textures;std::vector<IDirect3DBaseTexture9*> pointers;
        for(unsigned m=0;m<GetMainMaterialNum()&&textures.size()<7;++m){const auto& mat=GetMainMaterial()[m];for(unsigned l=0;l<mat.m_dwLayerNum&&textures.size()<7;++l){const int id=mat.m_Layer[l].m_iSurface;auto* p=id<0?nullptr:R3GetSurface(id);if(p&&std::find(pointers.begin(),pointers.end(),p)==pointers.end()){textures.push_back(id);pointers.push_back(p);}}}
        check(textures.size()==7,"seven distinct real textures135");
        D3DXVECTOR3 center((group.BBMin[0]+group.BBMax[0])/2,(group.BBMin[1]+group.BBMax[1])/2,(group.BBMin[2]+group.BBMax[2])/2);float radius=1;
        for(unsigned axis=0;axis<3;++axis)radius=max(radius,group.BBMax[axis]-group.BBMin[axis]);D3DXVECTOR3 eye(center.x+.5f*radius,center.y+radius,center.z-1.4f*radius),up(0,1,0);D3DXMATRIX view;D3DXMatrixLookAtLH(&view,&eye,&center,&up);float position[]={eye.x,eye.y,eye.z};level.SetCameraPos(position);level.SetViewMatrix(&view);D3DXMatrixInverse(&s->mInvMatView,nullptr,&s->mMatView);D3DXMatrixPerspectiveFovLH(&s->mMatProj,.9f,4.f/3,.1f,100000);D3DXMatrixIdentity(&s->mMatWorld);R3SetTime(.25f);R3SetLoopTime(1.f/30);level.FrameMove();
        const float divider[]={1,1,19,23},cameraSeed[]={eye.x,eye.y,eye.z,1},plasmaSeed[]={1,0,0,0},oldPS6[]={3,5,7,11};
        d->SetVertexShaderConstantF(12,cameraSeed,1);d->SetVertexShaderConstantF(13,divider,1);d->SetPixelShaderConstantF(16,plasmaSeed,1);
        RF455_ClearShaderLights();
        auto render=[&](unsigned flags,unsigned layers,unsigned mode,const char* frame){
            material.m_dwFlag=mode==1?0x11000105u:0x01000001u;material.m_dwLayerNum=layers;material.m_iDetailSurface=-1;
            for(unsigned i=0;i<7;++i){material.m_Layer[i]=_ONE_LAYER{};material.m_Layer[i].m_iSurface=textures[i];material.m_Layer[i].m_ARGB=0xffffffff;}
            auto& first=material.m_Layer[0];first.m_dwFlag=flags;first.m_sUVScrollU=-257;first.m_sUVScrollV=32767;first.m_fSpecularFlickeringScale=.375f;first.m_fSpecularFlickeringSpeed=-.625f;
            s->mIsFog=TRUE;d->SetRenderState(D3DRS_FOGENABLE,TRUE);d->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE);d->SetRenderState(D3DRS_ZENABLE,FALSE);d->SetRenderState(D3DRS_ZWRITEENABLE,FALSE);d->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE);d->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE);d->SetRenderState(D3DRS_LIGHTING,FALSE);d->SetPixelShaderConstantF(6,oldPS6,1);R3SetTime(cases%3==0?0.f:cases%3==1?.25f:1.75f);
            stageCount135=layers;expected135.fill(nullptr);for(unsigned i=0;i<layers;++i)expected135[i]=pointers[i];expected135[layers]=static_cast<IDirect3DBaseTexture9*>(GetLightMapSurface(group.LgtId));draws135.clear();
            check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"begin special material135");{Hook135 hook(d);(bsp.*access(Render135{}))(WORD(selected));}check(SUCCEEDED(d->EndScene()),"end special material135");check(draws135.size()==1,"one actual special DIP135");const auto& draw=draws135[0];check(draw.vertex&&draw.pixel&&draw.fog==FALSE,"actual ordinary BSP shader dispatch135");
            check(!std::memcmp(draw.vs,&s->mMatProj,64)&&!std::memcmp(draw.vs+16,&s->mMatView,64)&&!std::memcmp(draw.vs+32,&s->mMatWorld,64)&&!std::memcmp(draw.vs+60,&s->mInvMatView._41,16)&&!std::memcmp(draw.ps15,&s->mInvMatView._41,16),"untransposed matrices and full inverse-view position135");
            check(!std::memcmp(draw.vs+48,cameraSeed,16)&&!std::memcmp(draw.vs+52,divider,16),"target leaves VS12/13 untouched135");for(unsigned i=0;i<=layers;++i)check(draw.textures[i],"all actual material textures plus lightmap135");
            for(unsigned i=0;i<layers;++i){IDirect3DBaseTexture9* p=nullptr;d->GetTexture(i,&p);check(!p,"cleanup each active texture135");}
            IDirect3DBaseTexture9* lightmap=nullptr;d->GetTexture(layers,&lightmap);check(lightmap==expected135[layers],"lightmap beyond material layers persists135");if(lightmap)lightmap->Release();IDirect3DVertexShader9* vs=nullptr;IDirect3DPixelShader9* ps=nullptr;d->GetVertexShader(&vs);d->GetPixelShader(&ps);check(!vs&&!ps,"cleanup both shader stages135");DWORD fog;d->GetRenderState(D3DRS_FOGENABLE,&fog);check(!fog,"fog remains disabled135");
            if(!mode)check(!std::memcmp(draw.vs+72,&s->mInvMatView._41,16)&&!std::memcmp(draw.ps6,oldPS6,16),"no-light position fallback retains PS6");
            else{auto* light=RF455_GetShaderLight(0);check(!std::memcmp(draw.vs+72,light->position,16)&&!std::memcmp(draw.ps6,light->color,12),"actual first light fields135");}
            const auto selection=RF455_GetMaterialShaderSelection();check(selection.objectIndex==0&&selection.lightIndex==(mode==1?5u:mode==2?5u:0u),"packed indices and retained light selector135");
            std::fprintf(trace,"{\"kind\":\"draw\",\"id\":%u,\"layers\":%u,\"flags\":%u,\"light_mode\":%u,\"time\":%u,\"ps18\":",cases,layers,flags,mode,bits125(R3GetTime()));json135(trace,draw.ps18,4);std::fputs(",\"ps17\":",trace);json135(trace,draw.ps17,4);std::fprintf(trace,",\"selection\":[%d,%u],\"textures_and_cleanup\":true}\n",selection.objectIndex,selection.lightIndex);++cases;
            return frame?capture(frame):0;
        };
        for(unsigned layers:{1u,2u,7u})for(DWORD flags:{0u,1u,2u,0x800000u,0x10u,0x20u,0x30u,0x800033u})render(flags,layers,0,nullptr);
        pixels[0]=render(0x800033,2,0,"material-fraction.bgra");
        file135("light0.spt","[Particle]\n[light]\nlightcolor .25 .5 .75\npower 3\nradius 9\n[endlight]\n");file135("light1.spt","[Particle]\n[LIGHT]\nLIGHTCOLOR .125 .25 .5\nRADIUS 7\n[ENDLIGHT]\n");CParticle emitter0,emitter1;char f0[]="light0.spt",f1[]="light1.spt";check(emitter0.LoadParticleSPT(f0)&&emitter1.LoadParticleSPT(f1)&&emitter0.mLightID==0&&emitter1.mLightID==1&&RF455_GetShaderLightCount()==2,"real particle loader publishes light blocks135");auto* light=RF455_GetShaderLight(0);check(light->scale==1&&light->radius==9&&light->position[0]==0&&light->color[2]==.75f,"ctor/defaults/aliased power-radius field135");
        float world[4][4]={};for(unsigned i=0;i<4;++i)world[i][i]=1;world[3][0]=17;world[3][1]=-23;world[3][2]=31;DrawCParticle(&emitter1,nullptr,world,0xffffffff);check(light->position[0]==17&&light->position[1]==-23&&light->position[2]==31&&light->color[0]==.125f&&light->color[1]==.25f&&light->color[2]==.5f,"ordinary particle draw updates destination0 from selected1");
        for(unsigned layers:{1u,2u,7u})for(DWORD flags:{0u,1u,2u,0x800000u,0x10u,0x20u,0x30u,0x800033u})render(flags,layers,1,nullptr);
        pixels[1]=render(0x800033,7,2,"material-light.bgra");
        for(DWORD splatFlag:{0x01000041u,0x40u}){material.m_dwFlag=splatFlag;material.m_dwLayerNum=3;stageCount135=3;draws135.clear();check(SUCCEEDED(d->BeginScene()),"splat begin135");{Hook135 hook(d);(bsp.*access(Render135{}))(WORD(selected));}check(SUCCEEDED(d->EndScene())&&draws135.size()==3&&draws135[0].vertex==bool(splatFlag&0x01000000)&&!draws135[1].vertex&&!draws135[2].vertex,"base/special draw followed by fixed pair/lightmap splat passes135");splat+=unsigned(draws135.size());if(splatFlag&0x01000000){check(RF455_GetMaterialShaderSelection().objectIndex==64,"whole DWORD shader index includes splat bit135");pixels[2]=capture("material-splat.bgra");}}
        //Select the other supplied source pair through a staged binary-list
        //variant;original installed resources stay immutable.
        check(std::rename("System/shader/init.r3o","System/shader/init.original.r3o")==0,"save staged binary list135");FILE* f=std::fopen("System/shader/init.original.r3o","rb");check(f!=nullptr,"read shader list135");std::vector<BYTE> list(1424);check(std::fread(list.data(),1,list.size(),f)==list.size(),"shader list length135");std::fclose(f);for(unsigned at:{264u,844u})for(unsigned n=0;n<288;++n)std::swap(list[at+n],list[at+288+n]);f=std::fopen("System/shader/init.r3o","wb");std::fwrite(list.data(),1,list.size(),f);std::fclose(f);
        RF455_GetCharacterRfsCache()->ClearPayloads(); // The probe deliberately rewrote an immutable input.
        check(!RF455_LoadSpecialShaderBinary(),"actual Plazma list variant135");pixels[3]=render(0x800033,2,2,"material-plasma.bgra");
        check(std::rename("System/shader/init.r3o","plasma.r3o")==0&&std::rename("System/shader/init.original.r3o","System/shader/init.r3o")==0,"restore actual original list135");
        RF455_GetCharacterRfsCache()->ClearPayloads();
        check(!RF455_LoadSpecialShaderBinary(),"reload actual original list135");material=original;RF455_ClearShaderLights();land.Destroy();g_pCamera=nullptr;
    }
    std::fclose(trace);g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result135");std::fprintf(out,"{\"status\":\"PASS\",\"draw_cases\":%u,\"splat_draws\":%u,\"actual_particle_lights\":2,\"GPU_frames\":4,\"pixels\":[%u,%u,%u,%u],\"unowned_PS6w_certified\":false,\"full_client\":false,\"warnings\":%u}\n",cases,splat,pixels[0],pixels[1],pixels[2],pixels[3],warnings);std::fclose(out);return 0;
}
int main(){try{return run135();}catch(const std::exception& e){std::fprintf(stderr,"material-shaders135:%s\n",e.what());return 1;}}
