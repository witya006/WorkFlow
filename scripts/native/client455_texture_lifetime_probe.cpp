// Reuse the complete, real registry scenario, including its natural FX drain.
// Conditional observers are absent from its ordinary compilation.
#define RF455_TEXTURE_LIFETIME_PROBE
#define main RF455_RegistryScenarioMain118
#include "client455_nuclear_registry_probe.cpp"
#undef main
#include "r3d3dtex.h"
#include "jmalloc.h"
#include <map>
#include <set>
#include <fstream>
#include <sstream>

namespace {
struct CacheEntry118 {char name[90];DWORD id;void* payload;};
static_assert(sizeof(CacheEntry118)==100&&offsetof(CacheEntry118,payload)==96,"Own cache layout");
struct Owner118 {unsigned real,id;bool particle;int start,count;DWORD flags;};
struct Record118 {unsigned index,start,count,flags,same;std::string name;};
struct Slot118 {int id;std::uintptr_t address;ULONG refs;};
struct State118 {std::string phase;int records,slots,dmalloc;bool recordTable,surfaceTable;std::vector<Record118> rows;std::vector<Slot118> textures;};
struct Warning118 {std::string bytes,phase;std::vector<DWORD> stack;};
struct Pin118 {int id;IDirect3DTexture9* texture;ULONG before=0,after=0,finalRelease=0;};
std::vector<State118> states118;
std::vector<Owner118> owners118;
std::vector<Warning118> warnings118;
std::vector<Pin118> pins118;
std::vector<Pin118> worldPins118;
std::string phase118="scenario";
unsigned traceChecks118=0;
unsigned sharedRecord118=0,sharedStart118=0;
std::string warningCallback118;
void need118(bool ok,const char* text){++traceChecks118;if(!ok)throw std::runtime_error(text);}
std::uintptr_t ownSymbol118(const char* fragment){
    char path[MAX_PATH];GetModuleFileNameA(nullptr,path,MAX_PATH);std::string name(path);name=name.substr(0,name.find_last_of('.'))+".map";
    std::ifstream file(name);need118(bool(file),"Own probe map missing");std::string line;std::uintptr_t preferred=0;
    const auto runtime=reinterpret_cast<std::uintptr_t>(GetModuleHandleA(nullptr));
    while(std::getline(file,line)){
        if(line.find("Preferred load address is ")!=std::string::npos){preferred=std::stoul(line.substr(line.find_last_of(' ')+1),nullptr,16);continue;}
        std::istringstream in(line);std::string section,symbol,value;if(!(in>>section>>symbol>>value))continue;
        if(symbol.find(fragment)==0){need118(preferred!=0,"Own map preferred base");std::uintptr_t at=std::stoul(value,nullptr,16);return runtime+at-preferred;}}
    throw std::runtime_error(std::string("Own static symbol missing:")+fragment);
}
ULONG references118(IDirect3DTexture9* tex){tex->AddRef();return tex->Release();}
State118 snapshot118(const char* phase){
    State118 value;value.phase=phase;value.records=GetNowR3TexCnt();value.slots=GetNowR3D3DTexCnt();value.dmalloc=GetDmallocSize();
    value.recordTable=*reinterpret_cast<void**>(ownSymbol118("?stR3Texture@@"))!=nullptr;value.surfaceTable=*reinterpret_cast<void**>(ownSymbol118("?stR3D3DTexture@@"))!=nullptr;
    if(value.recordTable)for(int i=1;i<value.records;++i){auto* r=reinterpret_cast<R3Texture*>(R3GetTexName(i));need118(r!=nullptr,"Own record access");value.rows.push_back({unsigned(i),r->mStartID,r->mTexNum,r->mFlag,r->mSameCnt,r->mName});}
    if(value.surfaceTable)for(int i=1;i<value.slots;++i){auto* tex=R3GetSurface(i);if(tex)value.textures.push_back({i,reinterpret_cast<std::uintptr_t>(tex),references118(tex)});}
    return value;
}
void quoted118(FILE* f,const std::string& value){std::fputc('"',f);for(unsigned char c:value){if(c=='"'||c=='\\')std::fputc('\\',f);if(c<32||c>=127)std::fprintf(f,"\\u%04x",unsigned(c));else std::fputc(c,f);}std::fputc('"',f);}
void write118(){
    FILE* out=std::fopen("texture-trace.json","wb");need118(out!=nullptr,"Texture trace output");
    std::fprintf(out,"{\"checks\":%u,\"warning_callback_target_bytes\":true,\"warning_ignore_flag\":true,\"warning_without_callback_returns\":true,\"shared_record\":%u,\"shared_start\":%u,\"owners\":[",traceChecks118,sharedRecord118,sharedStart118);
    for(unsigned i=0;i<owners118.size();++i){const auto& x=owners118[i];std::fprintf(out,"%s{\"real\":%u,\"id\":%u,\"particle\":%s,\"start\":%d,\"count\":%d,\"flags\":%u}",i?",":"",x.real,x.id,x.particle?"true":"false",x.start,x.count,x.flags);}
    std::fprintf(out,"],\"states\":[");for(unsigned i=0;i<states118.size();++i){const auto& s=states118[i];if(i)std::fputc(',',out);std::fprintf(out,"{\"phase\":");quoted118(out,s.phase);std::fprintf(out,",\"records\":%d,\"slots\":%d,\"dmalloc\":%d,\"record_table\":%s,\"surface_table\":%s,\"rows\":[",s.records,s.slots,s.dmalloc,s.recordTable?"true":"false",s.surfaceTable?"true":"false");
        for(unsigned j=0;j<s.rows.size();++j){const auto& r=s.rows[j];std::fprintf(out,"%s{\"index\":%u,\"start\":%u,\"count\":%u,\"flags\":%u,\"same\":%u,\"name\":",j?",":"",r.index,r.start,r.count,r.flags,r.same);quoted118(out,r.name);std::fputc('}',out);}
        std::fprintf(out,"],\"textures\":[");for(unsigned j=0;j<s.textures.size();++j){const auto& t=s.textures[j];std::fprintf(out,"%s{\"id\":%d,\"address\":%u,\"refs\":%u}",j?",":"",t.id,unsigned(t.address),t.refs);}std::fprintf(out,"]}");}
    std::fprintf(out,"],\"pins\":[");for(unsigned i=0;i<pins118.size();++i){const auto& p=pins118[i];std::fprintf(out,"%s{\"id\":%d,\"before_refs\":%u,\"after_refs\":%u,\"pin_release_return\":%u}",i?",":"",p.id,p.before,p.after,p.finalRelease);}
    std::fprintf(out,"],\"world_pins\":[");for(unsigned i=0;i<worldPins118.size();++i){const auto& p=worldPins118[i];std::fprintf(out,"%s{\"id\":%d,\"before_refs\":%u,\"after_refs\":%u,\"pin_release_return\":%u}",i?",":"",p.id,p.before,p.after,p.finalRelease);}
    std::fprintf(out,"],\"warnings\":[");for(unsigned i=0;i<warnings118.size();++i){const auto& w=warnings118[i];if(i)std::fputc(',',out);std::fprintf(out,"{\"phase\":");quoted118(out,w.phase);std::fprintf(out,",\"hex\":");quoted118(out,w.bytes);std::fprintf(out,",\"own_stack_rvas\":[");for(unsigned j=0;j<w.stack.size();++j)std::fprintf(out,"%s%u",j?",":"",w.stack[j]);std::fprintf(out,"]}");}std::fprintf(out,"]}\n");std::fclose(out);
}
}
void RF455_TextureWarning118(const char* message){
    Warning118 w;w.phase=phase118;const auto* bytes=reinterpret_cast<const unsigned char*>(message);for(;*bytes;++bytes){char hex[3];std::sprintf(hex,"%02x",unsigned(*bytes));w.bytes+=hex;}
    void* stack[32];const auto n=CaptureStackBackTrace(0,32,stack,nullptr);const auto base=reinterpret_cast<std::uintptr_t>(GetModuleHandleA(nullptr));
    const auto* dos=reinterpret_cast<const IMAGE_DOS_HEADER*>(base);const auto* nt=reinterpret_cast<const IMAGE_NT_HEADERS32*>(base+dos->e_lfanew);const auto end=base+nt->OptionalHeader.SizeOfImage;
    for(unsigned i=0;i<n;++i){auto at=reinterpret_cast<std::uintptr_t>(stack[i]);if(at>=base&&at<end)w.stack.push_back(DWORD(at-base));}warnings118.push_back(std::move(w));
}
void RF455_TextureBeforeCache118(){
    phase118="before_cache";need118(sizeof(R3Texture)==144,"Own registry stride");
    extern int No_warning;
    const int oldIgnore=No_warning;No_warning=0;
    SetWarningMessageProc([](char* value){warningCallback118=value;});Warning("A","B");
    need118(warningCallback118=="AB\x3c\x2d\xb0\xe6\xb0\xed","Target CP949 warning callback bytes");
    No_warning=1;Warning("C","D");need118(warningCallback118=="AB\x3c\x2d\xb0\xe6\xb0\xed","Ignore-warning flag suppresses callback");
    No_warning=0;SetWarningMessageProc(nullptr);Warning("E","F");need118(true,"Target no-callback warning returns without dialog");
    SetWarningMessageProc(warning);No_warning=oldIgnore;
    // Lab-only unbinding after the final capture makes COM observations independent
    // of the device's retained sampler references. No more draws follow.
    for(unsigned i=0;i<8;++i)GetD3dDevice()->SetTexture(i,nullptr);
    const auto cacheAt=ownSymbol118("?stEffectEntityList@@");auto* cache=*reinterpret_cast<CacheEntry118**>(cacheAt);
    need118(ownSymbol118("?GetEffectEntityNum@@")==reinterpret_cast<std::uintptr_t>(&GetEffectEntityNum),"Own map ASLR relocation verified");
    need118(cache!=nullptr,"Actual effect cache");std::set<int> affected;
    for(unsigned i=0;i<GetEffectEntityNum();++i){if(!cache[i].payload)continue;const bool particle=IsParticle(i)!=0;auto* entity=particle?static_cast<CParticle*>(cache[i].payload)->mEntity:static_cast<CEntity*>(cache[i].payload);if(!entity)continue;
        owners118.push_back({i,cache[i].id,particle,entity->mStartTexID,entity->mTexNum,entity->mFlag});need118(!(entity->mFlag&_DO_NOT_MANAGE_TEXTURE),"Independent-cache scope needs separate trace");
        for(int j=0;j<entity->mTexNum;++j)affected.insert(entity->mStartTexID+j);}
    need118(owners118.size()==GetLoadedEffectEntityNum(),"Every actual loaded owner recorded");
    states118.push_back(snapshot118("before_shared"));
    for(int i=1;i<GetNowR3TexCnt();++i){auto* r=reinterpret_cast<R3Texture*>(R3GetTexName(i));if(r->mTexNum<2||!affected.count(r->mStartID)||!affected.count(r->mStartID+1))continue;
        sharedRecord118=i;sharedStart118=r->mStartID;const DWORD old=r->mSameCnt,flags=r->mFlag;char name[128];std::strcpy(name,r->mName);
        phase118="shared_acquire";auto* acquired=R3GetTexInfoR3T(name,flags);need118(acquired&&acquired->mSameCnt==old+1&&acquired->mStartID==sharedStart118,"Actual R3T cache hit increments package counter");states118.push_back(snapshot118("shared_acquired"));
        phase118="shared_first_release";R3ReleaseTextureMem(sharedStart118);states118.push_back(snapshot118("shared_first_release"));need118(acquired->mSameCnt==old&&R3GetSurface(sharedStart118),"First image consumes one shared count without COM release");
        phase118="shared_other_image";acquired=R3GetTexInfoR3T(name,flags);R3ReleaseTextureMem(sharedStart118+1);states118.push_back(snapshot118("shared_other_image"));need118(acquired->mSameCnt==old&&R3GetSurface(sharedStart118+1),"Other image consumes the same package counter");break;}
    need118(sharedRecord118!=0,"Real multi-image effect R3T");std::set<IDirect3DTexture9*> distinct;
    for(int id:affected){auto* tex=R3GetSurface(id);need118(tex!=nullptr,"Actual affected GPU texture");need118(distinct.insert(tex).second,"Shared COM aliases outside selected stock scope");tex->AddRef();Pin118 p;p.id=id;p.texture=tex;p.before=references118(tex);pins118.push_back(p);}
    states118.push_back(snapshot118("before_cache"));phase118="cache_release";
}
void RF455_TextureAfterCache118(){
    states118.push_back(snapshot118("after_cache"));
    for(auto& p:pins118){p.after=references118(p.texture);need118(R3GetSurface(p.id)==nullptr,"Effect cache slot cleared");need118(p.before==p.after+1,"Exactly one engine COM reference released");p.finalRelease=p.texture->Release();need118(p.finalRelease==0,"Last lab pin releases real effect texture");p.texture=nullptr;}
    for(int id=1;id<GetNowR3D3DTexCnt();++id){auto* tex=R3GetSurface(id);if(!tex)continue;tex->AddRef();Pin118 p;p.id=id;p.texture=tex;p.before=references118(tex);worldPins118.push_back(p);}
    states118.push_back(snapshot118("before_world"));
    phase118="world_release";
}
void RF455_TextureAfterWorld118(){
    states118.push_back(snapshot118("after_world"));need118(GetNowR3TexCnt()==1&&GetNowR3D3DTexCnt()==1,"World owner resets global counts");need118(!states118.back().recordTable&&!states118.back().surfaceTable,"World owner releases both global tables");
    for(auto& p:worldPins118){p.after=references118(p.texture);need118(p.before==p.after+1,"World releases exactly one COM reference per remaining slot");p.finalRelease=p.texture->Release();need118(p.finalRelease==0,"Last world pin releases actual texture");p.texture=nullptr;}
    phase118="engine_release";
}
void RF455_TextureAfterEngine118(){states118.push_back(snapshot118("after_engine"));write118();}
int main(){return RF455_RegistryScenarioMain118();}
