#define RF455_SKY_MATERIAL_NO_MAIN
#include "client455_sky_material_probe.cpp"
#include "client455_entity_lighting.h"
#include "client455_sky_atmosphere.h"
#include "client455_sky_lighting.h"
#include "r3material.h"
#include "client455_resource_io.h"
#include <cstddef>
void PreRenderOneLayer(CVertexBuffer*,_BSP_MAT_GROUP*);
void AfterRenderOneLayer(CVertexBuffer*,_BSP_MAT_GROUP*);
void GetBumpFactor(Vector4f);
void ExtractVertex(WORD,int,Vector3f*,void*,Vector3f,float);
static_assert(sizeof(_D3DR3VERTEX_TEX1)==36&&offsetof(_D3DR3VERTEX_TEX1,nx)==12&&offsetof(_D3DR3VERTEX_TEX1,color)==24&&offsetof(_D3DR3VERTEX_TEX1,u)==28,"455 vertex layout");
//Typed source records retain the legacy allocation ABI. Target455 has a
//526-byte runtime record;field correspondence must be proved,not cast to it.
static_assert(sizeof(_R3MATERIAL)==332&&offsetof(_R3MATERIAL,m_Layer)+sizeof(_ONE_LAYER)+offsetof(_ONE_LAYER,m_dwFlag)==208,"own material layer1 flag,not top-level material flag");
static void floats130(FILE* f,const float* p,unsigned n){std::fputc('[',f);for(unsigned i=0;i<n;++i)std::fprintf(f,"%s%u",i?",":"",bits125(p[i]));std::fputc(']',f);}
static DWORD stage130(IDirect3DDevice9* d,DWORD slot,D3DTEXTURESTAGESTATETYPE s){DWORD v;check(SUCCEEDED(d->GetTextureStageState(slot,s,&v)),"stage130");return v;}
static DWORD render130(IDirect3DDevice9* d,D3DRENDERSTATETYPE s){DWORD v;check(SUCCEEDED(d->GetRenderState(s,&v)),"render130");return v;}
static unsigned frameIndex130,shaderBytes130,stride130;
static HRESULT WINAPI observe130(IDirect3DDevice9* d,D3DPRIMITIVETYPE type,INT base,UINT low,UINT vertices,UINT start,UINT primitives){
    slot125(reinterpret_cast<void*>(originalDraw125));samples125.push_back(sample125(d));
    if(samples125.size()==1){
        IDirect3DVertexBuffer9* stream=nullptr;UINT offset=0;check(SUCCEEDED(d->GetStreamSource(0,&stream,&offset,&stride130)),"actual draw stream");if(stream)stream->Release();
        IDirect3DVertexShader9* shader=nullptr;check(SUCCEEDED(d->GetVertexShader(&shader)),"actual draw shader");shaderBytes130=0;
        if(shader){UINT size=0;check(SUCCEEDED(shader->GetFunction(nullptr,&size)),"actual shader size");std::vector<BYTE> code(size);check(SUCCEEDED(shader->GetFunction(code.data(),&size)),"actual shader bytecode");
            char name[64];std::sprintf(name,"draw-shader-%u.bin",frameIndex130);FILE* f=std::fopen(name,"wb");check(f!=nullptr,"shader capture");std::fwrite(code.data(),1,size,f);std::fclose(f);shaderBytes130=size;shader->Release();}
    }
    const HRESULT result=originalDraw125(d,type,base,low,vertices,start,primitives);slot125(reinterpret_cast<void*>(observe130));return result;
}
struct Hook130{Hook130(IDirect3DDevice9* d){real125=*reinterpret_cast<void***>(d);originalDraw125=reinterpret_cast<Draw125>(real125[82]);slot125(reinterpret_cast<void*>(observe130));}~Hook130(){slot125(reinterpret_cast<void*>(originalDraw125));}};
static void normalDiagnostic130(){
    FILE* file=std::fopen("entity-resolved.r3e","rb");check(file!=nullptr,"diagnostic input");_ENTITY_FILE_HEADER h;std::fseek(file,8,SEEK_SET);check(std::fread(&h,sizeof(h),1,file)==1,"diagnostic header");
    std::fseek(file,0,SEEK_END);const long size=std::ftell(file)-88;std::fseek(file,88,SEEK_SET);std::vector<BYTE> bytes(size);check(std::fread(bytes.data(),size,1,file)==1,"diagnostic streams");std::fclose(file);
    auto* comp=reinterpret_cast<_ENTITY_COMP_HEADER*>(bytes.data());BYTE* packed=bytes.data()+h.CompHeader.size;BYTE* colors=packed+h.Vertex.size;BYTE* uv=colors+h.VColor.size;auto* faces=reinterpret_cast<_READ_ENTITY_FACE*>(uv+h.UV.size);
    auto* faceIds=reinterpret_cast<WORD*>(reinterpret_cast<BYTE*>(faces)+h.Face.size);auto* vertexIds=reinterpret_cast<WORD*>(reinterpret_cast<BYTE*>(faceIds)+h.FaceId.size);auto* groups=reinterpret_cast<_READ_ENTITY_M_GROUP*>(reinterpret_cast<BYTE*>(vertexIds)+h.VertexId.size);
    const unsigned count=h.Vertex.size/((comp->type&0x8000)?3:(comp->type&0x4000)?6:12);std::vector<float> positions(count*3);auto* points=reinterpret_cast<Vector3f*>(positions.data());ExtractVertex(comp->type,count,points,packed,comp->pos,comp->scale);
    FILE* out=std::fopen("normal-diagnostic.jsonl","wb");check(out!=nullptr,"normal diagnostic trace");
    for(unsigned group=0;group<h.MatGroup.size/sizeof(_READ_ENTITY_M_GROUP);++group)for(unsigned j=0;j<groups[group].face_num;++j){const auto& face=faces[faceIds[groups[group].face_start_id+j]];unsigned hits=0;for(unsigned k=0;k<face.v_num;++k)hits+=vertexIds[face.v_start_id+k]==1;
        if(!hits)continue;Vector4f normal;const WORD a=vertexIds[face.v_start_id],b=vertexIds[face.v_start_id+1],c=vertexIds[face.v_start_id+2];GetNormal(normal,points[a],points[b],points[c]);
        std::fprintf(out,"{\"face\":%u,\"hits\":%u,\"normal\":",j,hits);floats130(out,normal,3);std::fputs(",\"a\":",out);floats130(out,points[a],3);std::fputs(",\"b\":",out);floats130(out,points[b],3);std::fputs(",\"c\":",out);floats130(out,points[c],3);std::fputs("}\n",out);
    }std::fclose(out);
}
static int run130(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);InitR3Engine();SetWarningMessageProc(warningMessage);SetErrorMessageProc(errorMessage);
    auto* s=GetR3State();s->mScreenXsize=640;s->mScreenYsize=480;s->mbFullScreen=FALSE;ForceFullScreen();std::strcpy(s->MapPath,".\\Map\\");std::strcpy(s->EntityPath,".\\Map\\Entity\\");
    check(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"device130");auto* d=GetD3dDevice();D3DCAPS9 caps;check(SUCCEEDED(d->GetDeviceCaps(&caps)),"actual caps130");
    FILE* out=std::fopen("lighting-consumers.jsonl","wb");check(out!=nullptr,"trace130");std::setvbuf(out,nullptr,_IONBF,0);const auto provider=RF455_ClockTickSource;RF455_ClockTickSource=now125;tick125=0;
    {
        CCamera camera;g_pCamera=&camera;CLand land;check(land.Create()!=0,"land130");char map[]=".\\Map\\bellato\\bellato.bsp";check(land.LoadLevel(map)!=0,"Bellato130");auto& level=*land.GetLevel();
        RF455_SetSkyDayEnabled(1);RF455_SetDayTime(12,0,0);level.FrameMove();
        unsigned selected=0;while(selected<GetMainMaterialNum()&&GetMainMaterial()[selected].m_Layer[0].m_iSurface<0)++selected;check(selected<GetMainMaterialNum(),"actual textured material130");
        auto& material=GetMainMaterial()[selected];const auto original=material;_BSP_MAT_GROUP group={};group.MtlId=short(selected);group.LgtId=-1;
        for(unsigned cap=0;cap<2;++cap)for(DWORD flag:{0u,0x40u})for(unsigned bump=0;bump<2;++bump){
            D3DCAPS9 fixture=caps;fixture.TextureOpCaps=(fixture.TextureOpCaps&~D3DTEXOPCAPS_BUMPENVMAP)|(cap?D3DTEXOPCAPS_BUMPENVMAP:0);RF455_SetLightingCaps(&fixture);
            material.m_dwFlag=flag;material.m_iDetailSurface=-1;material.m_dwLayerNum=2;material.m_Layer[0].m_dwFlag=0;material.m_Layer[1].m_dwFlag=bump?0x8000:0;material.m_Layer[1].m_iSurface=material.m_Layer[0].m_iSurface;
            d->SetRenderState(D3DRS_TEXTUREFACTOR,0x12345678);d->SetRenderState(D3DRS_ALPHATESTENABLE,TRUE);PreRenderOneLayer(nullptr,&group);
            const DWORD beforeOp=stage130(d,0,D3DTSS_COLOROP),beforeAlpha=render130(d,D3DRS_ALPHATESTENABLE);AfterRenderOneLayer(nullptr,&group);
            std::fprintf(out,"{\"kind\":\"material\",\"cap\":%u,\"flag\":%u,\"bump\":%u,\"pre_op\":%u,\"pre_alpha\":%u,\"post_op\":%u,\"post_arg2\":%u,\"post_factor\":%u,\"tint\":%u}\n",cap,flag,bump,beforeOp,beforeAlpha,stage130(d,0,D3DTSS_COLOROP),stage130(d,0,D3DTSS_COLORARG2),render130(d,D3DRS_TEXTUREFACTOR),RF455_GetSkyTintColor());
        }material=original;RF455_SetLightingCaps(&caps);
        for(float time:{0.f,.5f,5.125f}){R3SetTime(time);Vector4f bump;GetBumpFactor(bump);std::fprintf(out,"{\"kind\":\"bump\",\"time\":%u,\"values\":",bits125(time));floats130(out,bump,4);std::fputs("}\n",out);}
        CEntity entity;char model[]=".\\Map\\Entity\\e_battledungeon2\\bd_grass01\\bd_grass01.r3e";
        {FILE* input=RF455_OpenResource(model,"rb");FILE* copy=std::fopen("entity-resolved.r3e","wb");check(input&&copy,"actual resolved entity input");BYTE bytes[4096];size_t size;while((size=std::fread(bytes,1,sizeof(bytes),input)))std::fwrite(bytes,1,size,copy);std::fclose(copy);std::fclose(input);}
        normalDiagnostic130();check(entity.LoadEntity(model,0)!=0,"real entity130");check(entity.mVertexCount>0&&entity.GetStaticVertexBuffer()->m_lpVertexBuffer,"actual GPU vertices130");
        void* vertices=nullptr;auto* vb=static_cast<IDirect3DVertexBuffer9*>(entity.GetStaticVertexBuffer()->m_lpVertexBuffer);check(SUCCEEDED(vb->Lock(0,entity.mVertexCount*36,&vertices,D3DLOCK_READONLY)),"actual vertex readback130");FILE* binary=std::fopen("entity-vertices.bin","wb");check(binary!=nullptr,"vertex capture130");std::fwrite(vertices,36,entity.mVertexCount,binary);std::fclose(binary);vb->Unlock();
        std::fprintf(out,"{\"kind\":\"vertices\",\"count\":%u,\"groups\":%d,\"stride\":36,\"cw\":%u}\n",entity.mVertexCount,entity.GetMatGroupNum(),cw125());
        const float rx=entity.mBBMax[0]-entity.mBBMin[0],ry=entity.mBBMax[1]-entity.mBBMin[1],rz=entity.mBBMax[2]-entity.mBBMin[2],radius=max(50.f,max(rx,max(ry,rz)));
        D3DXMATRIX world;D3DXMatrixIdentity(&world);world._41=-(entity.mBBMin[0]+entity.mBBMax[0])*.5f;world._42=-(entity.mBBMin[1]+entity.mBBMax[1])*.5f;world._43=-(entity.mBBMin[2]+entity.mBBMax[2])*.5f;
        D3DXVECTOR3 eye(0,radius*.15f,-radius*2),at(0,0,0),up(0,1,0);D3DXMATRIX view;D3DXMatrixLookAtLH(&view,&eye,&at,&up);s->mNear=1;s->mFar=10000;s->mFov=.6f;s->mAsfectRatio=4.f/3;s->mIsFog=FALSE;
        level.SetViewMatrix(&view);D3DXMatrixPerspectiveFovLH(&s->mMatProj,s->mFov,s->mAsfectRatio,s->mNear,s->mFar);d->SetTransform(D3DTS_VIEW,&view);d->SetTransform(D3DTS_PROJECTION,&s->mMatProj);Vector3f direction={.2f,1.f,.3f};SetMainLight(direction);
        const DWORD flags[]={0x20,0x20,0x60,0x22,0x62};const char* names[]={"consumer-disabled.bgra","consumer-map-tint.bgra","consumer-lit-fixed.bgra","consumer-grass.bgra","consumer-lit-grass.bgra"};
        for(unsigned i=0;i<5;++i){frameIndex130=i;shaderBytes130=stride130=0;RF455_SetSkyDayEnabled(i!=0);entity.mFlag=flags[i];entity.SetMapColor(0xff4080c0);R3SetTime(.5f);R3SetLoopTime(1.f/30);const DWORD wanted=RF455_ApplySkyTint(entity.GetMapColor());
            d->SetRenderState(D3DRS_LIGHTING,FALSE);d->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE);d->SetRenderState(D3DRS_TEXTUREFACTOR,0x12345678);
            check(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff102030,1,0))&&SUCCEEDED(d->BeginScene()),"begin130");
            {Hook130 hook(d);samples125.clear();if(i<3)check(entity.DrawEntity(world.m,0xc0ffffff,0)!=0,"actual fixed entity130");else{_ENTITY_LIST list={};list.ShaderID=1;list.Factor[0]=.75f;list.Factor[1]=.25f;check(entity.DrawEntityVS(&list,world.m,0xc0ffffff)!=0,"actual shader entity130");}}
            check(SUCCEEDED(d->EndScene())&&!samples125.empty(),"actual entity submissions130");const unsigned pixels=capture(names[i]);D3DMATERIAL9 m;d->GetMaterial(&m);float constants[24];d->GetVertexShaderConstantF(19,constants,6);
            std::fprintf(out,"{\"kind\":\"frame\",\"id\":%u,\"flags\":%u,\"sky_tint\":%u,\"expected_tint\":%u,\"actual_factor\":%u,\"draws\":%u,\"pixels\":%u,\"shader_bytes\":%u,\"stride\":%u,\"material\":",i,flags[i],RF455_GetSkyTintColor(),wanted,samples125.front().render[0],unsigned(samples125.size()),pixels,shaderBytes130,stride130);floats130(out,reinterpret_cast<float*>(&m),17);std::fputs(",\"constants\":",out);floats130(out,constants,24);std::fprintf(out,",\"color_op\":%u,\"post\":[%u,%u,%u,%u,%u]}\n",samples125.front().stage[0],render130(d,D3DRS_LIGHTING),render130(d,D3DRS_COLORVERTEX),render130(d,D3DRS_DIFFUSEMATERIALSOURCE),render130(d,D3DRS_SPECULARENABLE),render130(d,D3DRS_EMISSIVEMATERIALSOURCE));
        }
#ifdef RF455_LIGHT_EXTRA
        RF455_LIGHT_EXTRA(entity,world);
#endif
        entity.ReleaseEntity();land.Destroy();g_pCamera=nullptr;
    }
    RF455_ClockTickSource=provider;std::fclose(out);g_MainApp.ReleaseR3D3D();ReleaseR3Engine();FILE* result=std::fopen("result.json","wb");check(result!=nullptr,"result130");std::fprintf(result,"{\"status\":\"PASS\",\"material_cases\":8,\"frames\":5,\"warnings\":%u,\"full_lighting\":false}\n",warnings);std::fclose(result);return 0;
}
#ifndef RF455_LIGHTING_CONSUMERS_NO_MAIN
int main(){try{return run130();}catch(const std::exception& e){std::fprintf(stderr,"lighting130:%s\n",e.what());return 1;}}
#endif
