#include "client455_effects.h"
#include "client455_effect_constants.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <io.h>

namespace {
template<class T>T get(const void* p,unsigned n){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+n,sizeof(v));return v;}
template<class T>void put(void* p,unsigned n,T v){std::memcpy(static_cast<unsigned char*>(p)+n,&v,sizeof(v));}
void copyFloat(void* out,const void* in){__asm{mov eax,in
    mov edx,out
    fld dword ptr[eax]
    fstp dword ptr[edx]}}
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
bool token(FILE* input,std::string& out){out.clear();int c;do{c=std::fgetc(input);}while(c!=EOF && c<=32);if(c==EOF)return false;do{out.push_back(static_cast<char>(c));if(out.size()>4255)return false;c=std::fgetc(input);}while(c!=EOF && c>32);return true;}
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
    records->clear();RF455EffectRead report={RF_EFFECT_OK,0,0,0,0};const auto* bytes=static_cast<const unsigned char*>(input);std::size_t at=0;
    while(at<size){if(size-at<2){report.status=RF_EFFECT_FORMAT;break;}const unsigned length=get<unsigned short>(bytes+at,0);if(length<2||length>176||length>size-at){report.status=RF_EFFECT_FORMAT;break;}
        std::unique_ptr<RF455EffectRecord> r(new RF455EffectRecord);r->exported.fill(0);put<unsigned short>(r->exported.data(),0,176);r->exported[2]=2;std::memcpy(r->exported.data(),bytes+at,length);construct(*r);r->file=file;
        if(!convert(*r)){report.status=RF_EFFECT_NAME;break;}
        records->push_back(std::move(*r));++report.records;at+=length;
    }return report;
}
RF455EffectRead RF455_ImportEffects(RF455EffectStore* store,const char* file,const void* input,std::size_t size){
    std::vector<RF455EffectRecord> records;auto report=RF455_ParseEffects(file,input,size,&records);
    for(auto& record:records){auto& target=store->files[file];const auto found=target.find(record.mesh);if(found!=target.end()){target.erase(found);++report.replaced;}
        const auto key=record.mesh;target.emplace(key,std::unique_ptr<RF455EffectRecord>(new RF455EffectRecord(std::move(record))));}
    return report;
}
RF455EffectRead RF455_LoadEffects(RF455EffectStore* store,const char* file){
    FILE* input=std::fopen(file,"rb");if(!input)return {RF_EFFECT_MISSING,0,0,1,0};
    if(std::fseek(input,0,SEEK_END)){std::fclose(input);return {RF_EFFECT_IO,0,0,0,0};}const long length=std::ftell(input);if(length<0){std::fclose(input);return {RF_EFFECT_IO,0,0,0,0};}std::rewind(input);
    std::vector<unsigned char> bytes(length);const bool complete=std::fread(bytes.data(),1,bytes.size(),input)==bytes.size();std::fclose(input);if(!complete)return {RF_EFFECT_IO,0,0,0,0};return RF455_ImportEffects(store,file,bytes.data(),bytes.size());
}
RF455EffectRead RF455_LoadEffectFileTable(RF455EffectFiles* table,RF455EffectStore* store,const char* path,bool modeColumn){
    FILE* input=std::fopen(path,"rb");RF455EffectRead report={RF_EFFECT_MISSING,0,0,0,0};if(!input)return report;report.status=RF_EFFECT_OK;std::string id,file,mode;
    while(token(input,id)){
        if(!modeColumn && id[0]==';')continue;
        if(!token(input,file) || (modeColumn && !token(input,mode)))break;
        if(!modeColumn && _access(file.c_str(),0)==-1){++report.missing;continue;}
        if(file.size()+1>=256){++report.ignored;continue;}
        const unsigned key=static_cast<unsigned>(std::atol(id.c_str()));if(table->entries.count(key)){++report.ignored;continue;}
        const int selected=modeColumn?std::atol(mode.c_str()):0;table->entries.emplace(key,RF455EffectFileEntry{file,selected});
        const auto loaded=RF455_LoadEffects(store,file.c_str());report.missing+=loaded.status==RF_EFFECT_MISSING;
        if(loaded.status!=RF_EFFECT_OK && loaded.status!=RF_EFFECT_MISSING){report.status=loaded.status;break;}++report.records;
    }
    if(id.size()>4255||file.size()>4255||mode.size()>4255)report.status=RF_EFFECT_NAME;
    std::fclose(input);return report;
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
