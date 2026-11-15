#include "client455_effects.h"
#include "client455_effect_constants.h"
#include "client455_character_rfs.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <new>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>
#include <io.h>

namespace {
template<class T>T get(const void* p,unsigned n){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+n,sizeof(v));return v;}
template<class T>void put(void* p,unsigned n,T v){std::memcpy(static_cast<unsigned char*>(p)+n,&v,sizeof(v));}
__declspec(noinline) void copyFloat(void* destination,const void* source) {
    __asm {
        mov eax,source
        mov edx,destination
        fld dword ptr[eax]
        fstp dword ptr[edx]
    }
}
// 929070 uses strlen,not a20byte bound. Some shipped records terminate in a
// neighbouring field. Preserve that read while it remains inside padded176.
bool text(std::string& out,const unsigned char* bytes,unsigned at){const char* p=reinterpret_cast<const char*>(bytes+at);const char* end=static_cast<const char*>(std::memchr(p,0,176-at));if(!end)return false;out.assign(p,end);return true;}
std::string upper(std::string value){if(!value.empty())_strupr(&value[0]);return value;}
void construct(RF455EffectRecord& r){r.draw.fill(0);for(unsigned at:{24u,52u,88u,116u,152u})put<unsigned>(r.draw.data(),at,15);put<unsigned>(r.draw.data(),196,1);}
bool convert(RF455EffectRecord& r){
    const auto* source=r.exported.data();auto* d=r.draw.data();
    if(!text(r.texture[0],source,3)||!text(r.texture[1],source,23)||!text(r.directory,source,43)||!text(r.mesh,source,152))return false;
    r.mesh=upper(r.mesh);
    for(unsigned i=0;i<4;++i)put<unsigned>(d,156+4*i,source[63+i]);
    put<unsigned>(d,172,get<unsigned>(source,67));copyFloat(d+176,source+71);copyFloat(d+180,source+75);
    for(unsigned i=0;i<2;++i)put<unsigned>(d,184+4*i,source[79+i]);
    for(unsigned i=0;i<3;++i)put<unsigned>(d,196+4*i,source[81+i]);
    std::memcpy(d+208,source+84,64);copyFloat(d+288,source+148);put<unsigned>(d,192,get<unsigned>(source,172));return true;
}
using EffectFile = std::unique_ptr<FILE,decltype(&std::fclose)>;
enum class TokenResult {Value,End,TooLong};
TokenResult token(const unsigned char*& next,std::size_t& left,std::string& out){
    while (left && *next <= 32) { ++next; --left; }
    if (!left) return TokenResult::End;
    const auto* begin = next;
    while (left && *next > 32) { ++next; --left; }
    const auto length = static_cast<std::size_t>(next - begin);
    if (length > 4255) return TokenResult::TooLong;
    out.assign(reinterpret_cast<const char*>(begin), length);
    return TokenResult::Value;
}
RF455EffectStatus tokenError(TokenResult result){return result==TokenResult::TooLong?RF_EFFECT_NAME:RF_EFFECT_FORMAT;}
bool decodeRecord(RF455EffectRecord& record,const char* file,const unsigned char* wire,unsigned length){
    record.exported.fill(0);put<unsigned short>(record.exported.data(),0,176);record.exported[2]=2;
    std::memcpy(record.exported.data(),wire,length);construct(record);record.file=file;
    return convert(record);
}
void publishRecord(RF455EffectStore& store,RF455EffectRecord&& record,RF455EffectRead& report){
    auto& target=store.files[record.file];const auto found=target.find(record.mesh);
    if(found!=target.end() && found->second){
        // Live meshes borrow draw.data(). Never replace its allocation.
        *found->second=std::move(record);++report.replaced;
    }else{
        const auto key=record.mesh;
        std::unique_ptr<RF455EffectRecord> owned(new RF455EffectRecord(std::move(record)));
        if(found!=target.end())found->second=std::move(owned);
        else target.emplace(key,std::move(owned));
    }
}
template<class Publish>
RF455EffectRead readBuffer(const char* file,const void* input,std::size_t size,Publish publish){
    RF455EffectRead report={RF_EFFECT_OK,0,0,0,0};
    if(!file || (!input && size)){report.status=RF_EFFECT_FORMAT;return report;}
    const auto* bytes=static_cast<const unsigned char*>(input);std::size_t at=0;
    try{
        while(at<size){
            if(size-at<2){report.status=RF_EFFECT_FORMAT;break;}
            const unsigned length=get<unsigned short>(bytes+at,0);
            if(length<2||length>176||length>size-at){report.status=RF_EFFECT_FORMAT;break;}
            RF455EffectRecord record;
            if(!decodeRecord(record,file,bytes+at,length)){report.status=RF_EFFECT_NAME;break;}
            publish(std::move(record),report);++report.records;at+=length;
        }
    }catch(const std::bad_alloc&){report.status=RF_EFFECT_IO;}
    return report;
}
std::string inlineText(const unsigned char* d,unsigned at){const auto cap=get<unsigned>(d,at+20),length=get<unsigned>(d,at+16);const char* value=cap<16?reinterpret_cast<const char*>(d+at):get<const char*>(d,at);return length?std::string(value,length):std::string();}
void apply(RF455CharacterRenderer* owner,RF455MeshStorage* mesh,unsigned char* d,const std::string names[2],const std::string& directory,int grade){
    for(unsigned i=0;i<2;++i){void* cached=get<void*>(d,120+4*i);if(cached)put(mesh->bytes,5115+4*i,cached);
        else if(!names[i].empty() && !get<unsigned>(d,56+4*i)){
            put<unsigned>(d,56+4*i,1);RF455_AddTexture(&owner->textures,directory.c_str(),names[i].c_str());
            const auto id=RF455_GetTextureId(&owner->textures,names[i].c_str());put(mesh->bytes,5123+4*i,id);
            auto* texture=RF455_GetTextureById(&owner->textures,id);put(mesh->bytes,5115+4*i,texture);put(d,120+4*i,texture);
        }}
    put(mesh->bytes,5455,d);put(mesh->bytes,5147,RF455_EffectFactor(d+176,grade));
}
}
unsigned RF455_EffectFactor(const void* intensity,int grade){
    double unit,rate,epsilon,maximum;std::memcpy(&unit,&RF455_EFFECT_UNIT_BITS,8);std::memcpy(&rate,&RF455_EFFECT_RATE_BITS,8);std::memcpy(&epsilon,&RF455_EFFECT_EPSILON_BITS,8);std::memcpy(&maximum,&RF455_EFFECT_MAX_BITS,8);
    unsigned short oldControl,newControl;long long result;
    if(grade==36){__asm{mov eax,intensity
        fld dword ptr[eax]
        fsub epsilon
        fmul maximum}}
    else{__asm{fild grade
        fmul unit
        fmul rate}}
    __asm{fnstcw oldControl
        mov ax,oldControl
        or ax,0c00h
        mov newControl,ax
        fldcw newControl
        fistp result
        fldcw oldControl}
    return static_cast<unsigned>(result);
}
RF455EffectRead RF455_ParseEffects(const char* file,const void* input,std::size_t size,std::vector<RF455EffectRecord>* records){
    if(!records)return {RF_EFFECT_FORMAT,0,0,0,0};records->clear();
    return readBuffer(file,input,size,[records](RF455EffectRecord&& record,RF455EffectRead&){records->push_back(std::move(record));});
}
RF455EffectRead RF455_ImportEffects(RF455EffectStore* store,const char* file,const void* input,std::size_t size){
    if(!store||!file)return {RF_EFFECT_FORMAT,0,0,0,0};
    try{store->successfulLoads.erase(file);}catch(const std::bad_alloc&){return {RF_EFFECT_IO,0,0,0,0};}
    return readBuffer(file,input,size,[store](RF455EffectRecord&& record,RF455EffectRead& report){publishRecord(*store,std::move(record),report);});
}
RF455EffectRead RF455_LoadEffects(RF455EffectStore* store,const char* file){
    RF455EffectRead report={RF_EFFECT_OK,0,0,0,0};
    if(!store||!file)return {RF_EFFECT_FORMAT,0,0,0,0};
    try{
        // Explicit load invalidates even a previous successful empty-file receipt.
        store->successfulLoads.erase(file);
        EffectFile input(std::fopen(file,"rb"),&std::fclose);
        if(!input)return {RF_EFFECT_MISSING,0,0,1,0};
        unsigned char wire[176];
        for(;;){
            const std::size_t header=std::fread(wire,1,2,input.get());
            if(header==0 && std::feof(input.get()) && !std::ferror(input.get()))break;
            if(header!=2){report.status=std::ferror(input.get())?RF_EFFECT_IO:RF_EFFECT_FORMAT;return report;}
            const unsigned length=get<unsigned short>(wire,0);
            if(length<2||length>sizeof(wire)){report.status=RF_EFFECT_FORMAT;return report;}
            const unsigned remaining=length-2;
            if(std::fread(wire+2,1,remaining,input.get())!=remaining){
                report.status=std::ferror(input.get())?RF_EFFECT_IO:RF_EFFECT_FORMAT;return report;
            }
            RF455EffectRecord record;
            if(!decodeRecord(record,file,wire,length)){report.status=RF_EFFECT_NAME;return report;}
            publishRecord(*store,std::move(record),report);++report.records;
        }
        if(std::fclose(input.release())!=0){report.status=RF_EFFECT_IO;return report;}
        store->successfulLoads.insert(file);
    }catch(const std::bad_alloc&){report.status=RF_EFFECT_IO;}
    return report;
}
RF455EffectRead RF455_LoadEffectFileTable(RF455EffectFiles* table,RF455EffectStore* store,const char* path,bool modeColumn){
    if(!table||!store||!path)return {RF_EFFECT_FORMAT,0,0,0,0};
    // Client 455 x86 RVA 0x52CD60 / 0x52CEA0 loads loose text lists. EFF
    // records keep their separate streaming loader and published owners.
    constexpr std::uint64_t maxListBytes = 2u * 1024u * 1024u;
    const auto input = RF455_GetCharacterRfsCache()->ReadLooseBytes(path, maxListBytes);
    if (input.status == RF455ResourceReadStatus::Unavailable) return {RF_EFFECT_MISSING,0,0,0,0};
    if (input.status != RF455ResourceReadStatus::Ready || !input.bytes) return {RF_EFFECT_IO,0,0,0,0};
    auto* next = input.bytes->data();
    auto left = input.bytes->size();
    RF455EffectRead report={RF_EFFECT_OK,0,0,0,0};std::string id,file,mode;
    try{
        for(;;){
            auto result=token(next,left,id);if(result==TokenResult::End)break;
            if(result!=TokenResult::Value){report.status=tokenError(result);break;}
            if(!modeColumn && id[0]==';')continue; // One comment token, not a whole line.
            result=token(next,left,file);
            if(result!=TokenResult::Value){report.status=tokenError(result);break;}
            if(modeColumn){result=token(next,left,mode);if(result!=TokenResult::Value){report.status=tokenError(result);break;}}
            if(!modeColumn && _access(file.c_str(),0)==-1){++report.missing;continue;}
            if(file.size()+1>=256){++report.ignored;continue;}
            const unsigned key=static_cast<unsigned>(std::atol(id.c_str()));if(table->entries.count(key)){++report.ignored;continue;}
            RF455EffectRead loaded={RF_EFFECT_OK,0,0,0,0};
            if(!store->successfulLoads.count(file))loaded=RF455_LoadEffects(store,file.c_str());
            report.missing+=loaded.status==RF_EFFECT_MISSING;
            if(loaded.status!=RF_EFFECT_OK && loaded.status!=RF_EFFECT_MISSING){report.status=loaded.status;break;}
            // Invalid EFF must not reserve an ID; missing mode-column rows still do.
            const int selected=modeColumn?std::atol(mode.c_str()):0;
            table->entries.emplace(key,RF455EffectFileEntry{file,selected});++report.records;
        }
    }catch(const std::bad_alloc&){report.status=RF_EFFECT_IO;}
    return report;
}
RF455EffectRecord* RF455_FindEffect(RF455EffectStore* store,const char* file,const char* name){const auto f=store->files.find(file);if(f==store->files.end())return nullptr;const auto r=f->second.find(name);return r==f->second.end()?nullptr:r->second.get();}
void RF455_ApplyEffect(RF455CharacterRenderer* owner,RF455MeshStorage* mesh,RF455EffectRecord* r,int grade){if(r)apply(owner,mesh,r->draw.data(),r->texture,r->directory,grade);}
void RF455_ApplyInlineEffect(RF455CharacterRenderer* owner,RF455MeshStorage* mesh,int grade){auto* d=mesh->bytes+5163;const std::string names[]={inlineText(d,68),inlineText(d,96)};apply(owner,mesh,d,names,inlineText(d,132),grade);}
int RF455_ApplyEffectFile(RF455EffectStore* store,RF455CharacterRenderer* owner,RF455CharacterStorage* model,const char* file,int grade){
    if(!model)return 0;const auto* b=reinterpret_cast<const unsigned char*>(model);const unsigned count=get<unsigned>(b,532);if(!count)return 0;const auto f=store->files.find(file);if(f==store->files.end())return 0;auto* meshes=get<RF455MeshStorage*>(b,536);
    for(unsigned i=0;i<count;++i){const auto name=upper(reinterpret_cast<const char*>(meshes[i].bytes));for(auto& record:f->second)if(record.first.empty() || record.first==name)RF455_ApplyEffect(owner,meshes+i,record.second.get(),grade);}
    return 0;
}
RF455EffectStore& RF455_NormalEffects(){static RF455EffectStore store;return store;}

HRESULT RF455_CaptureCharacterTextureReferences(const RF455TextureManager& textures,
    const std::vector<RF455CharacterManager*>& models, const std::vector<RF455EffectStore*>& effects,
    RF455CharacterTextureReferences& output)
{
    try {
        std::unordered_map<IDirect3DTexture9*, const RF455TextureEntry*> entriesByTexture;
        for (auto at = textures.begin; at != textures.end; ++at) {
            const auto* entry = *at;
            if (entry && entry->texture) entriesByTexture.emplace(entry->texture, entry);
        }
        RF455CharacterTextureReferences staged;
        if (!entriesByTexture.empty()) {
            std::unordered_set<unsigned char*> seen;
            const auto capture = [&](unsigned char* bytes, unsigned offset) {
                const auto found = entriesByTexture.find(get<IDirect3DTexture9*>(bytes, offset));
                if (found != entriesByTexture.end() && seen.emplace(bytes + offset).second)
                    staged.sites.push_back({bytes + offset, found->second});
            };

            // 455 RVA 0x51F0A0 publishes six model texture pointers and one alias.
            // 0x527040 can overwrite effect pointers without updating their IDs.
            constexpr unsigned meshFields[] = {5107, 5115, 5119, 5791, 5795, 5799, 5283, 5163 + 120, 5163 + 124};
            for (const auto* manager : models) {
                if (!manager) continue;
                // The lookup cache can contain stale model addresses after erase.
                for (auto at = manager->begin; at != manager->end; ++at) {
                    const auto* model = *at;
                    if (!model) continue;
                    const auto count = get<std::uint32_t>(model->prefix.bytes, 532);
                    auto* meshes = get<RF455MeshStorage*>(model->prefix.bytes, 536);
                    if (!meshes) continue;
                    for (std::uint32_t i = 0; i < count; ++i)
                        for (unsigned offset : meshFields) capture(meshes[i].bytes, offset);
                }
            }
            for (const auto* store : effects) {
                if (!store) continue;
                for (const auto& file : store->files)
                    for (const auto& item : file.second) {
                        if (!item.second) continue;
                        auto* draw = item.second->draw.data();
                        capture(draw, 120);
                        capture(draw, 124);
                    }
            }
        }
        output.sites.swap(staged.sites);
        return S_OK;
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    } catch (const std::length_error&) {
        return E_OUTOFMEMORY;
    }
}

void RF455_ClearCharacterTextureReferences(const RF455CharacterTextureReferences& snapshot) noexcept
{
    for (const auto& site : snapshot.sites) put<IDirect3DTexture9*>(site.field, 0, nullptr);
}

void RF455_RestoreCharacterTextureReferences(const RF455CharacterTextureReferences& snapshot) noexcept
{
    for (const auto& site : snapshot.sites) put(site.field, 0, site.entry->texture);
}
