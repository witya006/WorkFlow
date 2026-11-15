#include "client455_texture.h"
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

static unsigned textureChecks,profileCases,realGpuCases,renderCases,materialParts,materialHits,orphanCases;
#define TX_CHECK(x) do{++textureChecks;if(!(x)){std::fprintf(stderr,"texture check%u line%d\n",textureChecks,__LINE__);return 1;}}while(0)
static std::uint32_t txHash(const unsigned char* p,std::size_t n){std::uint32_t value=2166136261u;for(std::size_t i=0;i<n;++i)value=(value^p[i])*16777619u;return value;}
static bool txFile(const char* path,std::vector<unsigned char>& bytes){
    FILE* f=std::fopen(path,"rb");if(!f)return false;if(std::fseek(f,0,SEEK_END)){std::fclose(f);return false;}const long size=std::ftell(f);
    if(size<0 || std::fseek(f,0,SEEK_SET)){std::fclose(f);return false;}bytes.resize(static_cast<std::size_t>(size));const bool ok=bytes.empty() || std::fread(bytes.data(),1,bytes.size(),f)==bytes.size();return std::fclose(f)==0 && ok;
}
static bool txWrite(const char* path,const void* bytes,std::size_t size){FILE* f=std::fopen(path,"wb");if(!f)return false;const bool ok=!size || std::fwrite(bytes,1,size,f)==size;return std::fclose(f)==0 && ok;}
static bool txCopy(const char* input,const char* output){std::vector<unsigned char> bytes;return txFile(input,bytes) && txWrite(output,bytes.data(),bytes.size());}
static bool txResource(const char* path,std::vector<unsigned char>& bytes){
    std::uint32_t size=0;FILE* f=RF455_GetCharacterRfsCache()->Open(path,&size);
    if(!f)return txFile(path,bytes);bytes.resize(size);const bool ok=!size || std::fread(bytes.data(),1,size,f)==size;return std::fclose(f)==0 && ok;
}
struct TXReader {
    const std::vector<unsigned char>& bytes;std::size_t at=0;bool ok=true;
    std::uint32_t number(unsigned size=4){if(size>bytes.size()-at){ok=false;return 0;}std::uint32_t value=0;for(unsigned i=0;i<size;++i)value|=static_cast<std::uint32_t>(bytes[at++])<<(8*i);return value;}
    std::string string(){const auto n=number(2);if(n>bytes.size()-at){ok=false;return {}; }std::string s(reinterpret_cast<const char*>(bytes.data()+at),n);at+=n;return s;}
    std::vector<unsigned char> blob(std::size_t size){if(size>bytes.size()-at){ok=false;return {}; }std::vector<unsigned char> out(bytes.begin()+at,bytes.begin()+at+size);at+=size;return out;}
};
struct TXProfile {unsigned lod,widthLimit,heightLimit;bool valid;RF455CharacterDds expected;};
struct TXAsset {std::string path;std::vector<unsigned char> raw;std::vector<TXProfile> profiles;};
static int txCpu(std::vector<TXAsset>& assets,RF455CharacterRfsCache& cache){
    std::vector<unsigned char> golden;TX_CHECK(txFile("golden.bin",golden));TXReader g={golden};TX_CHECK(g.number()==0x58473954 && g.number()==1);const unsigned count=g.number();TX_CHECK(count==20);
    for(unsigned n=0;n<count;++n){
        TXAsset asset;asset.path=g.string();const auto length=g.number(),digest=g.number();TX_CHECK(txResource(asset.path.c_str(),asset.raw));TX_CHECK(asset.raw.size()==length && txHash(asset.raw.data(),asset.raw.size())==digest);
        const auto profiles=g.number();TX_CHECK(profiles==4);
        for(unsigned p=0;p<profiles;++p){
            TXProfile profile;profile.lod=g.number();profile.widthLimit=g.number();profile.heightLimit=g.number();profile.valid=g.number()!=0;
            if(profile.valid){profile.expected.skipped=g.number();profile.expected.width=g.number();profile.expected.height=g.number();profile.expected.cube=g.number()!=0;const auto size=g.number();profile.expected.bytes=g.blob(size);}
            RF455CharacterDds actual;actual.width=12345;
            TX_CHECK(RF455_PrepareCharacterDds(asset.raw.data(),asset.raw.size(),profile.lod,profile.widthLimit,profile.heightLimit,&actual)==profile.valid);
            if(profile.valid){TX_CHECK(actual.bytes==profile.expected.bytes);TX_CHECK(actual.skipped==profile.expected.skipped && actual.width==profile.expected.width && actual.height==profile.expected.height && actual.cube==profile.expected.cube);}
            else TX_CHECK(actual.width==12345);
            asset.profiles.push_back(std::move(profile));++profileCases;
        }
        assets.push_back(std::move(asset));
    }
    TX_CHECK(g.ok && g.at==golden.size());TX_CHECK(cache.FileCount()==13);
    TX_CHECK(RF455CharacterRfsCache::Normalize("tex/X.DDS")==RF455CharacterRfsCache::Normalize("X.DDS"));
    TX_CHECK(RF455CharacterRfsCache::Normalize("./tex/X.DDS")!=RF455CharacterRfsCache::Normalize("X.DDS"));
    TX_CHECK(RF455CharacterRfsCache::Normalize("C:/fixed/X.DDS")=="C:\\FIXED\\X.DDS");
    RF455TextureManager manager;std::memset(&manager,0xa5,sizeof(manager));RF455_ConstructTextureManager(&manager);
    TX_CHECK(!manager.device && !manager.begin && !manager.end && !manager.capacity && !manager.estimatedBytes && manager.nextId==1 && !manager.directory[0] && !manager.mipSkip);
    TX_CHECK(RF455_LastTextureManager()==&manager && !RF455_AddTexture(&manager,".\\tex","SYNTH.DDS"));RF455_DestroyTextureManager(&manager);TX_CHECK(RF455_LastTextureManager()==&manager);
    // All these writes target the probe's fresh owned working directory.
    TX_CHECK(CreateDirectoryA("negative",nullptr)!=FALSE);cache.Clear();std::uint32_t size=0;
    TX_CHECK(!cache.Open(".\\negative\\GT_A_01.RFT",&size));TX_CHECK(cache.DirectoryCount()==1);
    TX_CHECK(txCopy("tex/GTT.RFS","negative/DATA0.RFS"));TX_CHECK(!cache.Open(".\\negative\\GT_A_01.RFT",&size));
    cache.Clear();FILE* f=cache.Open(".\\negative\\GT_A_01.RFT",&size);TX_CHECK(f && size==349680);TX_CHECK(std::fclose(f)==0);
    TX_CHECK(CreateDirectoryA("emptyinfo",nullptr)!=FALSE);TX_CHECK(txCopy("tex/GTT.RFS","emptyinfo/DATA0.RFS"));TX_CHECK(txWrite("emptyinfo/RFSINFO.DAT","",0));cache.Clear();TX_CHECK(!cache.Open(".\\emptyinfo\\GT_A_01.RFT",&size));
    TX_CHECK(CreateDirectoryA("gap",nullptr)!=FALSE);TX_CHECK(txCopy("tex/GTT.RFS","gap/DATA0.RFS"));TX_CHECK(txCopy("tex/TRT.RFS","gap/DATA2.RFS"));cache.Clear();TX_CHECK(!cache.Open(".\\gap\\COM_TRAP_000.RFT",&size));TX_CHECK(cache.FileCount()==8);
    cache.Clear();f=cache.Open(".\\duplicate\\SHARED.RFT",&size);TX_CHECK(f && size==5);char value[8]={};TX_CHECK(std::fread(value,1,size,f)==size && !std::memcmp(value,"first",5));TX_CHECK(!std::fclose(f));
    TX_CHECK(txWrite("duplicate/RFSINFO.DAT","B.RFS\nA.RFS\n",12));f=cache.Open(".\\duplicate\\SHARED.RFT",&size);TX_CHECK(f && size==5);TX_CHECK(std::fread(value,1,size,f)==size && !std::memcmp(value,"first",5));TX_CHECK(!std::fclose(f));
    cache.Clear();f=cache.Open(".\\duplicate\\SHARED.RFT",&size);TX_CHECK(f && size==6);TX_CHECK(std::fread(value,1,size,f)==size && !std::memcmp(value,"second",6));TX_CHECK(!std::fclose(f));cache.Clear();return 0;
}

// GPU tests and exported probe entry follow below. This TU includes only D3D9,
// keeping it separate from the legacy client's D3D8 translation units.
template<class T> struct TXCom {
    T* p=nullptr;~TXCom(){if(p)p->Release();}T** out(){return &p;}
};
struct TXContext {
    HMODULE dx=nullptr,d3d=nullptr;HWND window=nullptr;IDirect3D9* api=nullptr;IDirect3DDevice9* device=nullptr;
    ~TXContext(){if(device)device->Release();if(api)api->Release();if(window)DestroyWindow(window);if(d3d)FreeLibrary(d3d);if(dx)FreeLibrary(dx);}
};
static RF455CharacterTextureApi realApi;
static std::vector<IDirect3DCubeTexture9*> observedCubes;
static unsigned fileCalls,memoryCalls;
static HRESULT WINAPI txMemory(IDirect3DDevice9* d,LPCVOID b,UINT size,UINT w,UINT h,UINT levels,DWORD usage,D3DFORMAT fmt,D3DPOOL pool,DWORD filter,DWORD mipfilter,D3DCOLOR color,void* info,PALETTEENTRY* palette,IDirect3DTexture9** out){
    ++memoryCalls;return realApi.memory2D(d,b,size,w,h,levels,usage,fmt,pool,filter,mipfilter,color,info,palette,out);
}
static HRESULT WINAPI txCube(IDirect3DDevice9* d,LPCVOID b,UINT size,UINT w,UINT levels,DWORD usage,D3DFORMAT fmt,D3DPOOL pool,DWORD filter,DWORD mipfilter,D3DCOLOR color,void* info,PALETTEENTRY* palette,IDirect3DCubeTexture9** out){
    const auto hr=realApi.memoryCube(d,b,size,w,levels,usage,fmt,pool,filter,mipfilter,color,info,palette,out);
    if(SUCCEEDED(hr) && *out){(*out)->AddRef();observedCubes.push_back(*out);}return hr;
}
static HRESULT WINAPI txDisk(IDirect3DDevice9* d,LPCSTR path,IDirect3DTexture9** out){++fileCalls;return realApi.file2D(d,path,out);}
struct TXManager {
    RF455TextureManager value;TXManager(IDirect3DDevice9* device){RF455_ConstructTextureManager(&value);value.device=device;}
    ~TXManager(){RF455_DestroyTextureManager(&value);}
};
static int txCompareTextures(IDirect3DTexture9* a,IDirect3DTexture9* b){
    TX_CHECK(a->GetLevelCount()==b->GetLevelCount());
    for(UINT i=0;i<a->GetLevelCount();++i){
        D3DSURFACE_DESC da={},db={};TX_CHECK(SUCCEEDED(a->GetLevelDesc(i,&da)) && SUCCEEDED(b->GetLevelDesc(i,&db)));
        TX_CHECK(da.Format==db.Format && da.Width==db.Width && da.Height==db.Height && da.Pool==db.Pool);
        unsigned rows=da.Height,row=0;
        switch(da.Format){
        case D3DFMT_DXT1:rows=(rows+3)/4;row=((da.Width+3)/4)*8;break;
        case D3DFMT_DXT2:case D3DFMT_DXT3:case D3DFMT_DXT4:case D3DFMT_DXT5:rows=(rows+3)/4;row=((da.Width+3)/4)*16;break;
        case D3DFMT_A8R8G8B8:case D3DFMT_X8R8G8B8:row=da.Width*4;break;
        case D3DFMT_R5G6B5:case D3DFMT_A1R5G5B5:case D3DFMT_A4R4G4B4:row=da.Width*2;break;
        case D3DFMT_A8:row=da.Width;break;
        default:TX_CHECK(false);
        }
        D3DLOCKED_RECT la={},lb={};TX_CHECK(SUCCEEDED(a->LockRect(i,&la,nullptr,D3DLOCK_READONLY)));TX_CHECK(SUCCEEDED(b->LockRect(i,&lb,nullptr,D3DLOCK_READONLY)));
        bool equal=true;for(unsigned y=0;y<rows;++y)if(std::memcmp(static_cast<unsigned char*>(la.pBits)+y*la.Pitch,static_cast<unsigned char*>(lb.pBits)+y*lb.Pitch,row))equal=false;
        const auto ua=a->UnlockRect(i),ub=b->UnlockRect(i);TX_CHECK(SUCCEEDED(ua) && SUCCEEDED(ub) && equal);
    }
    return 0;
}
static int txRender(IDirect3DDevice9* device,IDirect3DTexture9* texture,std::vector<unsigned char>& rgb){
    struct V {float x,y,z,rhw;DWORD color;float u,v;};
    const V vertices[]={{-.5f,-.5f,0,1,0xffffffff,0,0},{63.5f,-.5f,0,1,0xffffffff,1,0},{-.5f,63.5f,0,1,0xffffffff,0,1},{63.5f,63.5f,0,1,0xffffffff,1,1}};
    TX_CHECK(SUCCEEDED(device->SetTexture(0,texture)));TX_CHECK(SUCCEEDED(device->SetTexture(1,nullptr)));
    TX_CHECK(SUCCEEDED(device->SetFVF(D3DFVF_XYZRHW|D3DFVF_DIFFUSE|D3DFVF_TEX1)));
    const D3DRENDERSTATETYPE states[]={D3DRS_ZENABLE,D3DRS_LIGHTING,D3DRS_ALPHABLENDENABLE,D3DRS_ALPHATESTENABLE,D3DRS_FOGENABLE,D3DRS_SRGBWRITEENABLE};
    for(auto state:states)TX_CHECK(SUCCEEDED(device->SetRenderState(state,FALSE)));
    TX_CHECK(SUCCEEDED(device->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE)));
    TX_CHECK(SUCCEEDED(device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_SELECTARG1)));TX_CHECK(SUCCEEDED(device->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE)));
    TX_CHECK(SUCCEEDED(device->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_SELECTARG1)));TX_CHECK(SUCCEEDED(device->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE)));
    TX_CHECK(SUCCEEDED(device->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_DISABLE)));
    TX_CHECK(SUCCEEDED(device->SetSamplerState(0,D3DSAMP_MINFILTER,D3DTEXF_POINT)));TX_CHECK(SUCCEEDED(device->SetSamplerState(0,D3DSAMP_MAGFILTER,D3DTEXF_POINT)));TX_CHECK(SUCCEEDED(device->SetSamplerState(0,D3DSAMP_MIPFILTER,D3DTEXF_NONE)));
    TX_CHECK(SUCCEEDED(device->SetSamplerState(0,D3DSAMP_ADDRESSU,D3DTADDRESS_CLAMP)));TX_CHECK(SUCCEEDED(device->SetSamplerState(0,D3DSAMP_ADDRESSV,D3DTADDRESS_CLAMP)));
    TX_CHECK(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0x00132739,1,0)));TX_CHECK(SUCCEEDED(device->BeginScene()));
    const auto draw=device->DrawPrimitiveUP(D3DPT_TRIANGLESTRIP,2,vertices,sizeof(V));const auto end=device->EndScene();TX_CHECK(SUCCEEDED(draw) && SUCCEEDED(end));
    TXCom<IDirect3DSurface9> target,copy;TX_CHECK(SUCCEEDED(device->GetRenderTarget(0,target.out())));
    TX_CHECK(SUCCEEDED(device->CreateOffscreenPlainSurface(64,64,D3DFMT_X8R8G8B8,D3DPOOL_SYSTEMMEM,copy.out(),nullptr)));TX_CHECK(SUCCEEDED(device->GetRenderTargetData(target.p,copy.p)));
    D3DLOCKED_RECT lock={};TX_CHECK(SUCCEEDED(copy.p->LockRect(&lock,nullptr,D3DLOCK_READONLY)));rgb.resize(64*64*3);
    for(unsigned y=0;y<64;++y)for(unsigned x=0;x<64;++x){const auto* pixel=static_cast<const unsigned char*>(lock.pBits)+y*lock.Pitch+4*x;auto* out=rgb.data()+3*(y*64+x);out[0]=pixel[2];out[1]=pixel[1];out[2]=pixel[0];}
    TX_CHECK(SUCCEEDED(copy.p->UnlockRect()));TX_CHECK(SUCCEEDED(device->SetTexture(0,nullptr)));++renderCases;return 0;
}
static int txBmp(const char* path,const std::vector<unsigned char>& rgb){
    BITMAPFILEHEADER file={};BITMAPINFOHEADER info={};file.bfType=0x4d42;file.bfOffBits=sizeof(file)+sizeof(info);file.bfSize=file.bfOffBits+64*64*3;
    info.biSize=sizeof(info);info.biWidth=64;info.biHeight=64;info.biPlanes=1;info.biBitCount=24;info.biSizeImage=64*64*3;
    std::vector<unsigned char> bytes(file.bfSize);std::memcpy(bytes.data(),&file,sizeof(file));std::memcpy(bytes.data()+sizeof(file),&info,sizeof(info));
    for(unsigned y=0;y<64;++y)for(unsigned x=0;x<64;++x){auto* out=bytes.data()+file.bfOffBits+3*((63-y)*64+x);const auto* in=rgb.data()+3*(y*64+x);out[0]=in[2];out[1]=in[1];out[2]=in[0];}
    TX_CHECK(txWrite(path,bytes.data(),bytes.size()));return 0;
}
static int txGpu(const std::vector<TXAsset>& assets,const char* dll,const char* frame){
    std::fprintf(stderr,"GPU init\n");std::fflush(stderr);
    TXContext c;c.dx=LoadLibraryA(dll);TX_CHECK(c.dx);
    realApi.memory2D=reinterpret_cast<decltype(realApi.memory2D)>(GetProcAddress(c.dx,"D3DXCreateTextureFromFileInMemoryEx"));
    realApi.memoryCube=reinterpret_cast<decltype(realApi.memoryCube)>(GetProcAddress(c.dx,"D3DXCreateCubeTextureFromFileInMemoryEx"));
    realApi.file2D=reinterpret_cast<decltype(realApi.file2D)>(GetProcAddress(c.dx,"D3DXCreateTextureFromFileA"));TX_CHECK(realApi.memory2D && realApi.memoryCube && realApi.file2D);
    RF455CharacterTextureApi api={txMemory,txCube,txDisk};const auto* old=RF455_SetCharacterTextureApi(&api);
    char system[MAX_PATH];TX_CHECK(GetSystemDirectoryA(system,MAX_PATH));const auto library=std::string(system)+"\\d3d9.dll";c.d3d=LoadLibraryA(library.c_str());TX_CHECK(c.d3d);
    auto create=reinterpret_cast<IDirect3D9* (WINAPI*)(UINT)>(GetProcAddress(c.d3d,"Direct3DCreate9"));TX_CHECK(create);c.api=create(D3D_SDK_VERSION);TX_CHECK(c.api);
    c.window=CreateWindowExA(0,"STATIC","RF455 owned texture probe",WS_OVERLAPPEDWINDOW,0,0,64,64,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);TX_CHECK(c.window);
    D3DPRESENT_PARAMETERS pp={};pp.BackBufferWidth=pp.BackBufferHeight=64;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.Windowed=TRUE;pp.hDeviceWindow=c.window;
    TX_CHECK(SUCCEEDED(c.api->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,c.window,D3DCREATE_SOFTWARE_VERTEXPROCESSING,&pp,&c.device)));
    for(const auto& asset:assets)for(const auto& profile:asset.profiles){
        if(!profile.valid || profile.expected.cube)continue;
        std::fprintf(stderr,"GPU %s lod%u\n",asset.path.c_str(),profile.lod);std::fflush(stderr);
        TXCom<IDirect3DTexture9> expected,actual;const auto& prepared=profile.expected;
        const auto hr=realApi.memory2D(c.device,prepared.bytes.data(),static_cast<UINT>(prepared.bytes.size()),prepared.width,prepared.height,0,0,D3DFMT_UNKNOWN,D3DPOOL_MANAGED,0xffffffff,0xffffffff,0,nullptr,nullptr,expected.out());
        std::uint32_t cube=777;actual.p=RF455_LoadCharacterTextureFile(c.device,asset.path.c_str(),profile.lod,false,profile.widthLimit,profile.heightLimit,&cube);
        TX_CHECK(cube==0 && (actual.p!=nullptr)==SUCCEEDED(hr));
        if(actual.p){TX_CHECK(txCompareTextures(expected.p,actual.p)==0);std::vector<unsigned char> a,b;TX_CHECK(txRender(c.device,expected.p,a)==0 && txRender(c.device,actual.p,b)==0);TX_CHECK(a==b);++realGpuCases;}
    }
    std::fprintf(stderr,"GPU cube\n");std::fflush(stderr);
    std::uint32_t cube=777;TX_CHECK(!RF455_LoadCharacterTextureFile(c.device,".\\tex\\CUBE.DDS",0,false,2048,2048,&cube) && cube==1);TX_CHECK(observedCubes.size()==1);
    const auto refs=observedCubes.back()->Release();observedCubes.clear();TX_CHECK(refs==0);++orphanCases;
    cube=777;TX_CHECK(!RF455_LoadCharacterTextureFile(c.device,".\\tex\\ABSENT.DDS",0,false,2048,2048,&cube) && cube==777);
    TX_CHECK(txWrite("tex/EMPTY.DDS","",0));TX_CHECK(!RF455_LoadCharacterTextureFile(c.device,".\\tex\\EMPTY.DDS",0,false,2048,2048,&cube) && cube==777);
    {
        TXManager owned(c.device);TX_CHECK(RF455_AddTexture(&owned.value,".\\tex","SYNTH.MISSING"));
        TXCom<IDirect3DTexture9> expected;std::vector<unsigned char> bytes;TX_CHECK(txFile("tex/SYNTH.RFC",bytes));RF455CharacterDds prepared;TX_CHECK(RF455_PrepareCharacterDds(bytes.data(),bytes.size(),0,2048,2048,&prepared));
        TX_CHECK(SUCCEEDED(realApi.memory2D(c.device,prepared.bytes.data(),static_cast<UINT>(prepared.bytes.size()),prepared.width,prepared.height,1,0,D3DFMT_UNKNOWN,D3DPOOL_MANAGED,0xffffffff,0xffffffff,0xffffffff,nullptr,nullptr,expected.out())));
        TX_CHECK(RF455_GetTextureById(&owned.value,1)->GetLevelCount()==1);TX_CHECK(txCompareTextures(expected.p,RF455_GetTextureById(&owned.value,1))==0);TX_CHECK(!owned.value.begin[0]->flags);
    }
    {
        TXManager owned(c.device);auto& m=owned.value;const auto account=RF455_GetTextureAccounting();
        std::fprintf(stderr,"GPU manager\n");std::fflush(stderr);
        const auto priorFileCalls=fileCalls,priorMemoryCalls=memoryCalls;
        TX_CHECK(RF455_AddTexture(&m,".\\tex","CHECKER.BMP"));TX_CHECK(fileCalls==priorFileCalls && memoryCalls==priorMemoryCalls+1);TX_CHECK(m.nextId==2 && m.estimatedBytes==16 && m.end-m.begin==1);
        TXCom<IDirect3DTexture9> direct;TX_CHECK(SUCCEEDED(realApi.file2D(c.device,".\\tex\\CHECKER.BMP",direct.out())));TX_CHECK(txCompareTextures(direct.p,RF455_GetTextureById(&m,1))==0);
        std::vector<unsigned char> image;TX_CHECK(txRender(c.device,RF455_GetTextureById(&m,1),image)==0);
        const unsigned positions[]={16*64+16,16*64+48,48*64+16,48*64+48};const unsigned char colors[4][3]={{255,0,0},{0,255,0},{0,0,255},{255,255,255}};
        for(unsigned i=0;i<4;++i)TX_CHECK(!std::memcmp(image.data()+3*positions[i],colors[i],3));TX_CHECK(txBmp(frame,image)==0);
        RF455_ClearTextureManager(&m);TX_CHECK(m.begin==m.end && m.capacity-m.begin==1 && m.nextId==2 && m.estimatedBytes==16);
        const auto prior=RF455_GetTextureAccounting();TX_CHECK(prior.created==account.created+1 && prior.estimatedBytes==account.estimatedBytes+16);
        unsigned capacity=1;
        for(unsigned i=0;i<50;++i){char name[32];std::sprintf(name,"TEX_%03u.RFT",i);TX_CHECK(RF455_AddTexture(&m,".\\growth",name));
            if(i+1>capacity){capacity+=capacity/2;if(capacity<i+1)capacity=i+1;}
            TX_CHECK(static_cast<unsigned>(m.capacity-m.begin)==capacity && static_cast<unsigned>(m.end-m.begin)==i+1);TX_CHECK(RF455_GetTextureId(&m,name)==i+2 && RF455_GetTextureById(&m,i+2));
        }
        TX_CHECK(!RF455_AddTexture(&m,".\\growth","tex_000.dds"));TX_CHECK(RF455_GetTextureId(&m,"TEX_000.DDS")==2);
        TX_CHECK(RF455_AddTexture(&m,".\\growth","sub\\TEX_000.DDS"));TX_CHECK(m.end-m.begin==51 && RF455_GetTextureId(&m,"TEX_000.DDS")==2 && !RF455_GetTextureId(&m,"sub\\TEX_000.DDS"));
        RF455_DeleteTextureByName(&m,"TEX_000.DDS");TX_CHECK(m.end-m.begin==50 && RF455_GetTextureId(&m,"TEX_000.DDS")==2);
        RF455_DeleteTextureById(&m,2);TX_CHECK(m.end-m.begin==49 && !RF455_GetTextureById(&m,2));
        RF455_DeleteTextureByName(&m,"TEX_001.DDS");TX_CHECK(m.end-m.begin==49);RF455_DeleteTextureByName(&m,"tex_001.rft");TX_CHECK(m.end-m.begin==48);
        const auto bytes=m.estimatedBytes,id=m.nextId;auto** begin=m.begin;auto** cap=m.capacity;RF455_ClearTextureManager(&m);TX_CHECK(m.begin==begin && m.end==begin && m.capacity==cap && m.estimatedBytes==bytes && m.nextId==id);
        TX_CHECK(RF455_AddTexture(&m,".\\growth","TEX_000.RFT"));RF455_InitTextureManager(&m);TX_CHECK(m.begin==begin && m.end==begin+1 && m.capacity==cap && !m.device && m.nextId==1 && !m.estimatedBytes);m.device=c.device;
    }
    {
        TXManager owned(c.device);const auto ops=RF455_TextureMaterialOps(&owned.value);
        std::fprintf(stderr,"GPU materials\n");std::fflush(stderr);
        for(unsigned model=3;model<=5;++model){char file[64];std::sprintf(file,"models/model_%u.msh",model);std::vector<unsigned char> bytes;TX_CHECK(txFile(file,bytes));std::vector<RF455Mesh08Part> parts(100);RF455Mesh08View view={};
            TX_CHECK(RF455_DecodeMesh08(bytes.data(),bytes.size(),parts.data(),parts.size(),&view)==RF_MESH08_OK);
            RF455MeshAccounting meshAccounting={};
            for(unsigned p=0;p<view.meshCount;++p){RF455MeshStorage mesh;RF455_ConstructMeshStorage(&mesh,&meshAccounting);unsigned char header[693];std::memcpy(header,view.parts[p].header,693);
                TX_CHECK(RF455_LoadMesh08Materials(&mesh,header,".\\tex","ignored",&ops)==RF_MESH_RUNTIME_OK);
                const unsigned offsets[]={5111,5123,5767,5771,5775};
                for(auto offset:offsets){std::uint32_t id=0;std::memcpy(&id,mesh.bytes+offset,4);TX_CHECK(!id || id==0xffffffff || RF455_GetTextureById(&owned.value,id));if(id && id!=0xffffffff)++materialHits;}
                ++materialParts;
            }
        }
        TX_CHECK(materialParts==97 && materialHits>0 && owned.value.end>owned.value.begin);
    }
    TX_CHECK(SUCCEEDED(c.device->SetTexture(0,nullptr)));TX_CHECK(c.device->Release()==0);c.device=nullptr;TX_CHECK(c.api->Release()==0);c.api=nullptr;
    std::vector<IDirect3DCubeTexture9*>().swap(observedCubes);RF455_SetCharacterTextureApi(old);return 0;
}
extern "C" int RF455_RunCharacterTextureChecks(const char* dll,const char* output,const char* frame,int gpu){
    textureChecks=profileCases=realGpuCases=renderCases=materialParts=materialHits=orphanCases=fileCalls=memoryCalls=0;observedCubes.clear();
    RF455CharacterRfsCache cache;auto* previous=RF455_SetCharacterRfsCache(&cache);std::vector<TXAsset> assets;int status=txCpu(assets,cache);if(!status && gpu)status=txGpu(assets,dll,frame);RF455_SetCharacterRfsCache(previous);
    FILE* report=std::fopen(output,"wb");if(!report)return 1;
    std::fprintf(report,"{\"status\":\"%s\",\"checks\":%u,\"dds_profiles\":%u,\"gpu_texture_pairs\":%u,\"render_cases\":%u,\"material_parts\":%u,\"material_texture_bindings\":%u,\"cube_orphans_observed_and_released\":%u,\"memory_calls\":%u,\"file_calls\":%u}\n",status?"FAIL":"PASS",textureChecks,profileCases,realGpuCases,renderCases,materialParts,materialHits,orphanCases,memoryCalls,fileCalls);std::fclose(report);return status;
}
#ifndef RF455_TEXTURE_EMBEDDED
int main(int argc,char** argv){if(argc!=5 || (std::strcmp(argv[1],"--cpu") && std::strcmp(argv[1],"--gpu")))return 2;return RF455_RunCharacterTextureChecks(argv[2],argv[3],argv[4],!std::strcmp(argv[1],"--gpu"));}
#endif
