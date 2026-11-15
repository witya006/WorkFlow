// Standalone CPU-only checks for the production cache. No game, D3D or network.
// Argument: an existing scratch directory; creates a NEW "cache-fixtures" child
// and refuses to overwrite a previous fixture directory. No recursive deletion.
#include "client455_texture.h"
#include "client455_animation.h"
#include "client455_effects.h"
#include <direct.h>
#include <cstdlib>
#include <cstring>
#include <initializer_list>
#include <memory>

namespace {
const char* scenario="setup";
#define CHECK(value) do{if(!(value)){std::fprintf(stderr,"FAIL %s: line %d\n",scenario,__LINE__);return 1;}}while(0)
bool writeFile(const char* path,const void* bytes,std::size_t size){
    FILE* stream=std::fopen(path,"wb");if(!stream)return false;
    const bool written=!size || std::fwrite(bytes,1,size,stream)==size;
    return std::fclose(stream)==0 && written;
}
void put(std::vector<unsigned char>& bytes,std::size_t at,std::uint32_t value){
    std::memcpy(bytes.data()+at,&value,4);
}
template<class T> void field(unsigned char* bytes,unsigned offset,T value){std::memcpy(bytes+offset,&value,sizeof(value));}
template<class T> T field(const unsigned char* bytes,unsigned offset){T value;std::memcpy(&value,bytes+offset,sizeof(value));return value;}
bool archive(const char* path,const char* member,const char* payload,std::uint32_t offset,
    std::uint32_t declaredSize,bool duplicate=false){
    const std::size_t count=duplicate?2u:1u,base=4+64*count;
    const auto size=std::strlen(payload);std::vector<unsigned char> bytes(base+size,0);
    put(bytes,0,static_cast<std::uint32_t>(count));
    for(std::size_t i=0;i<count;++i){
        const auto at=4+64*i;std::memcpy(bytes.data()+at,member,std::strlen(member));
        put(bytes,at+56,offset+static_cast<std::uint32_t>(4*i));put(bytes,at+60,declaredSize);
    }
    std::memcpy(bytes.data()+base,payload,size);return writeFile(path,bytes.data(),bytes.size());
}
bool is(const RF455ResourceRead& read,const char* value){
    const auto size=std::strlen(value);
    return read.status==RF455ResourceReadStatus::Ready && read.bytes && read.bytes->size()==size
        && (!size || !std::memcmp(read.bytes->data(),value,size));
}
unsigned memoryCalls=0,cubeCalls=0,fileCalls=0;
std::vector<unsigned char> submitted;
UINT submittedWidth=0,submittedHeight=0,submittedLevels=0;
bool plainDefaults=false;
HRESULT plainResult=E_FAIL;
bool publishPlainTexture=false;
HRESULT cubeResult=E_FAIL;
struct MockTexture {
    void** vtable;
    unsigned releases=0;
};
ULONG WINAPI releaseTexture(MockTexture* texture){return ++texture->releases;}
HRESULT WINAPI describeTexture(MockTexture*,UINT,D3DSURFACE_DESC* desc){desc->Width=8;desc->Height=4;return S_OK;}
void* textureVtable[18]={};
MockTexture plainTexture={textureVtable},cubeTexture={textureVtable};
HRESULT WINAPI memory2D(IDirect3DDevice9*,LPCVOID bytes,UINT size,UINT width,UINT height,
    UINT levels,DWORD usage,D3DFORMAT format,D3DPOOL pool,DWORD filter,DWORD mipFilter,
    D3DCOLOR color,void* info,PALETTEENTRY* palette,IDirect3DTexture9** output){
    ++memoryCalls;const auto* data=static_cast<const unsigned char*>(bytes);
    submitted.assign(data,data+size);submittedWidth=width;submittedHeight=height;submittedLevels=levels;
    if(width==UINT_MAX){
        plainDefaults=height==UINT_MAX && levels==UINT_MAX && usage==0 && format==D3DFMT_UNKNOWN &&
            pool==D3DPOOL_MANAGED && filter==UINT_MAX && mipFilter==UINT_MAX && !color && !info && !palette;
        *output=publishPlainTexture?reinterpret_cast<IDirect3DTexture9*>(&plainTexture):nullptr;
        return plainResult;
    }
    *output=nullptr;return E_FAIL; // No GPU device or graphics API invocation.
}
HRESULT WINAPI memoryCube(IDirect3DDevice9*,LPCVOID,UINT,UINT,UINT,DWORD,D3DFORMAT,
    D3DPOOL,DWORD,DWORD,D3DCOLOR,void*,PALETTEENTRY*,IDirect3DCubeTexture9** output){
    ++cubeCalls;*output=reinterpret_cast<IDirect3DCubeTexture9*>(&cubeTexture);return cubeResult;
}
HRESULT WINAPI file2D(IDirect3DDevice9*,LPCSTR,IDirect3DTexture9** output){++fileCalls;*output=nullptr;return E_FAIL;}
int textureConsumer(){
    RF455CharacterRfsCache cache;auto* saved=RF455_SetCharacterRfsCache(&cache);
    const RF455CharacterTextureApi api={memory2D,memoryCube,file2D};
    const auto* oldApi=RF455_SetCharacterTextureApi(&api);
    struct Restore {
        RF455CharacterRfsCache* cache;const RF455CharacterTextureApi* api;
        ~Restore(){RF455_SetCharacterRfsCache(cache);RF455_SetCharacterTextureApi(api);}
    } restore={saved,oldApi};
    std::vector<unsigned char> dds(148,0);put(dds,0,0x20534444);put(dds,4,124);
    put(dds,12,8);put(dds,16,8);put(dds,20,16);put(dds,28,2);
    for(std::size_t i=128;i<dds.size();++i)dds[i]=static_cast<unsigned char>(i);
    CHECK(writeFile("texture.dds",dds.data(),dds.size()));
    scenario="texture consumer uses immutable cached source with private mip preparation";
    std::uint32_t flag=99;CHECK(!RF455_LoadCharacterTextureFile(nullptr,"texture.dds",1,false,2048,2048,&flag));
    CHECK(flag==0 && memoryCalls==1 && cubeCalls==0 && submitted.size()==132 && submittedWidth==4 && submittedHeight==4);
    const auto source=cache.ReadLooseBytes("texture.dds");CHECK(source.bytes && *source.bytes==dds);
    const auto reads=cache.Stats().payloadReads;
    CHECK(!RF455_LoadCharacterTextureFile(nullptr,"texture.dds",0,true,2048,2048,&flag));
    CHECK(memoryCalls==2 && submitted.size()==148 && submittedWidth==8 && submittedLevels==1);
    CHECK(cache.Stats().payloadReads==reads && *source.bytes==dds);

    scenario="texture missing or empty leaves caller flag unchanged";
    flag=99;CHECK(!RF455_LoadCharacterTextureFile(nullptr,"not-found.dds",0,false,2048,2048,&flag) && flag==99);
    CHECK(!RF455_LoadCharacterTextureFile(nullptr,"empty.bin",0,false,2048,2048,&flag) && flag==99);
    CHECK(!RF455_LoadCharacterTextureFile(nullptr,".\\empty\\empty.rft",0,false,2048,2048,&flag) && flag==99);

    scenario="opened invalid archive blocks texture loose fallback";
    CHECK(archive("bad/DATA0.RFS","texture.dds","x",68,148));
    CHECK(writeFile("bad/texture.dds",dds.data(),dds.size()));cache.Clear();
    flag=99;const auto calls=memoryCalls;
    CHECK(!RF455_LoadCharacterTextureFile(nullptr,".\\bad\\texture.dds",0,false,2048,2048,&flag));
    CHECK(flag==0 && memoryCalls==calls);

    textureVtable[2]=reinterpret_cast<void*>(releaseTexture);
    textureVtable[17]=reinterpret_cast<void*>(describeTexture);
    scenario="cube output is released once for each result and never passed as a 2D texture";
    put(dds,112,0x200);
    CHECK(writeFile("cube.dds",dds.data(),dds.size()));
    for(const HRESULT result:{S_OK,E_FAIL}){
        cubeResult=result;
        flag=99;CHECK(!RF455_LoadCharacterTextureFile(nullptr,"cube.dds",0,false,2048,2048,&flag));
        CHECK(flag==1 && cubeTexture.releases==cubeCalls);
    }

    scenario="plain fallback reuses loose bytes and unchanged D3DX defaults";
    CHECK(writeFile("bad/plain.bmp","RAW",3));
    CHECK(archive("bad/DATA0.RFS","plain.bmp","ARCHIVE",68,7));
    cache.Clear();cache.ResetStats();plainResult=S_OK;publishPlainTexture=true;
    RF455TextureManager manager;
    RF455_ConstructTextureManager(&manager);
    manager.device=reinterpret_cast<IDirect3DDevice9*>(1);
    CHECK(RF455_AddTexture(&manager,".\\bad","plain.bmp"));
    CHECK(plainDefaults && submitted==std::vector<unsigned char>({'R','A','W'}) && fileCalls==0);
    CHECK(cache.Stats().payloadReads==2 && manager.nextId==2 && manager.estimatedBytes==128);
    RF455_ClearTextureManager(&manager);
    CHECK(RF455_AddTexture(&manager,".\\bad","plain.bmp"));
    CHECK(cache.Stats().payloadReads==2 && fileCalls==0 && manager.nextId==3);
    RF455_ClearTextureManager(&manager);
    CHECK(plainTexture.releases==2);

    scenario="plain failure releases decoder output and continues to the next alias";
    CHECK(writeFile("bad/plain.rfc","ALIAS",5));
    plainResult=E_FAIL;
    CHECK(!RF455_AddTexture(&manager,".\\bad","plain.bmp"));
    CHECK(plainTexture.releases==4 && fileCalls==1 && manager.nextId==3 && manager.begin==manager.end);

    scenario="plain success without output is treated as failure";
    plainResult=S_OK;publishPlainTexture=false;
    CHECK(!RF455_AddTexture(&manager,".\\bad","plain.bmp"));
    CHECK(plainTexture.releases==4 && fileCalls==2 && manager.nextId==3 && manager.begin==manager.end);
    RF455_DestroyTextureManager(&manager);
    return 0;
}

struct TextureMigrationDecoder {
    std::vector<std::unique_ptr<MockTexture>> created;
    std::vector<unsigned> levels;
    std::vector<unsigned> colorKeys;
    std::vector<unsigned> widths;
    bool failSecond=false;
    unsigned fileCalls=0;
};
HRESULT WINAPI migrationTexture(IDirect3DDevice9* device,LPCVOID bytes,UINT size,UINT width,UINT,UINT levels,
    DWORD,D3DFORMAT,D3DPOOL,DWORD,DWORD,D3DCOLOR color,void*,PALETTEENTRY*,IDirect3DTexture9** output){
    auto& decoder=*reinterpret_cast<TextureMigrationDecoder*>(device);
    decoder.levels.push_back(levels);
    decoder.colorKeys.push_back(color);
    decoder.widths.push_back(width);
    *output=nullptr;
    const auto* input=static_cast<const unsigned char*>(bytes);
    if((width==UINT_MAX && (size!=3 || std::memcmp(input,"RAW",3))) ||
       (width!=UINT_MAX && (size!=132 || input[128]!=144 || decoder.failSecond))) return E_FAIL;
    auto texture=std::make_unique<MockTexture>();
    texture->vtable=textureVtable;
    *output=reinterpret_cast<IDirect3DTexture9*>(texture.get());
    decoder.created.push_back(std::move(texture));
    return S_OK;
}
HRESULT WINAPI migrationDisk(IDirect3DDevice9* device,LPCSTR,IDirect3DTexture9** output){
    ++reinterpret_cast<TextureMigrationDecoder*>(device)->fileCalls;
    *output=nullptr;
    return E_FAIL;
}
int textureMigration(){
    RF455CharacterRfsCache cache;
    const RF455CharacterTextureApi api={migrationTexture,memoryCube,migrationDisk};
    const auto* oldApi=RF455_SetCharacterTextureApi(&api);
    auto* oldCache=RF455_SetCharacterRfsCache(&cache);
    struct Restore {
        RF455CharacterRfsCache* cache;const RF455CharacterTextureApi* api;
        ~Restore(){RF455_SetCharacterRfsCache(cache);RF455_SetCharacterTextureApi(api);}
    } restore={oldCache,oldApi};
    TextureMigrationDecoder oldDecoder,newDecoder;
    auto* oldDevice=reinterpret_cast<IDirect3DDevice9*>(&oldDecoder);
    auto* newDevice=reinterpret_cast<IDirect3DDevice9*>(&newDecoder);
    RF455TextureManager manager;
    RF455_ConstructTextureManager(&manager);
    manager.device=oldDevice;
    CHECK(_mkdir("move-texture")==0);
    CHECK(writeFile("move-texture/same.bmp","RAW",3));
    std::vector<unsigned char> dds(148,0);
    put(dds,0,0x20534444);put(dds,4,124);put(dds,12,8);put(dds,16,8);put(dds,20,16);put(dds,28,2);
    for(std::size_t i=128;i<dds.size();++i)dds[i]=static_cast<unsigned char>(i);
    CHECK(writeFile("move-texture/skin.rfc",dds.data(),dds.size()));

    scenario="texture detach retains IDs and original successful load parameters";
    manager.mipSkip=1;
    CHECK(RF455_AddTexture(&manager,".\\move-texture","same.bmp"));
    CHECK(RF455_AddTexture(&manager,".\\move-texture","skin.dds"));
    CHECK(oldDecoder.created.size()==2 && manager.nextId==3);
    auto* entry1=manager.begin[0];auto* entry2=manager.begin[1];
    const auto account=RF455_GetTextureAccounting();
    const auto bytes=manager.estimatedBytes;
    const auto reads=cache.Stats().payloadReads;

    scenario="texture relocation follows actual mesh and EFF pointers even with stale IDs";
    RF455CharacterStorage model{}, alias{};
    RF455MeshStorage meshes[2]{};
    for(auto* record:{&model,&alias}){
        field(record->prefix.bytes,532,2u);
        field(record->prefix.bytes,536,meshes+0);
    }
    RF455CharacterStorage* models[]={&model,&alias};
    RF455CharacterManager modelManager{};
    modelManager.begin=models;modelManager.end=models+2;
    RF455EffectStore effects;
    auto& record=effects.files["effect.eff"]["PART"];
    record=std::make_unique<RF455EffectRecord>();
    auto& otherRecord=effects.files["unused.eff"]["OTHER"];
    otherRecord=std::make_unique<RF455EffectRecord>();
    auto& draw=record->draw;
    RF455CharacterRenderer owner{};
    owner.textures=manager;
    const unsigned fields[]={5107,5115,5119,5283,5791,5795,5799};
    for(auto offset:fields)field(meshes[0].bytes,offset,entry1->texture);
    field(meshes[0].bytes,5123,entry1->id);
    field(meshes[0].bytes,5127,entry2->id);
    field(draw.data(),120,entry2->texture);
    field(draw.data(),124,entry1->texture);
    field(otherRecord->draw.data(),120,entry1->texture);
    RF455_ApplyEffect(&owner,&meshes[0],record.get(),36);
    CHECK(field<IDirect3DTexture9*>(meshes[0].bytes,5115)==entry2->texture && field<unsigned>(meshes[0].bytes,5123)==entry1->id);
    field(meshes[1].bytes,5163+120,entry2->texture);
    auto* foreign=reinterpret_cast<IDirect3DTexture9*>(&plainTexture);
    field(meshes[1].bytes,5791,foreign);
    RF455CharacterTextureReferences references;
    CHECK(SUCCEEDED(RF455_CaptureCharacterTextureReferences(manager,{nullptr,&modelManager,&modelManager},{&effects,nullptr,&effects},references)));
    CHECK(references.sites.size()==11);
    RF455_ClearCharacterTextureReferences(references);
    for(auto offset:fields)CHECK(!field<IDirect3DTexture9*>(meshes[0].bytes,offset));
    CHECK(!field<IDirect3DTexture9*>(draw.data(),120) && !field<IDirect3DTexture9*>(draw.data(),124));
    CHECK(!field<IDirect3DTexture9*>(otherRecord->draw.data(),120));
    CHECK(!field<IDirect3DTexture9*>(meshes[1].bytes,5163+120) && field<IDirect3DTexture9*>(meshes[1].bytes,5791)==foreign);

    scenario="texture detach retains IDs and original successful load parameters";
    CHECK(FAILED(RF455_RecreateCharacterTextures(manager,newDevice)) && newDecoder.created.empty());
    RF455_DetachCharacterTextures(manager);
    RF455_DetachCharacterTextures(manager);
    CHECK(!manager.device && oldDecoder.created[0]->releases==1 && oldDecoder.created[1]->releases==1);
    CHECK(manager.begin[0]==entry1 && manager.begin[1]==entry2 && !entry1->texture && !entry2->texture);
    CHECK(RF455_GetTextureId(&manager,"skin.dds")==2 && !RF455_GetTextureById(&manager,2));

    scenario="texture recreation rolls back staged COM resources and supports retry";
    manager.mipSkip=0;
    newDecoder.failSecond=true;
    CHECK(FAILED(RF455_RecreateCharacterTextures(manager,newDevice)));
    CHECK(!manager.device && !entry1->texture && !entry2->texture && newDecoder.created.size()==1 && newDecoder.created[0]->releases==1);
    CHECK(!field<IDirect3DTexture9*>(meshes[0].bytes,5115) && !field<IDirect3DTexture9*>(draw.data(),120));
    newDecoder.failSecond=false;
    CHECK(SUCCEEDED(RF455_RecreateCharacterTextures(manager,newDevice)) && manager.device==newDevice);
    CHECK(newDecoder.created.size()==3 && RF455_GetTextureById(&manager,1)==reinterpret_cast<IDirect3DTexture9*>(newDecoder.created[1].get()));
    CHECK(entry2->texture==reinterpret_cast<IDirect3DTexture9*>(newDecoder.created[2].get()));
    RF455_RestoreCharacterTextureReferences(references);
    for(auto offset:fields)CHECK(field<IDirect3DTexture9*>(meshes[0].bytes,offset)==(offset==5115?entry2->texture:entry1->texture));
    CHECK(field<unsigned>(meshes[0].bytes,5123)==entry1->id && field<unsigned>(meshes[0].bytes,5127)==entry2->id);
    CHECK(field<IDirect3DTexture9*>(draw.data(),120)==entry2->texture && field<IDirect3DTexture9*>(draw.data(),124)==entry1->texture);
    CHECK(field<IDirect3DTexture9*>(otherRecord->draw.data(),120)==entry1->texture && !field<IDirect3DTexture9*>(otherRecord->draw.data(),124));
    CHECK(field<IDirect3DTexture9*>(meshes[1].bytes,5163+120)==entry2->texture && field<IDirect3DTexture9*>(meshes[1].bytes,5791)==foreign);
    CHECK(newDecoder.levels==std::vector<unsigned>({UINT_MAX,1,UINT_MAX,1}));
    CHECK(newDecoder.widths==std::vector<unsigned>({UINT_MAX,4,UINT_MAX,4}));
    CHECK(newDecoder.colorKeys==std::vector<unsigned>({0,UINT_MAX,0,UINT_MAX}));
    CHECK(!newDecoder.fileCalls && cache.Stats().payloadReads==reads && manager.nextId==3 && manager.estimatedBytes==bytes);
    CHECK(RF455_GetTextureAccounting().estimatedBytes==account.estimatedBytes && RF455_GetTextureAccounting().created==account.created);
    RF455_DestroyTextureManager(&manager);
    for(const auto& texture:newDecoder.created)CHECK(texture->releases==1);
    return 0;
}

struct BufferDevice;
struct Buffer {
    void** table;
    BufferDevice* owner;
    unsigned releases=0;
    std::vector<unsigned char> bytes;
};
struct BufferDevice {
    void** table;
    void* deviceTable[28]={},*bufferTable[13]={};
    std::vector<std::unique_ptr<Buffer>> resources;
    unsigned reads=0,writes=0,unlocks=0,failWrite=0;
    bool nullRead=false,failUnlock=false,failCreate=false;
    BufferDevice();
    IDirect3DDevice9* device(){return reinterpret_cast<IDirect3DDevice9*>(this);}
};
ULONG WINAPI releaseBuffer(Buffer* buffer){return ++buffer->releases;}
HRESULT WINAPI lockBuffer(Buffer* buffer,UINT offset,UINT size,void** data,DWORD flags){
    auto& owner=*buffer->owner;
    if(flags==D3DLOCK_READONLY)++owner.reads;
    else if(!flags && ++owner.writes==owner.failWrite)return E_FAIL;
    else if(flags)return E_INVALIDARG;
    if(!size || offset>buffer->bytes.size() || size>buffer->bytes.size()-offset)return E_INVALIDARG;
    *data=flags && owner.nullRead?nullptr:buffer->bytes.data()+offset;
    return S_OK;
}
HRESULT WINAPI unlockBuffer(Buffer* buffer){++buffer->owner->unlocks;return buffer->owner->failUnlock?E_FAIL:S_OK;}
Buffer* createBuffer(BufferDevice* device,unsigned size){
    auto resource=std::make_unique<Buffer>();
    resource->table=device->bufferTable;
    resource->owner=device;
    resource->bytes.resize(size);
    auto* output=resource.get();
    device->resources.push_back(std::move(resource));
    return output;
}
HRESULT WINAPI createVertex(BufferDevice* device,UINT size,DWORD usage,DWORD fvf,D3DPOOL pool,IDirect3DVertexBuffer9** output,HANDLE* shared){
    if(size!=RF455_VERTEX_BLOCK_BYTES || usage || (fvf!=278 && fvf!=282) || pool!=D3DPOOL_MANAGED || shared)return E_INVALIDARG;
    *output=reinterpret_cast<IDirect3DVertexBuffer9*>(createBuffer(device,size));
    return device->failCreate?E_FAIL:S_OK;
}
HRESULT WINAPI createIndex(BufferDevice* device,UINT size,DWORD usage,D3DFORMAT format,D3DPOOL pool,IDirect3DIndexBuffer9** output,HANDLE* shared){
    if(size!=RF455_INDEX_BLOCK_BYTES || usage || format!=D3DFMT_INDEX16 || pool!=D3DPOOL_MANAGED || shared)return E_INVALIDARG;
    *output=reinterpret_cast<IDirect3DIndexBuffer9*>(createBuffer(device,size));
    return device->failCreate?E_FAIL:S_OK;
}
BufferDevice::BufferDevice():table(deviceTable){
    deviceTable[26]=reinterpret_cast<void*>(createVertex);
    deviceTable[27]=reinterpret_cast<void*>(createIndex);
    bufferTable[2]=reinterpret_cast<void*>(releaseBuffer);
    bufferTable[11]=reinterpret_cast<void*>(lockBuffer);
    bufferTable[12]=reinterpret_cast<void*>(unlockBuffer);
}
int bufferMigration(){
    scenario="buffer snapshot captures only committed ranges and preserves sparse slots";
    BufferDevice oldDevice,newDevice;
    RF455VertexBufferPool vertices36={},vertices64={},target36={},target64={};
    RF455IndexBufferPool indices={},targetIndices={};
    vertices36.device=vertices64.device=indices.device=oldDevice.device();
    const unsigned char payload[]={1,2,3,4,5};
    std::uint32_t absolute=UINT_MAX;
    RF455BufferAccounting accounting={};
    CHECK(RF455_UploadVertices36(&vertices36,payload,sizeof(payload),&absolute,&accounting)==1 && absolute==0);
    vertices36.buffers[1]=reinterpret_cast<IDirect3DVertexBuffer9*>(createBuffer(&oldDevice,1));
    vertices64.buffers[701]=reinterpret_cast<IDirect3DVertexBuffer9*>(createBuffer(&oldDevice,16));
    indices.buffers[1023]=reinterpret_cast<IDirect3DIndexBuffer9*>(createBuffer(&oldDevice,10));
    vertices64.used[701]=8;indices.used[1023]=4;
    for(std::size_t resource=2;resource<oldDevice.resources.size();++resource)
        for(std::size_t i=0;i<oldDevice.resources[resource]->bytes.size();++i)
            oldDevice.resources[resource]->bytes[i]=static_cast<unsigned char>(i+1);
    RF455CharacterBufferSnapshot snapshot;
    CHECK(SUCCEEDED(RF455_CaptureCharacterBuffers(vertices36,vertices64,indices,snapshot)));
    CHECK(oldDevice.reads==3 && oldDevice.unlocks==4 && oldDevice.writes==1);
    CHECK(snapshot.vertices36.size()==2 && snapshot.vertices36[0].slot==0 && snapshot.vertices36[0].bytes.size()==5);
    CHECK(snapshot.vertices36[1].slot==1 && snapshot.vertices36[1].bytes.empty());
    CHECK(snapshot.vertices64.size()==1 && snapshot.vertices64[0].slot==701 && snapshot.vertices64[0].bytes.size()==8);
    CHECK(snapshot.indices.size()==1 && snapshot.indices[0].slot==1023 && snapshot.indices[0].bytes.size()==4);

    scenario="failed capture preserves prior snapshot and unlocks a null successful read";
    oldDevice.nullRead=true;
    CHECK(FAILED(RF455_CaptureCharacterBuffers(vertices36,vertices64,indices,snapshot)));
    CHECK(oldDevice.reads==4 && oldDevice.unlocks==5 && snapshot.indices[0].bytes[3]==4);
    oldDevice.nullRead=false;oldDevice.failUnlock=true;
    CHECK(FAILED(RF455_CaptureCharacterBuffers(vertices36,vertices64,indices,snapshot)));
    CHECK(snapshot.vertices36[0].bytes[4]==5);

    scenario="recreate rejects duplicate slots before touching device";
    snapshot.indices.push_back(snapshot.indices.front());
    CHECK(FAILED(RF455_RecreateCharacterBuffers(snapshot,newDevice.device(),target36,target64,targetIndices)));
    CHECK(newDevice.resources.empty());
    snapshot.indices.pop_back();

    scenario="failed creation, lock and unlock release staged objects leaving destinations vacant";
    newDevice.failCreate=true;
    CHECK(FAILED(RF455_RecreateCharacterBuffers(snapshot,newDevice.device(),target36,target64,targetIndices)));
    CHECK(newDevice.resources.size()==1 && newDevice.resources[0]->releases==1);
    newDevice.failCreate=false;newDevice.failWrite=2;
    CHECK(FAILED(RF455_RecreateCharacterBuffers(snapshot,newDevice.device(),target36,target64,targetIndices)));
    CHECK(newDevice.resources.size()==4 && !target36.device && !target64.device && !targetIndices.device);
    newDevice.failUnlock=true;
    CHECK(FAILED(RF455_RecreateCharacterBuffers(snapshot,newDevice.device(),target36,target64,targetIndices)));
    CHECK(newDevice.resources.size()==5 && !target36.buffers[0] && !target36.used[0]);
    for(const auto& resource:newDevice.resources)CHECK(resource->releases==1);

    scenario="retry restores exact bytes and original offsets, including an empty allocated slot";
    newDevice.failUnlock=false;
    for(const auto& resource:oldDevice.resources)CHECK(!resource->releases);
    RF455_DestroyVertexPool(&vertices36);
    RF455_DestroyVertexPool(&vertices64);
    RF455_DestroyIndexPool(&indices);
    CHECK(SUCCEEDED(RF455_RecreateCharacterBuffers(snapshot,newDevice.device(),target36,target64,targetIndices)));
    CHECK(target36.device==newDevice.device() && target64.device==target36.device && targetIndices.device==target36.device);
    CHECK(target36.used[0]==5 && target36.buffers[1] && !target36.used[1] && target64.used[701]==8 && targetIndices.used[1023]==4);
    CHECK(!std::memcmp(reinterpret_cast<Buffer*>(target36.buffers[0])->bytes.data(),snapshot.vertices36[0].bytes.data(),5));
    CHECK(!std::memcmp(reinterpret_cast<Buffer*>(target64.buffers[701])->bytes.data(),snapshot.vertices64[0].bytes.data(),8));
    CHECK(!std::memcmp(reinterpret_cast<Buffer*>(targetIndices.buffers[1023])->bytes.data(),snapshot.indices[0].bytes.data(),4));
    CHECK(newDevice.resources.size()==9 && FAILED(RF455_RecreateCharacterBuffers(snapshot,newDevice.device(),target36,target64,targetIndices)));
    CHECK(newDevice.resources.size()==9);
    RF455_DestroyVertexPool(&target36);
    RF455_DestroyVertexPool(&target64);
    RF455_DestroyIndexPool(&targetIndices);
    for(const auto& resource:newDevice.resources)CHECK(resource->releases==1);
    return 0;
}
struct ReaderMemory {
    std::map<void*,std::size_t> live;
    std::vector<std::string> messages;
    std::size_t calls=0,failAt=0,extentCalls=0,lastRequested=0;
    bool failAlways=false,bad=false;
    ~ReaderMemory(){for(const auto& entry:live)std::free(entry.first);}
    static void* __cdecl allocate(void* context,std::size_t size){
        auto& self=*static_cast<ReaderMemory*>(context);self.lastRequested=size;
        if(++self.calls==self.failAt || self.failAlways)return nullptr;
        void* bytes=std::malloc(size+16);if(bytes)self.live.emplace(bytes,size+16);return bytes;
    }
    static void __cdecl release(void* context,void* bytes){
        auto& self=*static_cast<ReaderMemory*>(context);const auto found=self.live.find(bytes);
        if(found==self.live.end()){self.bad=true;return;}self.live.erase(found);std::free(bytes);
    }
    static std::size_t __cdecl extent(void* context,const void* bytes){
        auto& self=*static_cast<ReaderMemory*>(context);++self.extentCalls;
        const auto found=self.live.find(const_cast<void*>(bytes));
        if(found==self.live.end()){self.bad=true;return 0;}return found->second;
    }
    static void __cdecl message(void* context,const char* text){static_cast<ReaderMemory*>(context)->messages.push_back(text);}
    static void __cdecl wideMessage(void*,const wchar_t*){}
    RF455MeshMemoryOps ops(){return {this,allocate,release};}
    void free(void* bytes){release(this,bytes);}
};
bool content(const void* bytes,std::uint32_t length,const char* text){
    return bytes && length==std::strlen(text) && (!length || !std::memcmp(bytes,text,length));
}
int modelAnimationConsumers(){
    for(const char* dir:{"models","short-model","animations","short-animation"})CHECK(_mkdir(dir)==0);
    CHECK(archive("models/DATA0.RFS","model.msh","ARCH",68,4));
    CHECK(writeFile("models/model.msh","LOOSE",5));
    CHECK(archive("short-model/DATA0.RFS","bad.msh","x",68,200));
    CHECK(writeFile("short-model/bad.msh","VALID",5));
    CHECK(archive("animations/DATA0.RFS","run.ani","ANI!",68,4));
    CHECK(writeFile("animations/run.ani","LOOSEANI",8));
    CHECK(writeFile("walk.ani","walk!",5));
    CHECK(archive("short-animation/DATA0.RFS","bad.ani","x",68,200));
    CHECK(writeFile("short-animation/bad.ani","GOODANI",7));
    CHECK(writeFile("empty.msh",nullptr,0) && writeFile("empty.ani",nullptr,0));
    RF455CharacterRfsCache cache;auto* saved=RF455_SetCharacterRfsCache(&cache);
    struct Restore {RF455CharacterRfsCache* cache;~Restore(){RF455_SetCharacterRfsCache(cache);}} restore={saved};
    ReaderMemory memory;auto ops=memory.ops();RF455RawModelBuffer first={},second={};

    scenario="MSH archive priority and independent mutable copies";
    CHECK(RF455_ReadMshFile(".\\models\\model.msh",&ops,&first)==1 && content(first.bytes,first.length,"ARCH"));
    const auto reads=cache.Stats().payloadReads;static_cast<char*>(first.bytes)[0]='X';
    CHECK(RF455_ReadMshFile(".\\models\\model.msh",&ops,&second)==1 && content(second.bytes,second.length,"ARCH"));
    CHECK(first.bytes!=second.bytes && cache.Stats().payloadReads==reads);
    memory.free(first.bytes);memory.free(second.bytes);

    scenario="MSH archive allocation failure and short read fall back to loose";
    memory.failAt=memory.calls+1;
    CHECK(RF455_ReadMshFile(".\\models\\model.msh",&ops,&first)==1 && content(first.bytes,first.length,"LOOSE"));memory.free(first.bytes);
    CHECK(RF455_ReadMshFile(".\\short-model\\bad.msh",&ops,&first)==1 && content(first.bytes,first.length,"VALID"));memory.free(first.bytes);

    scenario="MSH invalid allocator or failed allocation preserves output";
    char sentinel=0;first={&sentinel,99};memory.failAlways=true;
    CHECK(!RF455_ReadMshFile(".\\models\\model.msh",&ops,&first) && first.bytes==&sentinel && first.length==99);
    memory.failAlways=false;auto invalid=ops;invalid.allocate=nullptr;
    CHECK(!RF455_ReadMshFile(".\\models\\model.msh",&invalid,&first));
    CHECK(!RF455_ReadMshFile(".\\models\\model.msh",nullptr,&first));
    CHECK(!RF455_ReadMshFile("wrong.ani",&ops,&first) && first.bytes==&sentinel);

    std::uint32_t imported=0xfffffff0u;
    RF455AnimationContext context={{{&memory,ReaderMemory::allocate,ReaderMemory::release},ReaderMemory::extent},
        {&memory,ReaderMemory::message,nullptr},&imported};
    RF455AnimationBuffer ani={},ani2={};
    scenario="ANI archive allocation extent versus loose length accounting";
    CHECK(RF455_ReadAnimationFile(".\\animations\\run.ani",&context,&ani)==RF_ANIMATION_OK);
    CHECK(ani.fromRfs && ani.accountedBytes==20 && imported==4 && content(ani.bytes,ani.length,"ANI!"));
    const auto aniReads=cache.Stats().payloadReads;static_cast<char*>(ani.bytes)[0]='X';
    CHECK(RF455_ReadAnimationFile(".\\animations\\run.ani",&context,&ani2)==RF_ANIMATION_OK);
    CHECK(ani.bytes!=ani2.bytes && content(ani2.bytes,ani2.length,"ANI!") && imported==24 && cache.Stats().payloadReads==aniReads);
    memory.free(ani.bytes);memory.free(ani2.bytes);
    const auto extentCalls=memory.extentCalls;
    CHECK(RF455_ReadAnimationFile("walk.ani",&context,&ani)==RF_ANIMATION_OK);
    CHECK(!ani.fromRfs && ani.accountedBytes==5 && imported==29 && memory.extentCalls==extentCalls);memory.free(ani.bytes);

    scenario="ANI allocation or short archive read uses loose fallback";
    memory.failAt=memory.calls+1;
    CHECK(RF455_ReadAnimationFile(".\\animations\\run.ani",&context,&ani)==RF_ANIMATION_OK);
    CHECK(!ani.fromRfs && content(ani.bytes,ani.length,"LOOSEANI") && imported==37);memory.free(ani.bytes);
    CHECK(RF455_ReadAnimationFile(".\\short-animation\\bad.ani",&context,&ani)==RF_ANIMATION_OK);
    CHECK(!ani.fromRfs && content(ani.bytes,ani.length,"GOODANI") && imported==44);memory.free(ani.bytes);

    scenario="ANI loose allocation failure accounting and output preservation";
    ani={&sentinel,91,92,true};memory.failAt=memory.calls+1;
    CHECK(RF455_ReadAnimationFile("walk.ani",&context,&ani)==RF_ANIMATION_MEMORY);
    CHECK(imported==49 && ani.bytes==&sentinel && ani.length==91 && ani.accountedBytes==92 && ani.fromRfs);
    CHECK(!memory.messages.empty() && memory.messages.back()=="ReadAnimationData( walk.ani ) :NULL");
    CHECK(RF455_ReadAnimationFile("absent.ani",&context,&ani)==RF_ANIMATION_IO && imported==49 && ani.bytes==&sentinel);
    CHECK(memory.messages.back().find("Ani Not Found : FileName = absent.ani [")==0);

    scenario="zero-sized MSH and ANI still request allocator zero";
    CHECK(RF455_ReadMshFile("empty.msh",&ops,&first)==1 && memory.lastRequested==0 && first.length==0);memory.free(first.bytes);
    CHECK(RF455_ReadAnimationFile("empty.ani",&context,&ani)==RF_ANIMATION_OK);
    CHECK(memory.lastRequested==0 && ani.length==0 && ani.accountedBytes==0 && !ani.fromRfs && imported==49);memory.free(ani.bytes);
    CHECK(memory.live.empty() && !memory.bad);return 0;
}
bool binaryArchive(const char* path,const char* member,const std::vector<unsigned char>& payload,std::uint32_t declared){
    std::vector<unsigned char> bytes(68+payload.size(),0);put(bytes,0,1);
    std::memcpy(bytes.data()+4,member,std::strlen(member));put(bytes,60,68);put(bytes,64,declared);
    if(!payload.empty())std::memcpy(bytes.data()+68,payload.data(),payload.size());
    return writeFile(path,bytes.data(),bytes.size());
}
int legacyConsumer(){
    for(const char* dir:{"legacy","legacy-short","legacy-invalid"})CHECK(_mkdir(dir)==0);
    // One noncompact part with one vertex: parser owns model, part cookie,
    // vertex data and the zero-length face allocation. No render dependencies.
    std::vector<unsigned char> valid(2+693+28,0);valid[0]=1;valid[2]='B';valid[394]=1;valid[695]=42;
    CHECK(binaryArchive("legacy/DATA0.RFS","model.any",valid,static_cast<std::uint32_t>(valid.size())));
    CHECK(writeFile("legacy/model.any","bad",3));
    CHECK(writeFile("legacy-loose.bn",valid.data(),valid.size()));
    CHECK(binaryArchive("legacy-short/DATA0.RFS","model.any",valid,9999));
    CHECK(writeFile("legacy-short/model.any",valid.data(),valid.size()));
    const std::vector<unsigned char> malformed={1,0,0};
    CHECK(binaryArchive("legacy-invalid/DATA0.RFS","model.any",malformed,3));
    CHECK(writeFile("legacy-invalid/model.any",valid.data(),valid.size()));
    RF455CharacterRfsCache cache;auto* saved=RF455_SetCharacterRfsCache(&cache);
    struct Restore {RF455CharacterRfsCache* cache;~Restore(){RF455_SetCharacterRfsCache(cache);}} restore={saved};
    ReaderMemory memory;auto ops=memory.ops();RF455LegacyDiagnostics diagnostics={&memory,ReaderMemory::message,ReaderMemory::wideMessage};
    RF455LegacyModel *first=nullptr,*second=nullptr;

    scenario="legacy archived parse has independent model and nested ownership";
    CHECK(RF455_ImportLegacyFile(".\\legacy\\model.any",&ops,&diagnostics,&first)==RF_LEGACY_RUNTIME_OK);
    const auto* firstParts=field<RF455LegacyPart*>(first->bytes,4);auto* vertices=field<unsigned char*>(firstParts->bytes,696);
    CHECK(field<std::uint16_t>(first->bytes,2)==1 && vertices[0]==42);
    vertices[0]=99;const auto reads=cache.Stats().payloadReads;
    CHECK(RF455_ImportLegacyFile(".\\legacy\\model.any",&ops,&diagnostics,&second)==RF_LEGACY_RUNTIME_OK);
    const auto* secondParts=field<RF455LegacyPart*>(second->bytes,4);const auto* secondVertices=field<unsigned char*>(secondParts->bytes,696);
    CHECK(first!=second && firstParts!=secondParts && vertices!=secondVertices && secondVertices[0]==42 && cache.Stats().payloadReads==reads);
    CHECK(*cache.ReadArchiveBytes(".\\legacy\\model.any").bytes==valid);
    cache.Clear();CHECK(secondVertices[0]==42);RF455_DeleteLegacyModel(first,&ops);RF455_DeleteLegacyModel(second,&ops);
    CHECK(memory.live.empty() && memory.messages.back()=="ImportMeshorBoneData( .\\legacy\\model.any ) :NULL");

    scenario="legacy loose parse and short archive fallback";
    CHECK(RF455_ImportLegacyFile("legacy-loose.bn",&ops,&diagnostics,&first)==RF_LEGACY_RUNTIME_OK);RF455_DeleteLegacyModel(first,&ops);
    CHECK(RF455_ImportLegacyFile(".\\legacy-short\\model.any",&ops,&diagnostics,&first)==RF_LEGACY_RUNTIME_OK);RF455_DeleteLegacyModel(first,&ops);
    CHECK(memory.live.empty());

    scenario="legacy parsed invalid archive never falls back to valid loose file";
    RF455LegacyModel sentinel={};first=&sentinel;
    CHECK(RF455_ImportLegacyFile(".\\legacy-invalid\\model.any",&ops,&diagnostics,&first)==RF_LEGACY_RUNTIME_FORMAT && first==&sentinel);
    CHECK(memory.messages.back()=="ImportMeshorBoneData( .\\legacy-invalid\\model.any ) :NULL" && memory.live.empty());

    scenario="legacy missing file preserves output and missing diagnostic";
    CHECK(RF455_ImportLegacyFile("missing-legacy.bin",&ops,&diagnostics,&first)==RF_LEGACY_RUNTIME_IO && first==&sentinel);
    CHECK(memory.messages.back().find("Mesh or Bone Not Found : FileName = missing-legacy.bin [")==0);

    scenario="legacy decoder allocation failures release partial model";
    for(std::size_t fail=1;fail<=4;++fail){
        memory.failAt=memory.calls+fail;first=&sentinel;
        CHECK(RF455_ImportLegacyFile(".\\legacy\\model.any",&ops,&diagnostics,&first)==RF_LEGACY_RUNTIME_MEMORY);
        CHECK(first==&sentinel && memory.live.empty() && !memory.bad);
        CHECK(memory.messages.back()=="ImportMeshorBoneData( .\\legacy\\model.any ) :NULL");
    }
    memory.failAt=0;return 0;
}
int attachedModelInputLifetime()
{
    const unsigned char badMesh08[] = {'M','E','S','H','0','8',1,0};
    const unsigned char badLegacy[] = {1,0,0};
    const unsigned char emptyLegacy[] = {0,0};
    CHECK(writeFile("bad-mesh08.msh",badMesh08,sizeof badMesh08));
    CHECK(writeFile("bad-legacy.msh",badLegacy,sizeof badLegacy));
    CHECK(writeFile("empty-legacy.msh",emptyLegacy,sizeof emptyLegacy));

    RF455CharacterRfsCache cache;
    auto* saved=RF455_SetCharacterRfsCache(&cache);
    struct Restore {RF455CharacterRfsCache* cache;~Restore(){RF455_SetCharacterRfsCache(cache);}} restore={saved};
    ReaderMemory memory;
    RF455TextureManager textures{};
    RF455VertexBufferPool vertices{};
    RF455IndexBufferPool indices{};
    RF455MeshAccounting meshAccounting{};
    RF455BufferAccounting bufferAccounting{};
    RF455LegacyScratch scratch;
    const RF455MeshMatrixOps matrices={
        [](void*,float*,const void*) -> void* { std::abort(); },
        [](void*,const void*,const void*) -> void* { std::abort(); }
    };
    const RF455CharacterLoadContext context={
        {{memory.ops(),matrices,&textures,&vertices,&indices,&meshAccounting,&bufferAccounting},
         &vertices,0,&scratch,{&memory,ReaderMemory::message,ReaderMemory::wideMessage}},
        {}
    };
    RF455CharacterStorage parent,child;
    RF455_ConstructCharacter(&parent);
    field(parent.prefix.bytes,260,1u);
    const auto prepare=[&](const char* name) {
        RF455_ConstructCharacter(&child);
        std::strcpy(reinterpret_cast<char*>(child.prefix.bytes+4),name);
        field(child.prefix.bytes,272,&parent.prefix);
    };

    scenario="attached MESH08 format failure releases each copy on retry";
    prepare("bad-mesh08.msh");
    for(unsigned attempt=0;attempt<2;++attempt) {
        const auto calls=memory.calls;
        CHECK(!RF455_LoadCharacter(&child,0,&context));
        CHECK(!child.prefix.bytes[264] && !field<unsigned>(child.prefix.bytes,260));
        CHECK(memory.calls==calls+1 && memory.live.empty() && !memory.bad);
    }
    CHECK(cache.Stats().payloadReads==1);

    scenario="attached legacy format failure releases the copy and keeps the attempted flag";
    prepare("bad-legacy.msh");
    auto calls=memory.calls;
    CHECK(!RF455_LoadCharacter(&child,0,&context));
    CHECK(child.prefix.bytes[264]==1 && !field<unsigned>(child.prefix.bytes,260));
    CHECK(memory.calls==calls+1 && memory.live.empty() && !memory.bad);
    calls=memory.calls;
    CHECK(RF455_LoadCharacter(&child,0,&context) && memory.calls==calls);

    scenario="attached legacy conversion allocation failure releases both source and decoded blocks";
    prepare("empty-legacy.msh");
    // One raw allocation, then the legacy record and its part cookie. Reject
    // the next allocation in the converter for the destination mesh array.
    memory.failAt=memory.calls+4;
    CHECK(!RF455_LoadCharacter(&child,0,&context) && memory.calls==memory.failAt);
    CHECK(child.prefix.bytes[264]==1 && !field<unsigned>(child.prefix.bytes,260));
    CHECK(memory.live.empty() && !memory.bad);
    return 0;
}
int indexRobustness(){
    for(const char* dir:{"index-broken","index-list","index-empty","index-gap","index-retry"})CHECK(_mkdir(dir)==0);
    std::vector<unsigned char> broken(140,0);put(broken,0,2);
    std::memcpy(broken.data()+4,"part.rft",8);put(broken,60,132);put(broken,64,4);
    std::memset(broken.data()+68,'Q',56);std::memcpy(broken.data()+132,"LEAKTAIL",8);
    CHECK(writeFile("index-broken/DATA0.RFS",broken.data(),broken.size()));
    CHECK(archive("index-broken/DATA1.RFS","part.rft","GOOD",68,4));
    CHECK(archive("index-broken/DATA2.RFS","part.rft","LATE",68,4));
    CHECK(archive("index-broken/DATA4.RFS","skipped.rft","SKIP",68,4));
    RF455CharacterRfsCache cache;
    scenario="malformed numbered archive publishes no prefix and scanning continues";
    CHECK(is(cache.ReadArchiveBytes(".\\index-broken\\part.rft"),"GOOD"));
    CHECK(cache.FileCount()==1 && cache.ReadArchiveBytes(".\\index-broken\\skipped.rft").status==RF455ResourceReadStatus::Unavailable);

    scenario="RFSINFO consumes oversized token and continues after missing listed archive";
    const auto list=std::string(255,'A')+"EVIL.RFS VALID.RFS MISSING.RFS THIRD.RFS";
    CHECK(writeFile("index-list/RFSINFO.DAT",list.data(),list.size()));
    CHECK(archive("index-list/EVIL.RFS","evil.rft","EVIL",68,4));
    CHECK(archive("index-list/VALID.RFS","valid.rft","GOOD",68,4));
    CHECK(archive("index-list/THIRD.RFS","third.rft","LAST",68,4));cache.Clear();
    CHECK(is(cache.ReadArchiveBytes(".\\index-list\\valid.rft"),"GOOD"));
    CHECK(is(cache.ReadArchiveBytes(".\\index-list\\third.rft"),"LAST"));
    CHECK(cache.ReadArchiveBytes(".\\index-list\\evil.rft").status==RF455ResourceReadStatus::Unavailable && cache.FileCount()==2);

    scenario="empty RFSINFO suppresses numbered fallback and numbered gap ends scan";
    CHECK(writeFile("index-empty/RFSINFO.DAT",nullptr,0));
    CHECK(archive("index-empty/DATA0.RFS","hidden.rft","HIDE",68,4));
    CHECK(archive("index-gap/DATA1.RFS","hidden.rft","HIDE",68,4));cache.Clear();
    CHECK(cache.ReadArchiveBytes(".\\index-empty\\hidden.rft").status==RF455ResourceReadStatus::Unavailable);
    CHECK(cache.ReadArchiveBytes(".\\index-gap\\hidden.rft").status==RF455ResourceReadStatus::Unavailable && cache.FileCount()==0);

    scenario="invalid path rejected before directory mark and completed negative scan needs Clear";
    CHECK(!cache.LoadDirectory(std::string(256,'X')) && cache.DirectoryCount()==2);
    CHECK(writeFile("index-retry/DATA0.RFS","bad",3));
    CHECK(cache.ReadArchiveBytes(".\\index-retry\\fixed.rft").status==RF455ResourceReadStatus::Unavailable);
    CHECK(archive("index-retry/DATA0.RFS","fixed.rft","OKAY",68,4));
    CHECK(cache.ReadArchiveBytes(".\\index-retry\\fixed.rft").status==RF455ResourceReadStatus::Unavailable);
    cache.Clear();CHECK(is(cache.ReadArchiveBytes(".\\index-retry\\fixed.rft"),"OKAY"));return 0;
}
}

int main(int argc,char** argv){
    CHECK(argc==2 && _chdir(argv[1])==0);
    CHECK(_mkdir("cache-fixtures")==0 && _chdir("cache-fixtures")==0);
    for(const char* name:{"a","b","empty","negative","bad"})CHECK(_mkdir(name)==0);
    CHECK(archive("a/DATA0.RFS","dup.rft","AAAABBBB",132,4,true));
    CHECK(writeFile("a/dup.rft","LOOS",4));
    CHECK(writeFile("b/dup.rft","BEEF",4));
    CHECK(writeFile("one.bin","1111",4) && writeFile("two.bin","2222",4)
        && writeFile("three.bin","3333",4));
    RF455CharacterRfsCache cache;

    scenario="original normalization and first duplicate";
    CHECK(RF455CharacterRfsCache::Normalize("a/dup.rft")==RF455CharacterRfsCache::Normalize("dup.rft"));
    auto first=cache.ReadArchiveBytes(".\\a\\dup.rft");CHECK(is(first,"AAAA"));
    CHECK(cache.FileCount()==1 && cache.DirectoryCount()==1);

    scenario="immutable shared hit without payload reread";
    const auto before=cache.Stats();auto again=cache.ReadArchiveBytes("./a/DUP.RFT");
    CHECK(is(again,"AAAA") && again.bytes==first.bytes);
    CHECK(cache.Stats().hits==before.hits+1 && cache.Stats().payloadReads==before.payloadReads);

    scenario="archive and loose namespaces are separate";
    auto loose=cache.ReadLooseBytes("a/dup.rft");CHECK(is(loose,"LOOS") && loose.bytes!=first.bytes);
    CHECK(is(cache.ReadLooseBytes("b/dup.rft"),"BEEF"));

    scenario="loose size ceiling owns no payload and also applies on a hit";
    const auto sizeChecks=cache.Stats().payloadReads;
    auto rejected=cache.ReadLooseBytes("one.bin",3);
    CHECK(rejected.status==RF455ResourceReadStatus::ReadError && !rejected.bytes && rejected.declaredSize==4);
    CHECK(cache.Stats().payloadReads==sizeChecks && is(cache.ReadLooseBytes("one.bin",4),"1111"));
    rejected=cache.ReadLooseBytes("one.bin",3);
    CHECK(rejected.status==RF455ResourceReadStatus::ReadError && !rejected.bytes && rejected.declaredSize==4);
    CHECK(cache.Stats().payloadReads==sizeChecks+1);

    scenario="loose path canonicalization keeps all components";
    auto alias=cache.ReadLooseBytes("./a/../a/dup.rft");CHECK(alias.bytes==loose.bytes);
    char cwd[512];CHECK(_getcwd(cwd,sizeof(cwd))!=nullptr);
    const auto absolute=std::string(cwd)+"\\a\\dup.rft";
    CHECK(cache.ReadLooseBytes(absolute.c_str()).bytes==loose.bytes);

    scenario="generation snapshot until payload invalidation";
    CHECK(writeFile("a/dup.rft","NEW!",4));CHECK(is(cache.ReadLooseBytes("a/dup.rft"),"LOOS"));
    cache.ClearPayloads();CHECK(is(cache.ReadLooseBytes("a/dup.rft"),"NEW!"));
    CHECK(is(loose,"LOOS") && cache.FileCount()==1);

    scenario="full Clear refreshes archive index and leases survive";
    CHECK(archive("a/DATA0.RFS","dup.rft","PAD!FRESH",72,5));
    cache.Clear();CHECK(cache.FileCount()==0 && cache.DirectoryCount()==0 && cache.Stats().retainedBytes==0);
    CHECK(is(cache.ReadArchiveBytes(".\\a\\dup.rft"),"FRESH") && is(first,"AAAA"));

    scenario="LRU eviction leaves borrowed bytes valid";
    cache.Clear();cache.SetByteBudget(8);cache.ResetStats();
    auto one=cache.ReadLooseBytes("one.bin");auto two=cache.ReadLooseBytes("two.bin");
    CHECK(is(one,"1111") && is(two,"2222"));
    CHECK(cache.ReadLooseBytes("one.bin").bytes==one.bytes);
    CHECK(is(cache.ReadLooseBytes("three.bin"),"3333"));
    const auto reads=cache.Stats().payloadReads;
    CHECK(cache.ReadLooseBytes("one.bin").bytes==one.bytes && cache.Stats().payloadReads==reads);
    CHECK(is(cache.ReadLooseBytes("two.bin"),"2222") && cache.Stats().payloadReads==reads+1);
    CHECK(is(two,"2222") && cache.Stats().retainedBytes<=8 && cache.Stats().evictions>=1);

    scenario="budget reduction and counter reset preserve accounting";
    cache.SetByteBudget(4);CHECK(cache.Stats().retainedBytes<=4);
    const auto retained=cache.Stats().retainedBytes;cache.ResetStats();
    CHECK(cache.Stats().retainedBytes==retained && cache.Stats().hits==0 && cache.Stats().payloadReads==0);

    scenario="zero budget disables retention";
    cache.SetByteBudget(0);cache.ResetStats();
    auto zero1=cache.ReadLooseBytes("one.bin"),zero2=cache.ReadLooseBytes("one.bin");
    CHECK(is(zero1,"1111") && is(zero2,"1111") && zero1.bytes!=zero2.bytes);
    CHECK(cache.Stats().entries==0 && cache.Stats().retainedBytes==0 && cache.Stats().payloadReads==2);

    scenario="oversize valid payload remains readable uncached";
    cache.SetByteBudget(3);CHECK(is(cache.ReadLooseBytes("one.bin"),"1111"));
    CHECK(cache.Stats().retainedBytes==0 && cache.Stats().entries==0);

    scenario="truncated and overflowing archive extents fail before read";
    cache.SetByteBudget(1024);CHECK(archive("bad/DATA0.RFS","bad.rft","x",68,100));
    const auto malformed=cache.ReadArchiveBytes(".\\bad\\bad.rft");
    CHECK(malformed.status==RF455ResourceReadStatus::ReadError && malformed.declaredSize==100 && !malformed.bytes);
    CHECK(archive("bad/DATA0.RFS","bad.rft","x",0xfffffff0u,64));cache.Clear();
    const auto beforeBad=cache.Stats().payloadReads;
    CHECK(cache.ReadArchiveBytes(".\\bad\\bad.rft").status==RF455ResourceReadStatus::ReadError);
    CHECK(cache.Stats().payloadReads==beforeBad && cache.Stats().entries==0);
    CHECK(archive("bad/DATA0.RFS","bad.rft","good",68,4));cache.Clear();
    CHECK(is(cache.ReadArchiveBytes(".\\bad\\bad.rft"),"good"));

    scenario="zero-length data is ready but not retained";
    CHECK(writeFile("empty.bin",nullptr,0));const auto empty=cache.ReadLooseBytes("empty.bin");
    CHECK(is(empty,"") && empty.declaredSize==0);
    CHECK(archive("empty/DATA0.RFS","empty.rft","",68,0));
    CHECK(is(cache.ReadArchiveBytes(".\\empty\\empty.rft"),""));

    scenario="loose failed lookup is not cached";
    CHECK(cache.ReadLooseBytes("later.bin").status==RF455ResourceReadStatus::Unavailable);
    CHECK(writeFile("later.bin","NOW",3) && is(cache.ReadLooseBytes("later.bin"),"NOW"));

    scenario="original directory negative cache requires full Clear";
    CHECK(cache.ReadArchiveBytes(".\\negative\\late.rft").status==RF455ResourceReadStatus::Unavailable);
    CHECK(archive("negative/DATA0.RFS","late.rft","LATE",68,4));
    cache.ClearPayloads();CHECK(cache.ReadArchiveBytes(".\\negative\\late.rft").status==RF455ResourceReadStatus::Unavailable);
    cache.Clear();CHECK(is(cache.ReadArchiveBytes(".\\negative\\late.rft"),"LATE"));

    scenario="active-cache switching isolates retained bytes";
    RF455CharacterRfsCache other;auto* saved=RF455_SetCharacterRfsCache(&cache);
    auto fromFirst=RF455_GetCharacterRfsCache()->ReadLooseBytes("one.bin");
    RF455_SetCharacterRfsCache(&other);auto fromOther=RF455_GetCharacterRfsCache()->ReadLooseBytes("one.bin");
    RF455_SetCharacterRfsCache(saved);
    CHECK(is(fromFirst,"1111") && is(fromOther,"1111") && fromFirst.bytes!=fromOther.bytes);
    cache.Clear();CHECK(is(fromFirst,"1111") && other.Stats().entries==1);

    scenario="legacy Open remains an unbounded independent FILE";
    CHECK(archive("a/DATA0.RFS","dup.rft","AAAABBBB",132,4,true));cache.Clear();
    std::uint32_t declared=0;FILE* stream=cache.Open(".\\a\\dup.rft",&declared);
    CHECK(stream && declared==4);char bytes[8];const auto got=std::fread(bytes,1,sizeof(bytes),stream);
    const auto closed=std::fclose(stream);CHECK(got==8 && closed==0 && !std::memcmp(bytes,"AAAABBBB",8));
    CHECK(textureConsumer()==0);
    CHECK(textureMigration()==0);
    CHECK(bufferMigration()==0);
    CHECK(modelAnimationConsumers()==0);
    CHECK(legacyConsumer()==0);
    CHECK(attachedModelInputLifetime()==0);
    CHECK(indexRobustness()==0);
    std::puts("PASS: 51 resource-cache scenarios (CPU only; texture and buffer APIs stubbed)");return 0;
}
