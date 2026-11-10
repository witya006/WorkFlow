#include "gameobject/manager/ccharactermgr.h"
#include "cresobject.h"
#include <cstdio>
#include <cstring>
#include <new>
#include <stdexcept>
#include <vector>

static void check(bool value,const char* why){if(!value)throw std::runtime_error(why);}
static std::vector<unsigned char> read(const char* name){FILE* f=std::fopen(name,"rb");check(f!=nullptr,"fixture open");std::fseek(f,0,SEEK_END);long n=std::ftell(f);check(n>=0,"fixture length");std::rewind(f);std::vector<unsigned char> out(static_cast<std::size_t>(n));check(std::fread(out.data(),1,out.size(),f)==out.size(),"fixture read");std::fclose(f);return out;}
static unsigned word(const void* p){unsigned v;std::memcpy(&v,p,4);return v;}
static void put(void* p,unsigned v){std::memcpy(p,&v,4);}
static void compare(const void* object,const char* fixture,bool timestamp){
    auto expected=read(fixture);std::vector<unsigned char> actual(static_cast<const unsigned char*>(object),static_cast<const unsigned char*>(object)+sizeof(CResObject));
    put(actual.data(),0xc0455000);if(timestamp)put(actual.data()+244,0x01020304);check(actual.size()==expected.size(),"whole-record extent");
    for(unsigned i=0;i<actual.size();++i)if(actual[i]!=expected[i]){std::fprintf(stderr,"%s byte%u actual%u expected%u\n",fixture,i,actual[i],expected[i]);check(false,"independent whole record");}
}
struct Resource: CResObject {
    void setup(unsigned flags){m_dwStatusFlag=flags;m_bIsReceiveFixPositionMsg=1;m_dwReceiveFixPositionMsgTime=0xaabbccdd;m_dwEffectID[0]=0x111;m_dwEffectID[1]=0x222;}
    unsigned flags()const{return m_dwStatusFlag;}
    unsigned receive()const{return m_bIsReceiveFixPositionMsg;}
    unsigned receivedAt()const{return m_dwReceiveFixPositionMsgTime;}
    void offsets(){const unsigned expected[]={80,92,104,116,120,124,128,132,136,140,240,244,248,252,256,272,288,356,460,464,468,472,476,480,484,488,492,500};
        const void* actual[]={&m_vecPos,&m_vecPrevPos,&m_vecRot,&m_dwStatusFlag,&m_pBone,&m_pBBox,&m_dwOldBoneFrame,&m_dwBoneFrame,&m_dwFrameNumForAStopTime,&m_Animation,&m_fScale,&m_dwCreatedTime455,&m_bIsAniInterpolation,&m_pAniIPInfo,&m_stPosYIPInfo,&m_stRotYIPInfo,&m_d3dMaterial,&m_d3dLight,&m_dwLightColor,&m_dwPrevLightColor,&m_fAlphaDensity,&m_bIsBlink,&m_dwBlinkColor455,&m_dwTextColor,&m_bIsReceiveFixPositionMsg,&m_dwReceiveFixPositionMsgTime,&m_dwEffectID,&m_secondaryState455};
        for(unsigned i=0;i<sizeof(expected)/sizeof(expected[0]);++i)check(static_cast<const char*>(actual[i])-reinterpret_cast<const char*>(this)==expected[i],"actual compiled named field offset");}
};
int main(){try{
    check(sizeof(CObject)==80&&sizeof(CAnimation)==100&&sizeof(CResObject)==584,"actual source record sizes");
    alignas(CResObject) unsigned char storage[sizeof(CResObject)];std::memset(storage,0xa5,sizeof(storage));const DWORD before=timeGetTime();
    auto* object=new(storage) CResObject;const DWORD after=timeGetTime();check(word(storage+244)-before<=after-before,"real constructor timeGetTime");compare(object,"constructed.bin",true);object->~CResObject();
    alignas(CResObject) unsigned char sourceStorage[sizeof(CResObject)],copyStorage[sizeof(CResObject)];auto* source=new(sourceStorage) CResObject;
    auto pattern=read("copy-source.bin");check(pattern.size()==sizeof(CResObject),"copy input extent");std::memcpy(sourceStorage+4,pattern.data()+4,sizeof(CResObject)-4);
    std::memset(copyStorage,0xcc,sizeof(copyStorage));auto* copy=new(copyStorage) CResObject(*source);compare(copy,"copied.bin",false);
    source->SetEffectID(0,0);source->SetEffectID(1,0);copy->SetEffectID(0,0);copy->SetEffectID(1,0);copy->~CResObject();source->~CResObject();
    CObject named;char longName[101];std::memset(longName,'Q',100);longName[100]=0;named.SetName(longName);check(std::strlen(named.GetName())==63,"real64byte name truncation");
    char shortName[]="Name455";named.SetName(shortName);check(std::strcmp(named.GetName(),shortName)==0,"short name");
    const auto* bytes=reinterpret_cast<const unsigned char*>(&named);for(unsigned i=16+sizeof(shortName);i<80;++i)check(bytes[i]==0,"SetName clears full64byte storage");
    named.SetName(nullptr);check(std::strcmp(named.GetName(),shortName)==0,"null name leaves prior state");named.SetIndex(17);named.SetServerIndex(23);CObject* base=&named;base->Clear();
    check(named.IsEmpty()&&named.GetServerIndex()==23&&std::strcmp(named.GetName(),shortName)==0,"virtual CObject Clear only invalidates index");
    auto flags=read("flags.bin");check(flags.size()>=8&&std::memcmp(flags.data(),"RO90",4)==0,"flag oracle header");const unsigned count=word(flags.data()+4);check(flags.size()==8+count*24,"flag oracle extent");
    Resource resource;resource.offsets();unsigned retained=0,cleared=0,receiveReset=0;
    for(unsigned i=0;i<count;++i){const auto* row=flags.data()+8+24*i;resource.setup(word(row));const bool enable=word(row+4)!=0;
        if(enable)resource.Enable(word(row+8));else resource.Disable(word(row+8));
        const bool clear=word(row+20)!=0;check(resource.flags()==word(row+12)&&resource.receive()==word(row+16)&&resource.receivedAt()==0xaabbccdd,"actual flag/receive ordering");
        check(resource.GetEffectID(0)==(clear?0:0x111)&&resource.GetEffectID(1)==(clear?0:0x222),"real effect retention/clear branch");
        if(clear)++cleared;else ++retained;if(!resource.receive())++receiveReset;
    }
    resource.SetEffectID(0,0);resource.SetEffectID(1,0);
    object=new(storage) CResObject;object->SetEffectID(0,0x111);object->SetEffectID(1,0x222);object->~CResObject();check(!word(storage+492)&&!word(storage+496),"actual destructor clears both effect IDs");
    FILE* out=std::fopen("result.json","wb");check(out!=nullptr,"result output");std::fprintf(out,"{\"status\":\"PASS\",\"CObject_size\":80,\"CResObject_size\":584,\"named_offsets\":28,\"whole_record_oracles\":2,\"flag_cases\":%u,\"effect_retained_cases\":%u,\"effect_cleared_cases\":%u,\"receive_reset_cases\":%u,\"real_timeGetTime\":true,\"name_capacity\":64,\"virtual_base_clear\":true,\"real_effect_clear_provider\":true,\"live_effect_cache_loaded\":false,\"actual_item_wrapper_binding\":false,\"full_resource_methods\":false,\"full_client\":false}\n",count,retained,cleared,receiveReset);std::fclose(out);return 0;
}catch(const std::exception& e){std::fprintf(stderr,"Resource object:%s\n",e.what());return 1;}}
