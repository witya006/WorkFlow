#include "client455_animation.h"
#include <cstdio>
#include <cstring>
#include <cerrno>
#include <malloc.h>
#include <vector>
#include <initializer_list>

namespace {
template<class T>T get(const void* p,unsigned at){T v;std::memcpy(&v,static_cast<const unsigned char*>(p)+at,sizeof(v));return v;}
template<class T>void put(void* p,unsigned at,T v){std::memcpy(static_cast<unsigned char*>(p)+at,&v,sizeof(v));}
std::size_t __cdecl extent(void*,const void* p){return _msize(const_cast<void*>(p));}
bool valid(const RF455AnimationContext* c){return c && c->memory.memory.allocate && c->memory.memory.release && c->memory.extent && c->importedBytes && c->diagnostics.write;}
void importNull(const RF455LegacyDiagnostics* d,const char* name){char text[1024];std::snprintf(text,sizeof(text),"ReadAnimationData( %s ) :NULL",name);d->write(d->context,text);}
int suffix(const char* name){
    if(!name || !*name)return 0;
    std::size_t i=std::strlen(name);while(i && name[i]!='.')--i;
    const char* ext=name+i+1;
    if(!_stricmp(ext,"ANI"))return RF_IMPORTED_ANI;
    if(!_stricmp(ext,"MSH") || !_stricmp(ext,"BN"))return RF_IMPORTED_LEGACY;
    return 0;
}
struct Cursor {
    const unsigned char* bytes;std::size_t length,at=2;std::size_t* failure;
    const unsigned char* take(std::size_t size){
        if(at>length || size>length-at){if(failure)*failure=at+size;return nullptr;}
        const auto* p=bytes+at;at+=size;return p;
    }
};
void* readStream(FILE* file,unsigned size,const RF455MeshMemoryOps& memory,bool& complete){
    void* p=memory.allocate(memory.context,size);complete=false;
    if(p)complete=!size || std::fread(p,1,size,file)==size;
    return p;
}
}
RF455AnimationMemoryOps RF455_CrtAnimationMemoryOps(){return {RF455_CrtMeshMemoryOps(),extent};}
extern "C" void RF455_ConstructAnimation(RF455AnimationStorage* record){
    auto* b=record->bytes;b[5]=0;for(unsigned at:{264u,268u,272u,276u,280u,0u})put<unsigned>(b,at,0);b[4]=0;
}
extern "C" void RF455_DestroyAnimation(RF455AnimationStorage* record,const RF455MeshMemoryOps* memory){
    auto* b=record->bytes;void* p=get<void*>(b,268);if(p){memory->release(memory->context,p);put<void*>(b,268,nullptr);}
    p=get<void*>(b,272);if(p){
        // Cookiearray of32byte descriptors hasnullsub_13 destructors. Key data
        // isborrowed,not recursivelyfreed. Record owns only thecookie allocation.
        memory->release(memory->context,static_cast<unsigned char*>(p)-4);put<void*>(b,272,nullptr);
    }
    p=get<void*>(b,280);if(p){memory->release(memory->context,p);put<void*>(b,280,nullptr);}
}
extern "C" RF455AnimationStatus RF455_DecodeAni(const void* bytes,std::size_t length,
    RF455AniTrackView* tracks,std::size_t capacity,RF455AniView* output,std::size_t* failureEnd){
    if(!bytes || !output)return RF_ANIMATION_ARGUMENT;
    if(!length){if(failureEnd)*failureEnd=1;return RF_ANIMATION_FORMAT;}
    const auto count=*static_cast<const unsigned char*>(bytes);
    if(count && !tracks)return RF_ANIMATION_ARGUMENT;
    if(capacity<count)return RF_ANIMATION_CAPACITY;
    Cursor cursor={static_cast<const unsigned char*>(bytes),length,2,failureEnd};RF455AniView result={count,0,2};const unsigned stride[]={20,16,16,8};
    for(unsigned n=0;n<count;++n){RF455AniTrackView view={};view.header=cursor.take(140);if(!view.header)return RF_ANIMATION_FORMAT;
        const auto maximum=get<std::uint16_t>(view.header,102);if(maximum>result.maxFrame)result.maxFrame=maximum;
        for(unsigned i=0;i<4;++i){const auto* value=cursor.take(2);if(!value)return RF_ANIMATION_FORMAT;view.data.channel[i].count=get<std::uint16_t>(value,0);view.data.channel[i].keys=cursor.take(stride[i]*view.data.channel[i].count);if(!view.data.channel[i].keys)return RF_ANIMATION_FORMAT;}
        tracks[n]=view;
    }
    result.consumed=cursor.at;*output=result;return RF_ANIMATION_OK;
}
extern "C" RF455AnimationStatus RF455_ReadAnimationFile(const char* name,const RF455AnimationContext* context,RF455AnimationBuffer* output){
    if(!name || !valid(context) || !output)return RF_ANIMATION_ARGUMENT;
    const auto& memory=context->memory.memory;unsigned size=0;FILE* file=RF455_GetCharacterRfsCache()->Open(name,&size);void* p=nullptr;bool complete=false;
    if(file){p=readStream(file,size,memory,complete);std::fclose(file);if(complete){const auto allocated=static_cast<unsigned>(context->memory.extent(memory.context,p));*context->importedBytes+=allocated;*output={p,size,allocated,true};return RF_ANIMATION_OK;}if(p)memory.release(memory.context,p);}
    file=std::fopen(name,"rb");
    if(!file){const int error=errno;char text[1024];std::snprintf(text,sizeof(text),"Ani Not Found : FileName = %s [%d]%s",name,error,std::strerror(error));context->diagnostics.write(context->diagnostics.context,text);return RF_ANIMATION_IO;}
    std::fseek(file,0,SEEK_END);const long length=std::ftell(file);std::fseek(file,0,SEEK_SET);if(length<0){std::fclose(file);return RF_ANIMATION_IO;}size=static_cast<unsigned>(length);p=readStream(file,size,memory,complete);std::fclose(file);*context->importedBytes+=size;
    if(!p){importNull(&context->diagnostics,name);return RF_ANIMATION_MEMORY;}
    if(!complete){memory.release(memory.context,p);return RF_ANIMATION_IO;}
    *output={p,size,size,false};return RF_ANIMATION_OK;
}
extern "C" RF455AnimationStatus RF455_ImportCharacterResource(const char* name,int synchronous,
    const RF455AnimationContext* context,RF455ImportedResource* output){
    if(!valid(context) || !name || !output)return RF_ANIMATION_ARGUMENT;
    (void)synchronous; //9352A0 and935320 haveequivalent synchronous dispatch.
    RF455ImportedResource result={};result.kind=static_cast<RF455ImportedKind>(suffix(name));
    if(result.kind==RF_IMPORTED_ANI){const auto status=RF455_ReadAnimationFile(name,context,&result.animation);if(status!=RF_ANIMATION_OK)return status;}
    else if(result.kind==RF_IMPORTED_LEGACY){const auto status=RF455_ImportLegacyFile(name,&context->memory.memory,&context->diagnostics,&result.legacy);if(status!=RF_LEGACY_RUNTIME_OK)return status==RF_LEGACY_RUNTIME_MEMORY?RF_ANIMATION_MEMORY:RF_ANIMATION_IO;}
    else return RF_ANIMATION_TYPE;
    *output=result;return RF_ANIMATION_OK;
}
extern "C" void RF455_ReleaseImportedResource(RF455ImportedResource* imported,const RF455MeshMemoryOps* memory){
    if(imported->kind==RF_IMPORTED_ANI && imported->animation.bytes)memory->release(memory->context,imported->animation.bytes);
    else if(imported->kind==RF_IMPORTED_LEGACY && imported->legacy)RF455_DeleteLegacyModel(imported->legacy,memory);
    *imported={};
}
extern "C" RF455AnimationStatus RF455_FindAnimationMax(RF455AnimationStorage* record,const void* bytes,
    std::size_t available,const RF455LegacyDiagnostics* diagnostics){
    if(!record || !diagnostics || !diagnostics->write)return RF_ANIMATION_ARGUMENT;
    if(!bytes)return RF_ANIMATION_OK;
    const unsigned count=available?*static_cast<const unsigned char*>(bytes):0;std::vector<RF455AniTrackView> tracks(count);RF455AniView view={};std::size_t failed=0;
    const auto status=RF455_DecodeAni(bytes,available,tracks.data(),tracks.size(),&view,&failed);
    if(status!=RF_ANIMATION_OK){char text[1024];std::snprintf(text,sizeof(text),"FindMaxAni:%s:%d:%d",reinterpret_cast<const char*>(record->bytes+5),static_cast<int>(failed),static_cast<int>(available));diagnostics->write(diagnostics->context,text);return status;}
    put(record->bytes,276,view.maxFrame);return RF_ANIMATION_OK;
}
extern "C" int RF455_LoadAnimation(RF455AnimationStorage* record,int synchronous,const RF455AnimationContext* context){
    if(!record || !valid(context))return 0;
    auto* b=record->bytes;if(b[4] || get<unsigned>(b,0))return 1;
    b[4]=1;if(!std::memchr(b+5,0,256))return 0;
    RF455ImportedResource imported={};if(RF455_ImportCharacterResource(reinterpret_cast<const char*>(b+5),synchronous,context,&imported)!=RF_ANIMATION_OK)return 0;
    if(imported.kind!=RF_IMPORTED_ANI){RF455_ReleaseImportedResource(&imported,&context->memory.memory);return 0;} // Own typed guard forinvalid MSH/BN-as-animation domain.
    const auto available=context->memory.extent(context->memory.memory.context,imported.animation.bytes);
    if(RF455_FindAnimationMax(record,imported.animation.bytes,available,&context->diagnostics)!=RF_ANIMATION_OK){RF455_ReleaseImportedResource(&imported,&context->memory.memory);return 0;}
    put(b,268,imported.animation.bytes);put<unsigned>(b,0,1);return 1;
}
extern "C" RF455AnimationStatus RF455_ApplyAniTrack(const RF455AniTrackView* track,RF455KnownModelPrefix* model,
    const RF455MeshMemoryOps* memory,int* matchedIndex){
    if(!track || !track->header || !model || !memory || !memory->allocate || !memory->release || !matchedIndex)return RF_ANIMATION_ARGUMENT;
    if(!std::memchr(track->header,0,100))return RF_ANIMATION_NAME;
    const int count=get<int>(model->bytes,532);auto* meshes=get<RF455MeshStorage*>(model->bytes,536);if(count>0 && !meshes)return RF_ANIMATION_ARGUMENT;
    int index=0;for(;index<count;++index){if(!std::memchr(meshes[index].bytes,0,256))return RF_ANIMATION_NAME;if(!std::strcmp(reinterpret_cast<const char*>(meshes[index].bytes),reinterpret_cast<const char*>(track->header)))break;}
    if(index>=count){*matchedIndex=-1;return RF_ANIMATION_OK;}
    auto* b=meshes[index].bytes;auto* current=get<RF455AnimationData*>(b,5095);
    if(get<std::uint16_t>(track->header,100)){
        if(current){auto* previous=get<RF455AnimationData*>(b,5099);if(previous){memory->release(memory->context,previous);put<void*>(b,5099,nullptr);}
            previous=static_cast<RF455AnimationData*>(memory->allocate(memory->context,32));if(!previous)return RF_ANIMATION_MEMORY;std::memset(previous,0,32);put(b,5099,previous);std::memcpy(previous,current,32);
        }
        if(current){memory->release(memory->context,current);put<void*>(b,5095,nullptr);}
        b[5094]=1;current=static_cast<RF455AnimationData*>(memory->allocate(memory->context,32));if(!current)return RF_ANIMATION_MEMORY;std::memset(current,0,32);put(b,5095,current);std::memcpy(current,&track->data,32);put<unsigned>(b,5103,get<std::uint16_t>(track->header,102));
    }else{
        b[5094]=0;put<unsigned>(b,5103,0);if(current)memory->release(memory->context,current);put<void*>(b,5095,nullptr); // previous descriptor isretained.
    }
    const auto maximum=get<unsigned>(b,5103);if(get<unsigned>(model->bytes,676)<maximum)put(model->bytes,676,maximum);*matchedIndex=index;return RF_ANIMATION_OK;
}
extern "C" RF455AnimationStatus RF455_AttachAnimation(const void* bytes,std::size_t available,
    RF455KnownModelPrefix* model,const RF455MeshMemoryOps* memory,int* lastIndex){
    if(!model || !memory || !lastIndex)return RF_ANIMATION_ARGUMENT;
    if(!bytes){*lastIndex=0;return RF_ANIMATION_OK;}
    const unsigned count=available?*static_cast<const unsigned char*>(bytes):0;std::vector<RF455AniTrackView> tracks(count);RF455AniView view={};
    const auto decoded=RF455_DecodeAni(bytes,available,tracks.data(),tracks.size(),&view,nullptr);if(decoded!=RF_ANIMATION_OK)return decoded;
    int result=0;for(const auto& track:tracks){int matched=-1;const auto status=RF455_ApplyAniTrack(&track,model,memory,&matched);if(status!=RF_ANIMATION_OK)return status;if(matched!=-1)result=matched;}*lastIndex=result;return RF_ANIMATION_OK;
}
extern "C" int RF455_ValidateLegacyModel(const RF455LegacyModel* imported,const RF455LegacyDiagnostics* diagnostics){
    if(!imported || !diagnostics || !diagnostics->write)return 0;
    const auto count=get<std::uint16_t>(imported->bytes,2);const auto* parts=get<const RF455LegacyPart*>(imported->bytes,4);if(count && !parts)return 0;
    for(unsigned n=0;n<count;++n)if(3u*get<std::uint16_t>(parts[n].bytes,394)>64000){
        char text[1024];std::snprintf(text,sizeof(text),"InitVertex : %.100s : %d",reinterpret_cast<const char*>(parts[n].bytes),3*get<std::uint16_t>(parts[n].bytes,394));diagnostics->write(diagnostics->context,text);return 0;
    }
    return 1;
}
extern "C" int RF455_LoadCharacter(RF455CharacterStorage* record,int synchronous,const RF455CharacterLoadContext* context){
    if(!record || !context)return 0;
    auto* b=record->prefix.bytes;if(b[264] || get<unsigned>(b,260))return 1;
    auto* parent=get<RF455KnownModelPrefix*>(b,272);const auto& legacy=context->legacy;const auto& memory=legacy.base.memory;const auto& diagnostic=legacy.diagnostics;
    if(parent){
        if(!get<unsigned>(parent->bytes,260))return 0;
        b[264]=1;RF455RawModelBuffer raw={};RF455_ReadMshFile(reinterpret_cast<const char*>(b+4),&memory,&raw);
        if(!raw.bytes || (raw.length>=6 && !std::memcmp(raw.bytes,"MESH08",6))){
            if(!raw.bytes){char text[1024];std::snprintf(text,sizeof(text),"ImportMeshData( %s ) :NULL",reinterpret_cast<const char*>(b+4));diagnostic.write(diagnostic.context,text);}
            RF455ModelLoadStats stats={};if(RF455_LoadMesh08Model(raw.bytes,raw.length,&record->prefix,&legacy.base,&stats)!=RF_MODEL_OK){--b[264];return 0;} // Early return retainsraw asreference.
        }else{
            RF455LegacyModel* imported=nullptr;std::size_t consumed=0;if(RF455_ReadLegacyModel(raw.bytes,raw.length,&memory,&imported,&consumed)!=RF_LEGACY_OK)return 0;
            if(!RF455_ValidateLegacyModel(imported,&diagnostic)){--b[264];RF455_DeleteLegacyModel(imported,&memory);return 0;} // raw leak isobservable reference behavior.
            RF455LegacyLoadStats stats={};const auto status=RF455_LoadLegacyModel(imported,parent,&record->prefix,&legacy,&stats);RF455_DeleteLegacyModel(imported,&memory);if(status!=RF_LEGACY_RUNTIME_OK)return 0; // Own bounded converter failure domain.
        }
        RF455_RefreshModelTextures(&record->prefix,legacy.base.textures);put<unsigned>(b,260,1);if(raw.bytes)memory.release(memory.context,raw.bytes);return 1;
    }
    b[264]=1;RF455ImportedResource imported={};if(RF455_ImportCharacterResource(reinterpret_cast<const char*>(b+4),synchronous,&context->animation,&imported)!=RF_ANIMATION_OK)return 0;
    if(imported.kind!=RF_IMPORTED_LEGACY){RF455_ReleaseImportedResource(&imported,&context->animation.memory.memory);return 0;} // ANI-as-ObjectData28 isundefined reference domain;own typedreject.
    if(!RF455_ValidateLegacyModel(imported.legacy,&diagnostic)){RF455_ReleaseImportedResource(&imported,&context->animation.memory.memory);return 0;}
    RF455LegacyLoadStats stats={};const auto status=RF455_LoadLegacyModel(imported.legacy,nullptr,&record->prefix,&legacy,&stats);
    if(status!=RF_LEGACY_RUNTIME_OK){RF455_ReleaseImportedResource(&imported,&context->animation.memory.memory);return 0;}
    RF455_RefreshModelTextures(&record->prefix,legacy.base.textures);RF455_ReleaseImportedResource(&imported,&context->animation.memory.memory);put<unsigned>(b,260,1);return 1;
}
extern "C" int RF455_MatchAnimation(RF455AnimationStorage* animation,RF455CharacterStorage* model,const RF455CharacterLoadContext* context){
    if(!animation || !model || !context)return 0;
    auto* parent=get<RF455KnownModelPrefix*>(model->prefix.bytes,272);if(parent && !get<unsigned>(parent->bytes,260))return 0;
    if(!RF455_LoadCharacter(model,0,context) || !RF455_LoadAnimation(animation,0,&context->animation))return 0;
    const auto* bytes=get<const void*>(animation->bytes,268);const auto available=bytes?context->animation.memory.extent(context->animation.memory.memory.context,bytes):0;
    int last=0;if(RF455_AttachAnimation(bytes,available,&model->prefix,&context->legacy.base.memory,&last)!=RF_ANIMATION_OK)return 0;put<unsigned>(model->prefix.bytes,672,160);return 1;
}
