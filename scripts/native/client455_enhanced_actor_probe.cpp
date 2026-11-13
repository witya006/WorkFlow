// Reuse the existing real model loader fixture helpers, not its old-size tests.
#define RF455_DRAW_EMBEDDED
#include "test_client455_draw.cpp"
#include "client455_character_draw.h"
#include "client455_enhanced_lighting.h"
#include <stdexcept>

namespace enhancedActor {
using SaveSurface=HRESULT(WINAPI*)(LPCSTR,int,IDirect3DSurface9*,const PALETTEENTRY*,const RECT*);
void require(bool value,const char* why){if(!value)throw std::runtime_error(why);}
unsigned WINAPI fixedTicks(){return 7000;}
void __cdecl sineFloat(float* out,const float* value){*out=static_cast<float>(std::sin(*value));}
void __cdecl cosineFloat(float* out,const float* value){*out=static_cast<float>(std::cos(*value));}
struct Observation {
    IDirect3DDevice9* device;RF455ShaderManager* shaders;RF455MeshStorage* first;
    std::vector<unsigned> programs,parts;unsigned enhanced=0;bool bindings=true;
    static void __cdecl draw(void* raw,const RF455MeshStorage* mesh,unsigned index){
        auto& self=*static_cast<Observation*>(raw);self.programs.push_back(index);
        self.parts.push_back(static_cast<unsigned>(mesh-self.first));self.enhanced+=index>=12&&index<15;
        IDirect3DVertexShader9* vertex=nullptr;IDirect3DPixelShader9* pixel=nullptr;
        self.device->GetVertexShader(&vertex);self.device->GetPixelShader(&pixel);
        self.bindings=self.bindings&&index<self.shaders->count&&vertex==self.shaders->programs[index].vertex&&pixel==self.shaders->programs[index].pixel;
        if(vertex)vertex->Release();if(pixel)pixel->Release();
    }
    void clear(){programs.clear();parts.clear();enhanced=0;bindings=true;}
};
std::vector<unsigned char> frame(IDirect3DDevice9* device,SaveSurface save,const char* name){
    IDirect3DSurface9* target=nullptr;require(SUCCEEDED(device->GetRenderTarget(0,&target)),"target");
    D3DSURFACE_DESC desc{};target->GetDesc(&desc);require(desc.Width==1920&&desc.Height==1080,"actual Full HD");
    const HRESULT saved=save(name,3,target,nullptr,nullptr);target->Release();require(SUCCEEDED(saved),"save PNG");
    auto data=capture(device);require(data.size()==1920*1080*4,"full actor readback");return data;
}
unsigned changedPixels(const std::vector<unsigned char>& left,const std::vector<unsigned char>& right){
    require(left.size()==right.size(),"same frame shape");unsigned changed=0;
    for(std::size_t i=0;i<left.size();i+=4)changed+=std::memcmp(left.data()+i,right.data()+i,3)!=0;
    return changed;
}
unsigned occupiedPixels(const std::vector<unsigned char>& image){
    unsigned count=0;for(std::size_t i=0;i<image.size();i+=4)count+=(get<DWORD>(image.data(),unsigned(i))&0xffffff)!=0x101820;return count;
}
void writeObservation(FILE* file,const char* name,const Observation& observation){
    std::fprintf(file,"\"%s\":{\"draws\":%u,\"enhanced\":%u,\"bound_programs_match\":%s,\"programs\":[",name,
        unsigned(observation.programs.size()),observation.enhanced,observation.bindings?"true":"false");
    for(unsigned i=0;i<observation.programs.size();++i)std::fprintf(file,"%s%u",i?",":"",observation.programs[i]);
    std::fprintf(file,"]}");
}
void actor(const char* fixture,IDirect3DDevice9* device,RF455ShaderManager& shaders,
    IDirect3DVertexDeclaration9* d36,IDirect3DVertexDeclaration9* d64,RF455PoseMath math,
    RF455CharacterDrawMath drawing,SaveSurface save){
    FILE* input=std::fopen(fixture,"rb");require(input!=nullptr,"fixture");char paths[3][512];
    for(auto& path:paths){require(std::fgets(path,sizeof(path),input)!=nullptr,"fixture paths");path[std::strcspn(path,"\r\n")]=0;}std::fclose(input);
    Scene scene(device);Memory memory;const auto ops=memory.ops();unsigned imported=0;
    RF455LegacyDiagnostics log={nullptr,diagnostic,diagnosticWide};
    RF455CharacterLoadContext load={{{ops.memory,math.matrix,&scene.textures,&scene.v64,&scene.indices,&scene.meshes,&scene.buffers},&scene.v36,4,&scene.scratch,log},{ops,log,&imported}};
    RF455CharacterStorage root,child;RF455_ConstructCharacter(&root);RF455_ConstructCharacter(&child);
    std::strcpy(reinterpret_cast<char*>(root.prefix.bytes+4),paths[1]);std::strcpy(reinterpret_cast<char*>(child.prefix.bytes+4),paths[0]);
    for(auto* model:{&root,&child})std::strcpy(reinterpret_cast<char*>(model->prefix.bytes+276),".\\tex");
    put(child.prefix.bytes,272,&root.prefix);
    require(RF455_LoadCharacter(&root,0,&load)&&RF455_LoadCharacter(&child,0,&load),"production model loading");
    RF455_RefreshModelTextures(&child.prefix,&scene.textures);
    RF455AnimationStorage animation;RF455_ConstructAnimation(&animation);std::strcpy(reinterpret_cast<char*>(animation.bytes+5),paths[2]);
    require(RF455_MatchAnimation(&animation,&root,&load)!=0,"production animation match");
    Owners owner={{get<const unsigned char*>(animation.bytes,268),Memory::extent(&memory,get<const unsigned char*>(animation.bytes,268))}};
    RF455PoseScratch scratch{};RF455PoseContext pose={&load,math,&scratch,150,&owner,Owners::resolve};
    auto setPose=[&](unsigned value){put(root.prefix.bytes,672,value);put(child.prefix.bytes,672,value);
        require(RF455_UpdateCharacterPose(&root,&pose)==RF_POSE_OK&&RF455_UpdateCharacterPose(&child,&pose)==RF_POSE_OK,"production pose update");};
    setPose(160);
    auto* meshes=get<RF455MeshStorage*>(child.prefix.bytes,536);const unsigned count=get<unsigned>(child.prefix.bytes,532);
    float low[3]={1e30f,1e30f,1e30f},high[3]={-1e30f,-1e30f,-1e30f};unsigned geometry=0;
    FILE* details=std::fopen("parts.json","wb");require(details!=nullptr,"parts record");std::fprintf(details,"[");
    for(unsigned part=0;part<count;++part){auto* mesh=meshes[part].bytes;const unsigned vertices=get<unsigned>(mesh,5086);if(!vertices)continue;
        std::fprintf(details,"%s{\"part\":%u,\"vertices\":%u,\"bones\":%u,\"lighting\":%u,\"effect\":%u,\"second_effect\":%u,\"second_pass\":%u,\"alpha\":%.9g,\"normal_map\":%s,\"specular_map\":%s,\"secondary_texture\":%s}",geometry?",":"",part,vertices,get<unsigned>(mesh,522),get<unsigned>(mesh,5359),get<unsigned>(mesh,5363),get<unsigned>(mesh,5367),get<unsigned>(mesh,5351),get<float>(mesh,5131),get<void*>(mesh,5791)?"true":"false",get<void*>(mesh,5795)?"true":"false",get<void*>(mesh,5115)?"true":"false");++geometry;
        const unsigned address=get<unsigned>(mesh,4494);auto* buffer=scene.v64.buffers[address/RF455_VERTEX_BLOCK_BYTES];void* data=nullptr;
        require(buffer&&SUCCEEDED(buffer->Lock(address%RF455_VERTEX_BLOCK_BYTES,64*vertices,&data,D3DLOCK_READONLY)),"real shared model vertices");
        for(unsigned k=0;k<vertices;++k){const auto* vertex=static_cast<const unsigned char*>(data)+64*k;
            float weights[]={get<float>(vertex,12),get<float>(vertex,16),get<float>(vertex,20),0};weights[3]=1-weights[0]-weights[1]-weights[2];float p[3]{};
            for(unsigned bone=0;bone<4;++bone){const unsigned slot=get<unsigned short>(vertex,24+2*bone);
                require(slot<(std::max)(4u,get<unsigned>(mesh,522)),"bone index");const auto* matrix=mesh+(get<unsigned>(mesh,522)?646+64*slot:4830);
                for(unsigned axis=0;axis<3;++axis){float value=get<float>(matrix,48+4*axis);
                    for(unsigned component=0;component<3;++component)value+=get<float>(vertex,4*component)*get<float>(matrix,16*component+4*axis);p[axis]+=value*weights[bone];}}
            for(unsigned axis=0;axis<3;++axis){low[axis]=(std::min)(low[axis],p[axis]);high[axis]=(std::max)(high[axis],p[axis]);}}
        buffer->Unlock();
    }
    std::fprintf(details,"]\n");std::fclose(details);require(geometry>0,"loaded drawable model");
    // Uniform scale + right-handed model Z-up to world Y-up rotation; perspective
    // handles depth. Unlike the old fixture, depth is never flattened into clip Z.
    float world[16];unit(world);const float scale=2/(high[2]-low[2]);
    // Face the camera after the axis conversion; extra distance keeps the
    // animated weapon and wings inside the Full HD frame in both sampled poses.
    world[0]=-scale;world[5]=world[10]=0;world[6]=scale;world[9]=scale;
    world[12]=.5f*(low[0]+high[0])*scale;world[13]=-.5f*(low[2]+high[2])*scale;world[14]=-.5f*(low[1]+high[1])*scale;
    float view[16];unit(view);view[14]=5;
    float projection[16]{};const float y=1/std::tan(.6f/2);projection[0]=y/(1920.f/1080);projection[5]=y;
    projection[10]=100.f/99.9f;projection[11]=1;projection[14]=-10.f/99.9f;
    float light[26]{};light[16]=-.35f;light[17]=-.6f;light[18]=1;
    const float material[17]={.55f,.53f,.50f,1,.22f,.23f,.25f,1,.15f,.15f,.15f,1,0,0,0,0,24};
    std::memcpy(child.prefix.bytes+720,material,sizeof(material));
    RF455CharacterDrawGlobals globals{};RF455CharacterTransparency transparent;RF455_ResetCharacterTransparency(&transparent);std::memcpy(transparent.sortView,view,64);
    RF455CharacterDrawContext context{};context.state={device,4,d36,d64,light,0};context.shaders=&shaders;
    context.vertices36=&scene.v36;context.vertices64=&scene.v64;context.indices=&scene.indices;context.math=drawing;context.globals=&globals;
    context.transparent=&transparent;context.memory=ops.memory;context.projection=projection;context.view=view;
    Observation observation{device,&shaders,meshes};context.observer=&observation;context.beforeDraw=Observation::draw;
    auto render=[&](bool enhanced,const char* filename){require(RF455_SetEnhancedActorLightingEnabled(enhanced),"mode switch");RF455_SetEnhancedActorLightingProtected(false);
        observation.clear();RF455_SetCharacterDrawState(&context.state);device->SetRenderState(D3DRS_ZWRITEENABLE,TRUE);
        require(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0xff101820,1,0))&&SUCCEEDED(device->BeginScene()),"frame begin");
        require(RF455_DrawCharacter455(&context,&child,world,nullptr)==RF_CHARACTER_DRAW_OK&&RF455_FlushCharacterTransparency(&context)==RF_CHARACTER_DRAW_OK,"real actor draw");
        require(SUCCEEDED(device->EndScene()),"frame end");require(observation.bindings,"actual bound shaders");return frame(device,save,filename);};
    const auto classic=render(false,"actor-classic.png");const Observation classicObs=observation;
    const auto enhanced=render(true,"actor-enhanced.png");const Observation enhancedObs=observation;
    const auto restored=render(false,"actor-classic-restored.png");const Observation restoredObs=observation;
    const unsigned changed=changedPixels(classic,enhanced),classicPixels=occupiedPixels(classic),enhancedPixels=occupiedPixels(enhanced);
    const bool exact=classic==restored;
    setPose(get<unsigned>(animation.bytes,276)/2);const auto animated=render(true,"actor-enhanced-animated.png");
    const unsigned animationChanged=changedPixels(enhanced,animated);const Observation animatedObs=observation;
    require(RF455_SetEnhancedActorLightingEnabled(false),"final classic setting");
    const bool pass=exact&&enhancedObs.enhanced>0&&changed>100&&classicPixels>1000&&enhancedPixels>1000&&animationChanged>100;
    FILE* report=std::fopen("result.json","wb");require(report!=nullptr,"report");
    std::fprintf(report,"{\"status\":\"%s\",\"resolution\":[1920,1080],\"geometry_parts\":%u,\"same_pose_frame\":160,\"animated_frame\":%u,\"classic_pixels\":%u,\"enhanced_pixels\":%u,\"changed_pixels\":%u,\"animation_changed_pixels\":%u,\"classic_restored_exactly\":%s,\"observations\":{",pass?"PASS":"FAIL",geometry,get<unsigned>(animation.bytes,276)/2,classicPixels,enhancedPixels,changed,animationChanged,exact?"true":"false");
    writeObservation(report,"classic",classicObs);std::fprintf(report,",");writeObservation(report,"enhanced",enhancedObs);std::fprintf(report,",");writeObservation(report,"restored",restoredObs);std::fprintf(report,",");writeObservation(report,"animated",animatedObs);
    std::fprintf(report,"},\"scope\":\"real model, original textures and ANI through production loading/pose/draw in a controlled perspective scene; not live world\"}\n");std::fclose(report);
    for(unsigned i=0;i<8;++i)device->SetTexture(i,nullptr);device->SetStreamSource(0,nullptr,0,0);device->SetIndices(nullptr);
    RF455_ReleaseModelMeshArray(&child.prefix,&ops.memory);RF455_ReleaseModelMeshArray(&root.prefix,&ops.memory);RF455_DestroyAnimation(&animation,&ops.memory);
    require(memory.live.empty()&&!memory.bad,"model allocations balanced");require(pass,"real actor enhanced acceptance; see result/parts JSON");
}
int run(const char* compiler,const char* fixture){
    HMODULE provider=LoadLibraryA(compiler);require(provider!=nullptr,"D3DX");RF455PoseMath math{};RF455CharacterDrawMath drawing{};
#define LOAD(member,name) member=reinterpret_cast<decltype(member)>(GetProcAddress(provider,name));require(member!=nullptr,name)
    LOAD(math.matrix.inverse,"D3DXMatrixInverse");LOAD(math.matrix.multiply,"D3DXMatrixMultiply");LOAD(math.slerp,"D3DXQuaternionSlerp");LOAD(math.rotationQuaternion,"D3DXMatrixRotationQuaternion");
    RF455ShaderApi shader{};LOAD(shader.compile,"D3DXCompileShader");LOAD(shader.sprite,"D3DXCreateSprite");
    RF455CharacterTextureApi textures{};LOAD(textures.memory2D,"D3DXCreateTextureFromFileInMemoryEx");LOAD(textures.memoryCube,"D3DXCreateCubeTextureFromFileInMemoryEx");LOAD(textures.file2D,"D3DXCreateTextureFromFileA");
    drawing.matrix=math.matrix;LOAD(drawing.transform3,"D3DXVec3Transform");LOAD(drawing.ortho,"D3DXMatrixOrthoLH");drawing.ticks=fixedTicks;drawing.sineFloat=sineFloat;drawing.cosineFloat=cosineFloat;
    SaveSurface save=nullptr;LOAD(save,"D3DXSaveSurfaceToFileA");
#undef LOAD
    HWND window=CreateWindowExA(0,"STATIC","RF455 real actor lighting",WS_POPUP,0,0,1920,1080,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);
    require(window&&!IsWindowVisible(window),"hidden Full HD window");IDirect3D9* api=Direct3DCreate9(D3D_SDK_VERSION);require(api!=nullptr,"D3D9");
    D3DPRESENT_PARAMETERS pp{};pp.Windowed=TRUE;pp.hDeviceWindow=window;pp.BackBufferWidth=1920;pp.BackBufferHeight=1080;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.EnableAutoDepthStencil=TRUE;pp.AutoDepthStencilFormat=D3DFMT_D16;
    IDirect3DDevice9* device=nullptr;require(SUCCEEDED(api->CreateDevice(0,D3DDEVTYPE_HAL,window,D3DCREATE_SOFTWARE_VERTEXPROCESSING|D3DCREATE_FPU_PRESERVE,&pp,&device)),"hardware device");
    RF455ShaderManager shaders;RF455_ConstructShaderManager(&shaders);shaders.device=device;IUnknown* sprite=nullptr;IDirect3DVertexDeclaration9* d64=nullptr,*d36=nullptr;
    require(RF455_InitializeCharacterShaders(&shaders,&shader,&sprite,&d64,&d36)==11,"original shader inputs");RF455_InitializeEnhancedActorLighting(&shaders,&shader);require(RF455_EnhancedActorLightingAvailable(),"enhanced programs");
    auto* oldTextures=RF455_SetCharacterTextureApi(&textures);RF455CharacterRfsCache cache;auto* oldCache=RF455_SetCharacterRfsCache(&cache);
    actor(fixture,device,shaders,d36,d64,math,drawing,save);
    device->SetVertexShader(nullptr);device->SetPixelShader(nullptr);device->SetVertexDeclaration(nullptr);RF455_ReleaseShaderManager(&shaders);RF455_ReleaseCharacterDeclarations(&d64,&d36);sprite->Release();
    RF455_SetCharacterTextureApi(oldTextures);RF455_SetCharacterRfsCache(oldCache);require(!device->Release()&&!api->Release(),"device ownership balanced");DestroyWindow(window);FreeLibrary(provider);return 0;
}
}
int main(int argc,char** argv){SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX|SEM_NOOPENFILEERRORBOX);
    try{enhancedActor::require(argc==3,"compiler and fixture required");return enhancedActor::run(argv[1],argv[2]);}
    catch(const std::exception& error){std::fprintf(stderr,"Real actor lighting: %s\n",error.what());return 1;}}
