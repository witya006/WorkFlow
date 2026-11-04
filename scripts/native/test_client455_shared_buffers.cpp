#include "client455_shared_buffers.h"
#include <cstdio>
#include <cstring>
#include <memory>
#include <string>
#include <vector>

static unsigned checks,captureCases,modelFiles,modelParts,gpuDraws,gpuModelParts,gpuModelUploads;
#define B_CHECK(value) do{++checks;if(!(value)){std::fprintf(stderr,"buffer check%u line%d\n",checks,__LINE__);return 1;}}while(0)
namespace {
struct Event {char op;unsigned type,a,b,c,d;void* object;};
struct Capture;
struct FakeBuffer {void** table;Capture* owner;unsigned type,releases=0;std::vector<unsigned char> bytes;};
struct FakeDevice {void** table;Capture* owner;};
struct Capture {
    void* deviceTable[119]={};void* bufferTable[14]={};FakeDevice device={deviceTable,this};
    std::vector<std::unique_ptr<FakeBuffer>> resources;std::vector<Event> events;
    unsigned failCreate=0,failLock=0;bool failUnlock=false;
    Capture();
    IDirect3DDevice9* d3d(){return reinterpret_cast<IDirect3DDevice9*>(&device);}
};
ULONG WINAPI release(FakeBuffer* self){++self->releases;self->owner->events.push_back({'R',self->type,0,0,0,0,self});return 0;}
HRESULT WINAPI lock(FakeBuffer* self,UINT offset,UINT size,void** output,DWORD flags){
    auto& s=*self->owner;s.events.push_back({'L',self->type,offset,size,flags,0,self});
    if(s.failLock==self->type || offset>self->bytes.size() || size>self->bytes.size()-offset)return E_FAIL;
    *output=self->bytes.data()+offset;return S_OK;
}
HRESULT WINAPI unlock(FakeBuffer* self){self->owner->events.push_back({'U',self->type,0,0,0,0,self});return self->owner->failUnlock?E_FAIL:S_OK;}
HRESULT create(FakeDevice* device,UINT size,DWORD usage,unsigned format,D3DPOOL pool,void** output,HANDLE* shared,unsigned type){
    auto& s=*device->owner;s.events.push_back({'C',type,size,usage,format,static_cast<unsigned>(pool),shared});if(s.failCreate==type)return E_FAIL;
    std::unique_ptr<FakeBuffer> buffer(new FakeBuffer);buffer->table=s.bufferTable;buffer->owner=&s;buffer->type=type;buffer->bytes.resize(size);
    *output=buffer.get();s.resources.push_back(std::move(buffer));return S_OK;
}
HRESULT WINAPI vertex(FakeDevice* d,UINT size,DWORD usage,DWORD fvf,D3DPOOL pool,IDirect3DVertexBuffer9** output,HANDLE* shared){return create(d,size,usage,fvf,pool,reinterpret_cast<void**>(output),shared,fvf==278?36:64);}
HRESULT WINAPI index(FakeDevice* d,UINT size,DWORD usage,D3DFORMAT format,D3DPOOL pool,IDirect3DIndexBuffer9** output,HANDLE* shared){return create(d,size,usage,static_cast<unsigned>(format),pool,reinterpret_cast<void**>(output),shared,1);}
HRESULT WINAPI stream(FakeDevice* d,UINT number,IDirect3DVertexBuffer9* buffer,UINT offset,UINT stride){d->owner->events.push_back({'S',stride,number,offset,0,0,buffer});return E_FAIL;}
HRESULT WINAPI indices(FakeDevice* d,IDirect3DIndexBuffer9* buffer){d->owner->events.push_back({'I',1,0,0,0,0,buffer});return E_FAIL;}
Capture::Capture(){
    deviceTable[26]=reinterpret_cast<void*>(vertex);deviceTable[27]=reinterpret_cast<void*>(index);
    deviceTable[100]=reinterpret_cast<void*>(stream);deviceTable[104]=reinterpret_cast<void*>(indices);
    bufferTable[2]=reinterpret_cast<void*>(release);bufferTable[11]=reinterpret_cast<void*>(lock);bufferTable[12]=reinterpret_cast<void*>(unlock);
}
struct VertexOps {
    using Pool=RF455VertexBufferPool;unsigned stride;
    unsigned capacity()const{return 2300000;}unsigned type()const{return stride;}
    void construct(Pool* p)const{RF455_ConstructVertexPool(p);}void destroy(Pool* p)const{RF455_DestroyVertexPool(p);}
    int upload(Pool* p,const void* s,unsigned n,unsigned* o,RF455BufferAccounting* a)const{return stride==36?RF455_UploadVertices36(p,s,n,o,a):RF455_UploadVertices64(p,s,n,o,a);}
    void bind(Pool* p,unsigned n)const{if(stride==36)RF455_BindVertices36(p,n);else RF455_BindVertices64(p,n);}
};
struct IndexOps {
    using Pool=RF455IndexBufferPool;
    unsigned capacity()const{return 1000000;}unsigned type()const{return 1;}
    void construct(Pool* p)const{RF455_ConstructIndexPool(p);}void destroy(Pool* p)const{RF455_DestroyIndexPool(p);}
    int upload(Pool* p,const void* s,unsigned n,unsigned* o,RF455BufferAccounting* a)const{return RF455_UploadIndices(p,s,n,o,a);}
    void bind(Pool* p,unsigned n)const{RF455_BindIndices(p,n);}
};
template<class Ops> int policy(const Ops& ops){
    using Pool=typename Ops::Pool;const unsigned cap=ops.capacity(),type=ops.type();Capture s;Pool pool;
    std::memset(&pool,0xa5,sizeof(pool));ops.construct(&pool);const unsigned char zeros[8200]={};B_CHECK(!std::memcmp(&pool,zeros,sizeof(pool)));
    unsigned offset=0xdeadbeef;RF455BufferAccounting account={0xfffffff0,0xffffffff};const unsigned char source[32]={1,2,3,4,5,6,7,8};
    B_CHECK(!ops.upload(&pool,source,12,&offset,&account) && offset==0xdeadbeef && s.events.empty());pool.device=s.d3d();
    B_CHECK(ops.upload(&pool,source,12,&offset,&account) && offset==0 && pool.used[0]==12);B_CHECK(s.resources.size()==1 && s.events.size()==3);
    B_CHECK(s.events[0].op=='C' && s.events[0].a==cap && s.events[0].b==8 && s.events[0].c==(type==1?101u:(type==36?278u:282u)) && s.events[0].d==1 && !s.events[0].object);
    B_CHECK(s.events[1].op=='L' && s.events[1].a==0 && s.events[1].b==12 && !s.events[1].c && s.events[2].op=='U');
    B_CHECK(account.created==0 && account.bytes==cap-16 && !std::memcmp(s.resources[0]->bytes.data(),source,12));
    B_CHECK(ops.upload(&pool,source,20,&offset,&account) && offset==12 && pool.used[0]==32 && s.resources.size()==1);
    pool.used[0]=cap-4;B_CHECK(ops.upload(&pool,source,4,&offset,&account) && offset==cap-4 && pool.used[0]==cap);
    B_CHECK(ops.upload(&pool,source,8,&offset,&account) && offset==cap && pool.used[1]==8 && s.resources.size()==2);
    pool.used[0]=4;B_CHECK(ops.upload(&pool,source,8,&offset,&account) && offset==4 && pool.used[0]==12 && pool.used[1]==8);
    s.failUnlock=true;B_CHECK(ops.upload(&pool,source,4,&offset,&account) && offset==12 && pool.used[0]==16);s.failUnlock=false;
    pool.used[0]=0xfffffff0;s.failLock=type;offset=0xdeadbeef;const auto before=s.events.size();
    B_CHECK(!ops.upload(&pool,source,32,&offset,&account) && offset==0xdeadbeef && pool.used[0]==0xfffffff0);
    B_CHECK(s.events.size()==before+1 && s.events.back().op=='L' && s.events.back().a==0xfffffff0);
    s.failLock=0;for(auto& used:pool.used)used=cap;const auto beforeFull=s.events.size();B_CHECK(!ops.upload(&pool,source,1,&offset,&account) && s.events.size()==beforeFull);
    pool.used[1023]=cap-4;B_CHECK(ops.upload(&pool,source,4,&offset,&account) && offset==cap*1024u-4 && pool.used[1023]==cap && pool.buffers[1023]);
    pool.used[0]=0;B_CHECK(ops.upload(&pool,source,0,&offset,&account) && offset==0 && !pool.used[0]);
    const unsigned bindings[]={0,cap-1,cap,cap*1024u-1,cap*1024u,0xffffffff};
    for(auto value:bindings){const auto at=s.events.size();ops.bind(&pool,value);
        if(value/cap<1024 && value!=0xffffffff){B_CHECK(s.events.size()==at+1 && s.events.back().object==pool.buffers[value/cap]);B_CHECK(!s.events.back().a && !s.events.back().b);B_CHECK(type==1?s.events.back().op=='I':(s.events.back().op=='S' && s.events.back().type==type));}
        else B_CHECK(s.events.size()==at);
    }
    pool.device=nullptr;const auto beforeBind=s.events.size();ops.bind(&pool,0);B_CHECK(s.events.size()==beforeBind);pool.device=s.d3d();
    const Pool saved=pool;const auto oldAccounting=account;const auto releaseAt=s.events.size();ops.destroy(&pool);
    B_CHECK(!std::memcmp(&pool,&saved,sizeof(pool)) && !std::memcmp(&account,&oldAccounting,sizeof(account)));
    B_CHECK(s.events.size()==releaseAt+3 && s.events[releaseAt].object==saved.buffers[0] && s.events[releaseAt+1].object==saved.buffers[1] && s.events[releaseAt+2].object==saved.buffers[1023]);
    ops.construct(&pool);pool.device=s.d3d();s.failCreate=type;offset=0xdeadbeef;const auto old=account;
    B_CHECK(!ops.upload(&pool,source,4,&offset,&account) && offset==0xdeadbeef && !pool.buffers[0] && !std::memcmp(&account,&old,sizeof(old)));s.failCreate=0;
    s.failLock=type;B_CHECK(!ops.upload(&pool,source,4,&offset,&account) && offset==0xdeadbeef && pool.buffers[0] && !pool.used[0]);B_CHECK(account.created==old.created+1 && account.bytes==old.bytes+cap);
    const auto resources=s.resources.size();B_CHECK(!ops.upload(&pool,source,4,&offset,&account) && s.resources.size()==resources);s.failLock=0;ops.destroy(&pool);
    for(const auto& resource:s.resources)B_CHECK(resource->releases==1);
    ++captureCases;return 0;
}
static bool readFile(const std::string& path,std::vector<unsigned char>& bytes){
    FILE* file=std::fopen(path.c_str(),"rb");if(!file)return false;std::fseek(file,0,SEEK_END);const long size=std::ftell(file);if(size<0){std::fclose(file);return false;}std::fseek(file,0,SEEK_SET);bytes.resize(static_cast<std::size_t>(size));const bool ok=std::fread(bytes.data(),1,bytes.size(),file)==bytes.size();return !std::fclose(file) && ok;
}
static int rebaseCases(){
    const unsigned offsets[]={0,64,2299968,2300000,2300128,0xffffffff};
    for(auto offset:offsets){unsigned char storage[9]={0xcc,0,0,1,0,255,255,0,128};const auto original=std::vector<unsigned char>(storage,storage+9);RF455_RebaseMesh08Indices(storage+1,4,offset);
        for(unsigned i=0;i<4;++i){unsigned short a,b;std::memcpy(&a,original.data()+1+2*i,2);std::memcpy(&b,storage+1+2*i,2);B_CHECK(b==static_cast<unsigned short>(a+((offset%2300000)/64)));}B_CHECK(storage[0]==0xcc);
    }
    RF455_RebaseMesh08Indices(nullptr,0,0xffffffff);return 0;
}
static int modelCases(const char* workspace){
    Capture s;RF455VertexBufferPool vertices;RF455IndexBufferPool indices;RF455_ConstructVertexPool(&vertices);RF455_ConstructIndexPool(&indices);vertices.device=indices.device=s.d3d();RF455BufferAccounting account={};
    for(unsigned sample=1;sample<=12;++sample){char name[128];std::sprintf(name,"/work/client-reference/character-models/mesh08-native/sample_%03u.msh",sample);std::vector<unsigned char> raw;B_CHECK(readFile(std::string(workspace)+name,raw));
        std::vector<RF455Mesh08Part> records(100);RF455Mesh08View view={};B_CHECK(RF455_DecodeMesh08(raw.data(),raw.size(),records.data(),records.size(),&view)==RF_MESH08_OK);
        for(unsigned n=0;n<view.meshCount;++n){RF455MeshStorage mesh;RF455MeshAccounting meshAccount={};RF455_ConstructMeshStorage(&mesh,&meshAccount);const auto& part=view.parts[n];
            const auto before=s.events.size();RF455_UploadMesh08Gpu(&vertices,&indices,&account,&mesh,&part);unsigned vo,io;std::memcpy(&vo,mesh.bytes+4494,4);std::memcpy(&io,mesh.bytes+4502,4);
            if(!part.indexCount){B_CHECK(vo==0xffffffff && io==0xffffffff && s.events.size()==before);}
            else{
                auto* vb=reinterpret_cast<FakeBuffer*>(vertices.buffers[vo/2300000]);auto* ib=reinterpret_cast<FakeBuffer*>(indices.buffers[io/1000000]);
                B_CHECK(!std::memcmp(vb->bytes.data()+vo%2300000,part.vertices,64u*part.vertexCount));
                for(unsigned i=0;i<part.indexCount;++i){unsigned short input,actual;std::memcpy(&input,part.indices+2*i,2);std::memcpy(&actual,ib->bytes.data()+io%1000000+2*i,2);B_CHECK(actual==static_cast<unsigned short>(input+(vo%2300000)/64));}
            }
            ++modelParts;
        }
        ++modelFiles;
    }
    RF455_DestroyVertexPool(&vertices);RF455_DestroyIndexPool(&indices);for(const auto& resource:s.resources)B_CHECK(resource->releases==1);
    // The real loader ignores vertex upload failure and still rebases/uploads IB.
    Capture failure;RF455_ConstructVertexPool(&vertices);RF455_ConstructIndexPool(&indices);vertices.device=indices.device=failure.d3d();failure.failLock=64;
    unsigned char rawVertices[64]={};unsigned short rawIndices[]={0,1,65535};RF455Mesh08Part part={};part.vertices=rawVertices;part.indices=reinterpret_cast<unsigned char*>(rawIndices);part.vertexCount=1;part.indexCount=3;
    RF455MeshStorage mesh;RF455MeshAccounting meshAccount={};RF455_ConstructMeshStorage(&mesh,&meshAccount);RF455_UploadMesh08Gpu(&vertices,&indices,&account,&mesh,&part);unsigned vo,io;std::memcpy(&vo,mesh.bytes+4494,4);std::memcpy(&io,mesh.bytes+4502,4);
    B_CHECK(vo==0xffffffff && io==0 && vertices.buffers[0] && !vertices.used[0] && indices.used[0]==6);
    auto* ib=reinterpret_cast<FakeBuffer*>(indices.buffers[0]);for(unsigned i=0;i<3;++i){unsigned short actual;std::memcpy(&actual,ib->bytes.data()+2*i,2);B_CHECK(actual==static_cast<unsigned short>(rawIndices[i]+((0xffffffffu%2300000)/64)));}
    RF455_DestroyVertexPool(&vertices);RF455_DestroyIndexPool(&indices);for(const auto& resource:failure.resources)B_CHECK(resource->releases==1);
    RF455_ConstructVertexPool(&vertices);RF455_ConstructIndexPool(&indices);vertices.device=indices.device=failure.d3d();failure.failLock=1;RF455_ConstructMeshStorage(&mesh,&meshAccount);
    RF455_UploadMesh08Gpu(&vertices,&indices,&account,&mesh,&part);std::memcpy(&vo,mesh.bytes+4494,4);std::memcpy(&io,mesh.bytes+4502,4);
    B_CHECK(vo==0 && io==0xffffffff && vertices.used[0]==64 && !indices.used[0] && indices.buffers[0]);
    RF455_DestroyVertexPool(&vertices);RF455_DestroyIndexPool(&indices);for(const auto& resource:failure.resources)B_CHECK(resource->releases==1);return 0;
}
} // namespace
// Actual HAL/device rendering and the entry point are below.
namespace {
template<class T> struct Com {T* p=nullptr;~Com(){if(p)p->Release();}T** out(){return &p;}};
struct Device {
    HMODULE module=nullptr;HWND window=nullptr;IDirect3D9* api=nullptr;IDirect3DDevice9* device=nullptr;
    ~Device(){if(device)device->Release();if(api)api->Release();if(window)DestroyWindow(window);if(module)FreeLibrary(module);}
};
struct Pools {
    RF455VertexBufferPool vertex;RF455IndexBufferPool index;
    Pools(IDirect3DDevice9* device){RF455_ConstructVertexPool(&vertex);RF455_ConstructIndexPool(&index);vertex.device=index.device=device;}
    ~Pools(){RF455_DestroyVertexPool(&vertex);RF455_DestroyIndexPool(&index);}
};
int draw(IDirect3DDevice9* device,unsigned startIndex,unsigned firstVertex,std::vector<unsigned char>& rgb){
    const D3DVERTEXELEMENT9 elements[]={{0,0,D3DDECLTYPE_FLOAT4,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_POSITIONT,0},{0,16,D3DDECLTYPE_D3DCOLOR,D3DDECLMETHOD_DEFAULT,D3DDECLUSAGE_COLOR,0},D3DDECL_END()};
    Com<IDirect3DVertexDeclaration9> declaration;B_CHECK(SUCCEEDED(device->CreateVertexDeclaration(elements,declaration.out())));B_CHECK(SUCCEEDED(device->SetVertexDeclaration(declaration.p)));
    const D3DRENDERSTATETYPE disabled[]={D3DRS_ZENABLE,D3DRS_LIGHTING,D3DRS_ALPHABLENDENABLE,D3DRS_ALPHATESTENABLE,D3DRS_FOGENABLE};for(auto state:disabled)B_CHECK(SUCCEEDED(device->SetRenderState(state,FALSE)));
    B_CHECK(SUCCEEDED(device->SetRenderState(D3DRS_CULLMODE,D3DCULL_NONE)));
    B_CHECK(SUCCEEDED(device->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_SELECTARG1)));B_CHECK(SUCCEEDED(device->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_DIFFUSE)));B_CHECK(SUCCEEDED(device->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_SELECTARG1)));B_CHECK(SUCCEEDED(device->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_DIFFUSE)));
    B_CHECK(SUCCEEDED(device->Clear(0,nullptr,D3DCLEAR_TARGET,0x00132739,1,0)));B_CHECK(SUCCEEDED(device->BeginScene()));
    const auto hr=device->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,0,firstVertex,3,startIndex,1);const auto end=device->EndScene();B_CHECK(SUCCEEDED(hr) && SUCCEEDED(end));
    Com<IDirect3DSurface9> target,copy;B_CHECK(SUCCEEDED(device->GetRenderTarget(0,target.out())));B_CHECK(SUCCEEDED(device->CreateOffscreenPlainSurface(64,64,D3DFMT_X8R8G8B8,D3DPOOL_SYSTEMMEM,copy.out(),nullptr)));B_CHECK(SUCCEEDED(device->GetRenderTargetData(target.p,copy.p)));
    D3DLOCKED_RECT locked={};B_CHECK(SUCCEEDED(copy.p->LockRect(&locked,nullptr,D3DLOCK_READONLY)));rgb.resize(64*64*3);
    for(unsigned y=0;y<64;++y)for(unsigned x=0;x<64;++x){auto* out=rgb.data()+3*(y*64+x);const auto* in=static_cast<const unsigned char*>(locked.pBits)+locked.Pitch*y+4*x;out[0]=in[2];out[1]=in[1];out[2]=in[0];}
    B_CHECK(SUCCEEDED(copy.p->UnlockRect()));B_CHECK(SUCCEEDED(device->SetVertexDeclaration(nullptr)));++gpuDraws;return 0;
}
int saveFrame(const std::string& path,const std::vector<unsigned char>& rgb){
    BITMAPFILEHEADER file={};BITMAPINFOHEADER info={};file.bfType=0x4d42;file.bfOffBits=sizeof(file)+sizeof(info);file.bfSize=file.bfOffBits+64*64*3;info.biSize=sizeof(info);info.biWidth=64;info.biHeight=64;info.biPlanes=1;info.biBitCount=24;info.biSizeImage=64*64*3;
    FILE* out=std::fopen(path.c_str(),"wb");B_CHECK(out);bool ok=std::fwrite(&file,1,sizeof(file),out)==sizeof(file) && std::fwrite(&info,1,sizeof(info),out)==sizeof(info);
    for(int y=63;y>=0;--y)for(unsigned x=0;x<64;++x){const auto* in=rgb.data()+3*(y*64+x);unsigned char bgr[]={in[2],in[1],in[0]};ok=std::fwrite(bgr,1,3,out)==3 && ok;}
    const int closed=std::fclose(out);B_CHECK(ok && !closed);return 0;
}
int physicalModels(IDirect3DDevice9* device,const char* workspace){
    Pools pools(device);RF455BufferAccounting accounting={};RF455MeshAccounting meshes={};
    for(unsigned sample=1;sample<=12;++sample){char name[128];std::sprintf(name,"/work/client-reference/character-models/mesh08-native/sample_%03u.msh",sample);std::vector<unsigned char> raw;B_CHECK(readFile(std::string(workspace)+name,raw));std::vector<RF455Mesh08Part> parts(100);RF455Mesh08View view={};B_CHECK(RF455_DecodeMesh08(raw.data(),raw.size(),parts.data(),parts.size(),&view)==RF_MESH08_OK);
        for(unsigned n=0;n<view.meshCount;++n){RF455MeshStorage mesh;RF455_ConstructMeshStorage(&mesh,&meshes);RF455_UploadMesh08Gpu(&pools.vertex,&pools.index,&accounting,&mesh,&parts[n]);unsigned vo,io;std::memcpy(&vo,mesh.bytes+4494,4);std::memcpy(&io,mesh.bytes+4502,4);
            if(parts[n].indexCount){B_CHECK(vo!=0xffffffff && io!=0xffffffff);B_CHECK(pools.vertex.used[vo/2300000]>=vo%2300000+64u*parts[n].vertexCount && pools.index.used[io/1000000]>=io%1000000+2u*parts[n].indexCount);++gpuModelUploads;}
            else B_CHECK(vo==0xffffffff && io==0xffffffff);
            ++gpuModelParts;
        }
    }
    B_CHECK(gpuModelParts==393 && gpuModelUploads>0 && accounting.created>0);return 0;
}
int gpu(const char* frameBase,const char* workspace){
    Device c;char system[MAX_PATH];B_CHECK(GetSystemDirectoryA(system,MAX_PATH));c.module=LoadLibraryA((std::string(system)+"\\d3d9.dll").c_str());B_CHECK(c.module);
    auto create=reinterpret_cast<IDirect3D9* (WINAPI*)(UINT)>(GetProcAddress(c.module,"Direct3DCreate9"));B_CHECK(create);c.api=create(D3D_SDK_VERSION);B_CHECK(c.api);
    c.window=CreateWindowExA(0,"STATIC","RF455 owned shared buffer test",WS_OVERLAPPEDWINDOW,0,0,64,64,nullptr,nullptr,GetModuleHandleA(nullptr),nullptr);B_CHECK(c.window);
    D3DPRESENT_PARAMETERS pp={};pp.BackBufferWidth=pp.BackBufferHeight=64;pp.BackBufferFormat=D3DFMT_X8R8G8B8;pp.SwapEffect=D3DSWAPEFFECT_DISCARD;pp.Windowed=TRUE;pp.hDeviceWindow=c.window;
    B_CHECK(SUCCEEDED(c.api->CreateDevice(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,c.window,D3DCREATE_SOFTWARE_VERTEXPROCESSING,&pp,&c.device)));
    B_CHECK(physicalModels(c.device,workspace)==0);
    for(unsigned stride:{36u,64u}){
        Pools pool(c.device);RF455BufferAccounting account={};const VertexOps ops={stride};std::vector<unsigned char> triangle(3*stride,0);
        const float points[3][4]={{8,8,0,1},{56,8,0,1},{8,56,0,1}};const DWORD color=stride==64?0xffff0000:0xff00ffff;
        for(unsigned v=0;v<3;++v){std::memcpy(triangle.data()+v*stride,points[v],16);std::memcpy(triangle.data()+v*stride+16,&color,4);}
        std::vector<unsigned char> padding(5*stride);unsigned vo=0,io=0;B_CHECK(ops.upload(&pool.vertex,padding.data(),static_cast<unsigned>(padding.size()),&vo,&account));
        const unsigned short indexPadding[4]={};B_CHECK(RF455_UploadIndices(&pool.index,indexPadding,sizeof(indexPadding),&io,&account));
        unsigned short indicesData[]={0,1,2};RF455Mesh08Part part={};part.vertices=triangle.data();part.indices=reinterpret_cast<unsigned char*>(indicesData);part.vertexCount=part.indexCount=3;
        RF455MeshStorage mesh;RF455MeshAccounting meshAccount={};RF455_ConstructMeshStorage(&mesh,&meshAccount);
        if(stride==64){RF455_UploadMesh08Gpu(&pool.vertex,&pool.index,&account,&mesh,&part);std::memcpy(&vo,mesh.bytes+4494,4);std::memcpy(&io,mesh.bytes+4502,4);}
        else{B_CHECK(ops.upload(&pool.vertex,triangle.data(),static_cast<unsigned>(triangle.size()),&vo,&account));unsigned short legacyIndices[]={5,6,7};B_CHECK(RF455_UploadIndices(&pool.index,legacyIndices,sizeof(legacyIndices),&io,&account));}
        B_CHECK(vo==5*stride && io==8);
        D3DVERTEXBUFFER_DESC vd={};D3DINDEXBUFFER_DESC id={};B_CHECK(SUCCEEDED(pool.vertex.buffers[0]->GetDesc(&vd)) && SUCCEEDED(pool.index.buffers[0]->GetDesc(&id)));
        B_CHECK(vd.Size==2300000 && vd.Usage==8 && vd.Pool==D3DPOOL_MANAGED && vd.FVF==(stride==36?278u:282u));B_CHECK(id.Size==1000000 && id.Format==D3DFMT_INDEX16 && id.Usage==8 && id.Pool==D3DPOOL_MANAGED);
        ops.bind(&pool.vertex,vo);RF455_BindIndices(&pool.index,io);std::vector<unsigned char> first,second;B_CHECK(draw(c.device,io/2,5,first)==0);
        const auto* inside=first.data()+3*(16*64+16);const auto* outside=first.data()+3*(56*64+56);B_CHECK(inside[0]==(stride==64?255:0) && inside[1]==(stride==64?0:255) && inside[2]==(stride==64?0:255));B_CHECK(outside[0]==0x13 && outside[1]==0x27 && outside[2]==0x39);
        // Fill block0 to its exact physical boundary,then force both VB/IB to block1.
        padding.resize(2300000-pool.vertex.used[0]);B_CHECK(ops.upload(&pool.vertex,padding.data(),static_cast<unsigned>(padding.size()),&vo,&account));B_CHECK(pool.vertex.used[0]==2300000);
        padding.resize(1000000-pool.index.used[0]);B_CHECK(RF455_UploadIndices(&pool.index,padding.data(),static_cast<unsigned>(padding.size()),&io,&account));B_CHECK(pool.index.used[0]==1000000);
        if(stride==64){RF455_UploadMesh08Gpu(&pool.vertex,&pool.index,&account,&mesh,&part);std::memcpy(&vo,mesh.bytes+4494,4);std::memcpy(&io,mesh.bytes+4502,4);}
        else{B_CHECK(ops.upload(&pool.vertex,triangle.data(),static_cast<unsigned>(triangle.size()),&vo,&account));B_CHECK(RF455_UploadIndices(&pool.index,indicesData,sizeof(indicesData),&io,&account));}
        B_CHECK(vo==2300000 && io==1000000);
        ops.bind(&pool.vertex,vo);RF455_BindIndices(&pool.index,io);
        {Com<IDirect3DVertexBuffer9> current;UINT offset=999,currentStride=999;B_CHECK(SUCCEEDED(c.device->GetStreamSource(0,current.out(),&offset,&currentStride)));B_CHECK(current.p==pool.vertex.buffers[1] && offset==0 && currentStride==stride);}
        {Com<IDirect3DIndexBuffer9> current;B_CHECK(SUCCEEDED(c.device->GetIndices(current.out())) && current.p==pool.index.buffers[1]);}
        B_CHECK(draw(c.device,(io%1000000)/2,0,second)==0 && first==second);B_CHECK(account.created==4 && account.bytes==6600000);
        B_CHECK(saveFrame(std::string(frameBase)+"-"+std::to_string(stride)+".bmp",second)==0);
        B_CHECK(SUCCEEDED(c.device->SetStreamSource(0,nullptr,0,0)) && SUCCEEDED(c.device->SetIndices(nullptr)));
    }
    B_CHECK(c.device->Release()==0);c.device=nullptr;B_CHECK(c.api->Release()==0);c.api=nullptr;return 0;
}
} // namespace
extern "C" int RF455_RunSharedBufferChecks(const char* workspace,const char* output,const char* frameBase,int physical){
    checks=captureCases=modelFiles=modelParts=gpuDraws=gpuModelParts=gpuModelUploads=0;int result=policy(VertexOps{36});if(!result)result=policy(VertexOps{64});if(!result)result=policy(IndexOps{});if(!result)result=rebaseCases();if(!result)result=modelCases(workspace);if(!result && physical)result=gpu(frameBase,workspace);
    FILE* file=std::fopen(output,"wb");if(!file)return 1;std::fprintf(file,"{\"status\":\"%s\",\"checks\":%u,\"capture_pool_types\":%u,\"real_files\":%u,\"model_parts\":%u,\"gpu_draws\":%u,\"gpu_model_parts\":%u,\"gpu_model_uploads\":%u}\n",result?"FAIL":"PASS",checks,captureCases,modelFiles,modelParts,gpuDraws,gpuModelParts,gpuModelUploads);std::fclose(file);return result;
}
#ifndef RF455_SHARED_BUFFERS_EMBEDDED
int main(int argc,char** argv){if(argc!=5 || (std::strcmp(argv[1],"--gpu") && std::strcmp(argv[1],"--cpu")))return 2;return RF455_RunSharedBufferChecks(argv[2],argv[3],argv[4],!std::strcmp(argv[1],"--gpu"));}
#endif
