#define RF455_EQUIPMENT_NO_MAIN
#include "client455_equipment_probe.cpp"
#include "multilayer.h"
#include <array>
#include <fstream>
#include <iterator>
#include "client455_resource_io.h"

namespace {
using GradeDraw=HRESULT(WINAPI*)(IDirect3DDevice9*,D3DPRIMITIVETYPE,INT,UINT,UINT,UINT,UINT);
GradeDraw realGradeDraw=nullptr;unsigned gradeDrawCalls=0;
HRESULT WINAPI observeGradeDraw(IDirect3DDevice9* device,D3DPRIMITIVETYPE type,INT base,UINT first,UINT count,UINT start,UINT primitives){
    ++gradeDrawCalls;return realGradeDraw(device,type,base,first,count,start,primitives);
}
struct GradeDrawHook {
    void** slot;
    GradeDrawHook(IDirect3DDevice9* device){slot=*reinterpret_cast<void***>(device)+82;realGradeDraw=reinterpret_cast<GradeDraw>(*slot);DWORD old;require(VirtualProtect(slot,sizeof(void*),PAGE_READWRITE,&old)!=0,"Own device observation");*slot=reinterpret_cast<void*>(&observeGradeDraw);VirtualProtect(slot,sizeof(void*),old,&old);}
    ~GradeDrawHook(){DWORD old;if(VirtualProtect(slot,sizeof(void*),PAGE_READWRITE,&old)){*slot=reinterpret_cast<void*>(realGradeDraw);VirtualProtect(slot,sizeof(void*),old,&old);}}
};
template<class T>void setExpected(std::array<unsigned char,526>& bytes,unsigned offset,T value){std::memcpy(bytes.data()+offset,&value,sizeof value);}
DWORD renderGrade(IDirect3DDevice9* d,D3DRENDERSTATETYPE key){DWORD value=0;require(SUCCEEDED(d->GetRenderState(key,&value)),"Read real render state");return value;}
DWORD stageGrade(IDirect3DDevice9* d,D3DTEXTURESTAGESTATETYPE key){DWORD value=0;require(SUCCEEDED(d->GetTextureStageState(0,key,&value)),"Read real stage state");return value;}
void verifyTextureGrade(IDirect3DDevice9* d,IDirect3DTexture9* expected){IDirect3DBaseTexture9* actual=nullptr;require(SUCCEEDED(d->GetTexture(0,&actual))&&actual==expected,"Actual selected grade texture");if(actual)actual->Release();}
std::vector<DWORD> pixelsGrade(IDirect3DDevice9* device,const char* filename){
    IDirect3DSurface9* surface=nullptr;require(SUCCEEDED(device->GetRenderTarget(0,&surface)),"Actual model surface");D3DSURFACE_DESC desc={};require(SUCCEEDED(surface->GetDesc(&desc))&&(desc.Format==D3DFMT_X8R8G8B8||desc.Format==D3DFMT_A8R8G8B8),"32bit actual surface");
    IDirect3DSurface9* cpu=nullptr;require(SUCCEEDED(device->CreateOffscreenPlainSurface(desc.Width,desc.Height,desc.Format,D3DPOOL_SYSTEMMEM,&cpu,nullptr))&&SUCCEEDED(device->GetRenderTargetData(surface,cpu)),"Actual GPU readback");
    D3DLOCKED_RECT lock;require(SUCCEEDED(cpu->LockRect(&lock,nullptr,D3DLOCK_READONLY)),"Actual pixels");std::vector<DWORD> pixels(desc.Width*desc.Height);
    for(unsigned y=0;y<desc.Height;++y)std::memcpy(pixels.data()+y*desc.Width,static_cast<const unsigned char*>(lock.pBits)+y*lock.Pitch,desc.Width*4);cpu->UnlockRect();cpu->Release();
    using Save=HRESULT(WINAPI*)(LPCSTR,D3DXIMAGE_FILEFORMAT,LPDIRECT3DSURFACE9,const PALETTEENTRY*,const RECT*);
    auto save=reinterpret_cast<Save>(GetProcAddress(GetModuleHandleW(L"d3dx9_36.dll"),"D3DXSaveSurfaceToFileA"));require(save&&SUCCEEDED(save(filename,D3DXIFF_PNG,surface,nullptr,nullptr)),"Actual model frame capture");surface->Release();return pixels;
}
void writeGrade(const std::string& value){FILE* f=std::fopen("Chef/GradeEffect/Bgrade.mst","wb");require(f,"Private grade fixture");require(std::fwrite(value.data(),1,value.size(),f)==value.size(),"Private fixture write");std::fclose(f);RF455_GetCharacterRfsCache()->RemoveLooseBytes("Chef/GradeEffect/Bgrade.mst");}
int runGrade(){
    SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    require(RF455_InitializeNationPaths()&&RF455_InitializeLanguageData(),"Nation/language");InitR3Engine();
    auto* state=GetR3State();state->mScreenXsize=640;state->mScreenYsize=480;state->mbFullScreen=FALSE;ForceFullScreen();
    require(SUCCEEDED(g_MainApp.InitR3D3D(GetModuleHandleA(nullptr),0)),"Own actual D3D");
    require(_CreateCharIF(GetD3dDevice()),"Actual Character shader owner");
    RF455_RpkGroup archive;archive.LoadDirectory("grade-archive-flag\\");require(archive.count==1,"One private archive fixture");RF455_SetResourceGroup(&archive);
    for(int enabled:{1,0,17}){RF455_SetResourceArchiveEnabled(enabled);require(RF455_GetResourceArchiveEnabled()==enabled&&RF455_GetResourceGroup()==&archive,"Archive flag independentofloadedgroup");char path[]="grade-archive-flag\\dir\\a.spt";FILE* f=RF455_OpenResource(path,"rb");require(f&&std::fgetc(f)==(enabled?'o':'L'),"Actual archive/loose fallback");std::fclose(f);char exclusive[]="grade-archive-flag\\dir\\b.spt";require(RF455_ResourceExists(exclusive)==(enabled?TRUE:FALSE),"Archive-only existence is gated");}
    RF455_SetResourceGroup(nullptr);archive.Release();RF455_SetResourceArchiveEnabled(TRUE);
    auto& grades=RF455_GradeOverlays455();require(grades.Load455()&&!RF455_GetResourceArchiveEnabled(),"Four shipped grade materials andtarget archive disable");
    auto* device=GetD3dDevice();std::array<std::array<unsigned char,526>,4> frozen{};
    for(unsigned i=0;i<4;++i){auto& e=frozen[i];setExpected<DWORD>(e,154,3);setExpected<DWORD>(e,158,i==1?0x64ffffff:0xffffffff);
        setExpected<DWORD>(e,162,i==1?0x401:i==0?0x4b0:0xcf0);setExpected<SHORT>(e,184,i==1?512:768);setExpected<WORD>(e,186,i==1?0x1fe:255);
        if(i!=1){setExpected<SHORT>(e,170,256);setExpected<SHORT>(e,172,256);setExpected<SHORT>(e,176,128);setExpected<SHORT>(e,178,256);setExpected<SHORT>(e,180,i?256:512);}
        if(i>1){setExpected<SHORT>(e,174,256);setExpected<SHORT>(e,188,1536);setExpected<SHORT>(e,190,2560);}
        require(!std::memcmp(&grades.Material455(i),e.data(),526),"All526material bytes match independent frozen input");
        auto* texture=grades.Texture455(i);require(texture,"Actual shipped GPU texture");D3DSURFACE_DESC desc={};require(SUCCEEDED(texture->GetLevelDesc(0,&desc))&&desc.Width&&desc.Height,"Actual grade surface");
    }
    const float previousTime=GetMultiLayerTime();SetMultiLayerTime(1);unsigned starts=0,visiblePixels=0,changedPixels=0;
    for(BYTE grade:{BYTE(1),BYTE(2),BYTE(3),BYTE(4),BYTE(255)}){
        grades.Begin455(grade);++starts;verifyTextureGrade(device,grades.Texture455(grade>4?3:grade-1));
        require(renderGrade(device,D3DRS_ZWRITEENABLE)==FALSE&&renderGrade(device,D3DRS_ALPHABLENDENABLE)==TRUE,"Actual begin state");
        require(renderGrade(device,D3DRS_SRCBLEND)==D3DBLEND_SRCALPHA&&renderGrade(device,D3DRS_DESTBLEND)==D3DBLEND_ONE,"Grade blend type3");
        IDirect3DVertexShader9* shader=nullptr;require(SUCCEEDED(device->GetVertexShader(&shader))&&shader,"Real grade vertex shader bound");shader->Release();
        float uv[16];require(SUCCEEDED(device->GetVertexShaderConstantF(92,uv,4)),"Actual UV shader constants92");
        if(grade==2)for(unsigned i=0;i<16;++i)require(uv[i]==(i%5?0.0f:1.0f),"Environment overlay uploads identity");
        grades.End455();require(renderGrade(device,D3DRS_ZWRITEENABLE)==TRUE&&renderGrade(device,D3DRS_SPECULARENABLE)==TRUE,"Recovered finish state");
        require(renderGrade(device,D3DRS_ALPHABLENDENABLE)==FALSE&&renderGrade(device,D3DRS_ALPHATESTENABLE)==FALSE&&stageGrade(device,D3DTSS_TEXCOORDINDEX)==0&&stageGrade(device,D3DTSS_TEXTURETRANSFORMFLAGS)==0,"Finish is exact state set");
    }
    float sentinel[16];for(unsigned i=0;i<16;++i)sentinel[i]=float(i+10);device->SetVertexShaderConstantF(92,sentinel,4);grades.Begin455(0);
    float unchanged[16];device->GetVertexShaderConstantF(92,unchanged,4);require(!std::memcmp(unchanged,sentinel,64),"Grade0leaves constants unchanged");
    grades.Release455();for(unsigned i=0;i<4;++i)require(!grades.Texture455(i)&&!std::memcmp(&grades.Material455(i),frozen[i].data(),526),"Release zeros textures but preserves materials");
    require(grades.Load455()&&_CreateBoneMgr()&&_CreateMeshMgr()&&_CreateAnimationMgr()&&_CreateBoundBoxMgr(),"Real model owners");
    require(RF455_GameItems().loadItemFiles(),"Real Item47metadata for model selection");
    {
        CCharResDataMgr catalog;require(catalog.LoadData(),"Real resource catalog");
        FILE* expected=std::fopen("expected.bin","rb");require(expected,"Real model fixture");char signature[4];require(std::fread(signature,1,4,expected)==4&&!std::memcmp(signature,"EQ45",4),"Expected model fixture signature");
        const unsigned planCount=word(expected);require(std::fseek(expected,long(planCount*sizeof(PlanCase)),SEEK_CUR)==0,"Skip selection plans");
        const unsigned caseCount=word(expected);std::vector<RealCase> models(caseCount);require(std::fread(models.data(),sizeof(RealCase),caseCount,expected)==caseCount,"Real model cases");std::fclose(expected);
        const RealCase* selected=nullptr;for(const auto& value:models)if(value.type==1&&value.race==0){selected=&value;break;}require(selected,"Selected actual Bellato equipment model");
        RF455EquipmentObject equipment;require(equipment.Create455(BYTE(selected->type),selected->index),"Real equipment creation");auto* model=equipment.GetMesh455();require(model&&model->m_Load&&model->m_MaxObj==selected->parts,"Actual loaded model");
        _GetCharIF()->InitEffect(model);D3DXMATRIX identity;D3DXMatrixIdentity(&identity);
        for(unsigned node=0;node<model->m_MaxObj;++node){model->m_pMesh[node].m_MatResult=identity;for(unsigned p=0;p<model->m_pMesh[node].m_BlendNum;++p)model->m_pMesh[node].m_pMatBlend[p]=identity;}
        //A controlled pose/camera isolates the real geometry draw from the still
        //unconnected ordinary player animation/state pipeline.
        D3DXMATRIX view,projection;D3DXVECTOR3 eye(0,5,-25),at(0,5,0),up(0,1,0);D3DXMatrixLookAtLH(&view,&eye,&at,&up);D3DXMatrixPerspectiveFovLH(&projection,.78539816f,640.0f/480.0f,.1f,500);
        state->mMatView=view;state->mMatProj=projection;D3DXMatrixMultiply(&state->mMatViewProj,&view,&projection);device->SetTransform(D3DTS_VIEW,&view);device->SetTransform(D3DTS_PROJECTION,&projection);
        model->m_Material.Diffuse.r=model->m_Material.Diffuse.g=model->m_Material.Diffuse.b=model->m_Material.Diffuse.a=1;
        model->m_Material.Ambient.r=model->m_Material.Ambient.g=model->m_Material.Ambient.b=model->m_Material.Ambient.a=1;
        D3DLIGHT9 light={};light.Type=D3DLIGHT_DIRECTIONAL;light.Diffuse.r=light.Diffuse.g=light.Diffuse.b=light.Diffuse.a=1;light.Ambient.r=light.Ambient.g=light.Ambient.b=light.Ambient.a=1;light.Direction.z=1;
        _GetCharIF()->SetLight(light);_GetCharIF()->SetState();
        Vector3f position={0,0,0};GradeDrawHook observe(device);
        require(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff101010,1,0))&&SUCCEEDED(device->BeginScene()),"Actual model frame");
        _GetCharIF()->DrawCharacter(model,position,0,1,0,false);require(SUCCEEDED(device->EndScene()),"Primary pass completed");
        const auto primary=pixelsGrade(device,"grade-model-base.png");require(SUCCEEDED(device->BeginScene()),"Overlay pass begins without clearing primary");gradeDrawCalls=0;
        grades.Begin455(2);_GetCharIF()->DrawCharacterOverlay455(model,position,0,1,0,true);grades.End455();
        require(SUCCEEDED(device->EndScene())&&gradeDrawCalls>0,"Actual indexed geometry submission");
        IDirect3DVertexShader9* cleared=nullptr;require(SUCCEEDED(device->GetVertexShader(&cleared))&&!cleared,"Overlay geometry clears shaders");if(cleared)cleared->Release();
        const auto overlay=pixelsGrade(device,"grade-model.png");require(primary.size()==overlay.size(),"Equal actual frame dimensions");
        for(unsigned i=0;i<primary.size();++i){const DWORD rgb=primary[i]&0xffffff;if((rgb&255)>16||((rgb>>8)&255)>16||((rgb>>16)&255)>16)++visiblePixels;if(rgb!=(overlay[i]&0xffffff))++changedPixels;}
        require(visiblePixels>0&&changedPixels>0,"Actual visible model andadditional overlay contribution");
    }
    require(_DestroyBoundBoxMgr()&&_DestroyAnimationMgr()&&_DestroyMeshMgr()&&_DestroyBoneMgr(),"Model resource teardown");
    std::ifstream source("Chef/GradeEffect/Bgrade.mst",std::ios::binary);const std::string original((std::istreambuf_iterator<char>(source)),std::istreambuf_iterator<char>());source.close();
    writeGrade("layer 6 { type 5 alpha 12 color 1 2 3 map_name .\\Chef\\GradeEffect\\Bgrade.dds uv_scroll_u -.25 uv_scroll_v .5 uv_lava 1 uv_lava_wave 2 uv_metal_floor 3 uv_metal_wall 4 uv_gradient_alpha_u -1 uv_gradient_alpha_v 2 uv_rotate -.5 uv_scale 1.5 uv_scale_start .25 uv_scale_end 2 uv_scale_speed 3 ani_alpha_flicker .5 ani_alpha_flicker_start .25 ani_alpha_flicker_end .75 ani_tex_frame 4 ani_tex_speed 2 uv_env 0 tex_clamp zwrite bump_env } end");
    require(grades.Load455(),"Private complete command fixture onlayer6");std::array<unsigned char,526> other{};const unsigned b=148+6*54;
    setExpected<DWORD>(other,b+6,0x2005);setExpected<DWORD>(other,b+10,0x0c010203);setExpected<DWORD>(other,b+14,0x18fff);
    for(const auto& pair:std::array<std::pair<unsigned,SHORT>,14>{{{18,512},{20,256},{22,-64},{24,128},{26,-128},{28,64},{30,512},{32,768},{34,1024},{36,128},{38,SHORT(0x3fbf)},{40,1024},{42,512},{44,SHORT(0x4b96)}}})setExpected<SHORT>(other,b+pair.first,pair.second);
    require(!std::memcmp(&grades.Material455(0),other.data(),526),"Full independent layer6 parser oracle");
    for(const char* malformed:{"layer 7 { }","layer -1 { }","layer 0 { uv_scroll_u"}){writeGrade(malformed);require(!grades.Load455(),"Bounded malformed material rejection");}
    writeGrade(original);require(grades.Load455(),"Restore actual immutable input bytes from privatecopy");grades.Release455();SetMultiLayerTime(previousTime);
    require(_DestroyCharIF(),"Character teardown");g_MainApp.ReleaseR3D3D();ReleaseR3Engine();
    FILE* out=std::fopen("result.json","wb");require(out,"Result");std::fprintf(out,"{\"status\":\"PASS\",\"real_materials\":4,\"real_GPU_textures\":4,\"all_material_bytes\":2104,\"actual_overlay_starts\":%u,\"actual_overlay_geometry_draws\":%u,\"visible_model_pixels\":%u,\"changed_overlay_pixels\":%u,\"archive_flag_fallback_cases\":3,\"real_equipment_model\":true,\"controlled_pose\":true,\"grade0_noop\":true,\"grade255_clamps_last\":true,\"actual_shader_constants92\":true,\"private_layer6_oracle\":true,\"malformed_cases\":3,\"actual_release\":true,\"full_equipment_draw\":false}\n",starts,gradeDrawCalls,visiblePixels,changedPixels);std::fclose(out);return 0;
}
}
#ifndef RF455_GRADE_OVERLAY_NO_MAIN
int main(){try{return runGrade();}catch(const std::exception& e){std::fprintf(stderr,"Grade overlay:%s\n",e.what());return 2;}}
#endif
