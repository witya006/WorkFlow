#include "cresobject.h"
#include "global.h"
#include "jmalloc.h"
#include "client455_normal_renderer_math.h"
#include <cstdio>
#include <cstring>
#include <vector>
#include <string>
#include <algorithm>
int RF455_CheckNormalShadowCapture();
int RF455_CheckNormalShadowHal(CRender*,CHARACTEROBJECT*,IDirect3DDevice9*);
int RF455_CheckEffectsGpu(ChInterface*,CHARACTEROBJECT*,IDirect3DDevice9*);

#define R_REQUIRE(x) do{if(!(x)){std::fprintf(stderr,"Normal renderer failure line%d\n",__LINE__);return 1;}}while(0)
template<class T>T read(const void* p,unsigned at){T out;std::memcpy(&out,static_cast<const unsigned char*>(p)+at,sizeof(out));return out;}
static std::vector<unsigned char> capture(IDirect3DDevice9* d){
    IDirect3DSurface9* target=nullptr;IDirect3DSurface9* memory=nullptr;std::vector<unsigned char> pixels;
    if(FAILED(d->GetRenderTarget(0,&target)))return pixels;D3DSURFACE_DESC desc={};target->GetDesc(&desc);
    if(SUCCEEDED(d->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&memory,nullptr)) && SUCCEEDED(d->GetRenderTargetData(target,memory))){D3DLOCKED_RECT lock={};if(SUCCEEDED(memory->LockRect(&lock,nullptr,D3DLOCK_READONLY))){pixels.resize(desc.Width*desc.Height*4);for(unsigned y=0;y<desc.Height;++y)std::memcpy(pixels.data()+4*desc.Width*y,static_cast<const unsigned char*>(lock.pBits)+y*lock.Pitch,4*desc.Width);memory->UnlockRect();}}
    if(memory)memory->Release();target->Release();return pixels;
}
static bool frame(const char* name,const std::vector<unsigned char>& pixels){FILE* f=std::fopen(name,"wb");if(!f)return false;const bool ok=std::fwrite(pixels.data(),1,pixels.size(),f)==pixels.size();std::fclose(f);return ok;}
static int scene(IDirect3DDevice9* d,const char* fixture){
    FILE* f=std::fopen(fixture,"rb");R_REQUIRE(f);char paths[3][512];for(auto& path:paths){R_REQUIRE(std::fgets(path,sizeof(path),f));path[std::strcspn(path,"\r\n")]=0;}std::fclose(f);
    ChInterface renderer;renderer.InitCharacter(d);renderer.native.blendDuration=150;g_ifCharIF=&renderer;
    CUnityBoneMgr bones;CUnityMeshMgr meshes;CUnityAniMgr animations;R_REQUIRE(bones.Create() && meshes.Create() && animations.Create());
    auto* root=bones.AddBone(RLI_MONSTER,paths[1]);auto* model=meshes.AddMesh(RLI_MONSTER,paths[0],root);R_REQUIRE(root && model && !root->m_Load && !model->m_Load);
    renderer.SetTexPath(root,".\\tex");renderer.SetTexPath(model,".\\tex");
    R_REQUIRE(bones.GetBone(RLI_MONSTER,root->m_ID)==root && root->m_Load && meshes.GetMesh(RLI_MONSTER,model->m_ID)==model && model->m_Load);
    auto* animation=animations.AddAni(RLI_MONSTER,paths[2]);R_REQUIRE(animation && renderer.IsLoadAnimation(animation) && animation->m_Load);
    renderer.MatchAnimationToMesh(animation,root);const DWORD originalMax=root->m_OMaxFrame;R_REQUIRE(originalMax>160);
    renderer.AnimationReset(root);R_REQUIRE(root->m_Frame==160 && root->m_OMaxFrame==0);
    for(unsigned i=0;i<root->m_MaxObj;++i)R_REQUIRE(!root->m_pMesh[i].bytes[5094] && !read<unsigned>(root->m_pMesh+i,5095));
    renderer.MatchAnimationToMesh(animation,root);R_REQUIRE(root->m_OMaxFrame==originalMax);
    renderer.RematchParent(root,model);unsigned rematched=0;
    for(unsigned i=0;i<model->m_MaxObj;++i){const auto& mesh=model->m_pMesh[i];if(!read<unsigned>(&mesh,5495))continue;
        auto* expected=RF455_FindParentMesh(mesh.parentName,root->m_pMesh,static_cast<int>(root->m_MaxObj));
        if(expected){R_REQUIRE(mesh.m_pParent==expected && mesh.m_HaveParent);++rematched;}}
    R_REQUIRE(rematched>0);root->m_Frame=model->m_Frame=160;renderer.FrameMove(root);renderer.FrameMove(model);
    f=std::fopen(paths[0],"rb");R_REQUIRE(f);std::fseek(f,0,SEEK_END);const long meshLength=std::ftell(f);std::rewind(f);std::vector<unsigned char> meshRaw(meshLength);R_REQUIRE(std::fread(meshRaw.data(),1,meshRaw.size(),f)==meshRaw.size());std::fclose(f);std::vector<RF455Mesh08Part> inputParts(128);RF455Mesh08View inputView={};R_REQUIRE(RF455_DecodeMesh08(meshRaw.data(),meshRaw.size(),inputParts.data(),inputParts.size(),&inputView)==RF_MESH08_OK);
    R_REQUIRE(model->m_MaxObj==inputView.meshCount && renderer.native.vertexMode==4);
    const float position[3]={1,2,-3};
    D3DXMATRIX rotation,world,conversion;D3DXMatrixIdentity(&world);world._11=world._22=world._33=.5f;
    D3DXMatrixRotationZ(&rotation,3.1415927410125732421875f);D3DXMatrixMultiply(&world,&world,&rotation);
    D3DXMatrixIdentity(&conversion);conversion._22=conversion._33=0;conversion._23=conversion._32=1;D3DXMatrixMultiply(&world,&world,&conversion);world._41=position[0];world._42=position[1];world._43=position[2];
    D3DXVECTOR3 low(1e30f,1e30f,1e30f),high(-1e30f,-1e30f,-1e30f);
    unsigned geometry=0;
    for(unsigned i=0;i<model->m_MaxObj;++i){const auto* mesh=model->m_pMesh+i;const unsigned n=read<unsigned>(mesh,5086);if(!n)continue;++geometry;const unsigned offset=read<unsigned>(mesh,4494);void* bytes=nullptr;auto* buffer=renderer.native.vertices64.buffers[offset/RF455_VERTEX_BLOCK_BYTES];R_REQUIRE(buffer && SUCCEEDED(buffer->Lock(offset%RF455_VERTEX_BLOCK_BYTES,64*n,&bytes,D3DLOCK_READONLY)));
        for(unsigned k=0;k<n;++k){const auto* vertex=static_cast<const unsigned char*>(bytes)+64*k;float weights[]={read<float>(vertex,12),read<float>(vertex,16),read<float>(vertex,20),0};weights[3]=1-weights[0]-weights[1]-weights[2];D3DXVECTOR3 position(0,0,0);
            for(unsigned b=0;b<4;++b){const auto slot=read<unsigned short>(vertex,24+2*b);R_REQUIRE(slot<(std::max<DWORD>)(4,mesh->m_BlendNum));const auto* mat=mesh->bytes+(mesh->m_BlendNum?646+64*slot:4830);D3DXVECTOR3 local;D3DXVec3TransformCoord(&local,reinterpret_cast<const D3DXVECTOR3*>(vertex),reinterpret_cast<const D3DXMATRIX*>(mat));position+=weights[b]*local;}
            D3DXVECTOR3 final;D3DXVec3TransformCoord(&final,&position,&world);for(unsigned axis=0;axis<3;++axis){(&low.x)[axis]=(std::min)((&low.x)[axis],(&final.x)[axis]);(&high.x)[axis]=(std::max)((&high.x)[axis],(&final.x)[axis]);}}
        buffer->Unlock();}
    R_REQUIRE(geometry==46);
    const D3DXVECTOR3 center=(low+high)*.5f;const float span=(std::max)(high.x-low.x,(std::max)(high.y-low.y,high.z-low.z));D3DXVECTOR3 eye=center+D3DXVECTOR3(0,0,-2*span),up(0,1,0);D3DXMATRIX view,projection;D3DXMatrixLookAtLH(&view,&eye,&center,&up);D3DXMatrixOrthoLH(&projection,span*1.3f,span*1.3f,0,4*span);
    std::memcpy(GetR3State()->mMatView,&view,64);std::memcpy(GetR3State()->mMatProj,&projection,64);d->SetTransform(D3DTS_VIEW,&view);d->SetTransform(D3DTS_PROJECTION,&projection);
    D3DLIGHT9 light=renderer.native.light;light.Direction=D3DXVECTOR3(.25f,-.5f,-1);light.Range=123;renderer.SetLight(light);float constant[4];R_REQUIRE(SUCCEEDED(d->GetVertexShaderConstantF(10,constant,1)) && !std::memcmp(constant,&light.Direction,16));
    std::vector<unsigned char> first;
    for(unsigned phase=0;phase<2;++phase){root->m_Frame=model->m_Frame=phase?animation->maximum/2:160;renderer.FrameMove(root);renderer.FrameMove(model);renderer.SetState();
        R_REQUIRE(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff101020,1,0)) && SUCCEEDED(d->BeginScene()));renderer.DrawCharacter(model,const_cast<float*>(position),0,.5f,0);g_AMeshManager.DrawAlpahMesh();R_REQUIRE(SUCCEEDED(d->EndScene()));auto pixels=capture(d);R_REQUIRE(pixels.size()==256*256*4);unsigned colored=0;for(unsigned i=0;i<256*256;++i)if((read<DWORD>(pixels.data(),4*i)&0xffffff)!=0x101020)++colored;std::fprintf(stderr,"phase%u colored%u bounds[%g,%g,%g][%g,%g,%g] parts%lu\n",phase,colored,low.x,low.y,low.z,high.x,high.y,high.z,model->m_MaxObj);char name[64];std::sprintf(name,"normal-frame-%u.bgra",phase);R_REQUIRE(frame(name,pixels));if(!phase)first=pixels;else R_REQUIRE(first!=pixels);
        renderer.SetState();R_REQUIRE(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff101020,1,0)) && SUCCEEDED(d->BeginScene()));renderer.DrawCharacterMat(model,&world,0);g_AMeshManager.DrawAlpahMesh();R_REQUIRE(SUCCEEDED(d->EndScene()));auto direct=capture(d);R_REQUIRE(frame("direct-frame.bgra",direct));R_REQUIRE(direct==pixels);R_REQUIRE(colored>100 && colored<256*256-100);
    }
    renderer.SetAlpha(model,.625f);R_REQUIRE(renderer.GetAlpha(model)==.625f);for(unsigned i=0;i<model->m_MaxObj;++i)R_REQUIRE(model->m_pMesh[i].m_Alpha==.625f);
    D3DMATERIAL9 material=model->m_Material;material.Power=17;renderer.SetMaterial(model,material);renderer.SetMaterial(nullptr,material);R_REQUIRE(!std::memcmp(&model->m_Material,&material,68));
    for(unsigned filter=0;filter<3;++filter){
        model->opaque268=filter==0;renderer.native.effects.active=filter!=0;float planes[6][4]={};planes[0][0]=1;planes[0][3]=filter==1?1000000.0f:-1000000.0f;std::memcpy(reinterpret_cast<unsigned char*>(&renderer.native)+8736,planes,96);renderer.SetState();
        R_REQUIRE(SUCCEEDED(d->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff101020,1,0)) && SUCCEEDED(d->BeginScene()));renderer.DrawCharacter(model,const_cast<float*>(position),0,.5f,0);g_AMeshManager.DrawAlpahMesh();R_REQUIRE(SUCCEEDED(d->EndScene()));const auto pixels=capture(d);R_REQUIRE(pixels.size()==256*256*4);unsigned colored=0;for(unsigned i=0;i<256*256;++i)if((read<DWORD>(pixels.data(),4*i)&0xffffff)!=0x101020)++colored;R_REQUIRE(filter==2?colored>100:colored==0);
    }
    model->opaque268=0;renderer.native.effects.active=0;
    R_REQUIRE(RF455_CheckEffectsGpu(&renderer,model,d)==0);
    R_REQUIRE(RF455_CheckNormalShadowHal(&renderer,model,d)==0);
    renderer.UnSetState();DWORD state;R_REQUIRE(SUCCEEDED(d->GetRenderState(D3DRS_VERTEXBLEND,&state)) && state==D3DVBF_DISABLE);R_REQUIRE(SUCCEEDED(d->GetRenderState(D3DRS_CULLMODE,&state)) && state==D3DCULL_CCW);R_REQUIRE(SUCCEEDED(d->GetSamplerState(4,D3DSAMP_MIPFILTER,&state)) && state==D3DTEXF_POINT);
    g_ifCharIF=nullptr;R_REQUIRE(animations.Destroy() && meshes.Destroy() && bones.Destroy());return 0;
}
int main(int argc,char** argv){
    if(argc!=3)return 2;R_REQUIRE(RF455_CheckNormalShadowCapture()==0);const unsigned before=GetDmallocSize();InitR3Engine();IDirect3D9* api=Direct3DCreate9(D3D_SDK_VERSION);R_REQUIRE(api);HWND window=CreateWindowExA(0,"STATIC","Owned normal455renderer test",WS_OVERLAPPEDWINDOW,0,0,256,256,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);R_REQUIRE(window);
    D3DPRESENT_PARAMETERS pp={};pp.Windowed=TRUE;pp.hDeviceWindow=window;pp.BackBufferWidth=pp.BackBufferHeight=256;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.EnableAutoDepthStencil=TRUE;pp.AutoDepthStencilFormat=D3DFMT_D16;IDirect3DDevice9* d=nullptr;R_REQUIRE(SUCCEEDED(api->CreateDevice(0,D3DDEVTYPE_HAL,window,D3DCREATE_SOFTWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&pp,&d)));
    R_REQUIRE(scene(d,argv[1])==0);for(unsigned i=0;i<8;++i)d->SetTexture(i,nullptr);d->SetStreamSource(0,nullptr,0,0);d->SetIndices(nullptr);d->SetVertexShader(nullptr);d->SetPixelShader(nullptr);d->SetVertexDeclaration(nullptr);RF455_ReleaseNormalCharacterSharedResources();ReleaseR3Engine();const auto refs=d->Release(),apiRefs=api->Release();DestroyWindow(window);R_REQUIRE(!refs && !apiRefs && GetDmallocSize()==before);
    R_REQUIRE(!GetModuleHandleA("mss32.dll") && !GetModuleHandleA("ABuse.dll") && !GetModuleHandleA("Adv.dll") && !GetModuleHandleA("PDLL.dll"));FILE* f=std::fopen(argv[2],"wb");R_REQUIRE(f);std::fputs("{\"status\":\"PASS\",\"normal_unity_model_pipeline\":true,\"animated_frames\":2,\"matrix_wrapper_equal_frames\":2,\"geometry_parts\":46,\"filter_cases\":3,\"alpha_material_checked\":true,\"real_animation_reset_reattach\":true,\"real_mesh_rematch\":true,\"texture_path_method\":true,\"shadow_capture\":true,\"shadow_target_passes\":3,\"real_model_shadow\":true,\"shadow_begin_success_return\":0,\"device_refs\":0,\"dmalloc_balance\":0,\"game_dlls_loaded\":false}\n",f);std::fclose(f);return 0;
}
