#pragma once
#include <array>
#include <cstdint>
#include <stdexcept>

//8BC680 zeroes64records of128bytes. Physical rows are retained after
//compaction:reusing the former last row can retain its old tag count.
class RF455LoopSoundRegistry {
public:
    struct Row {std::uint32_t id=0;std::array<std::uint32_t,30> tags{};std::uint32_t count=0;};
private:
    std::array<Row,64> rows{};unsigned active=0;bool ready=false;
public:
    void open(){rows={};active=0;ready=true;}
    void close(){active=0;ready=false;}
    unsigned size()const{return active;}
    const Row& row(unsigned index)const{if(index>=active)throw std::out_of_range("455 tracked sound group");return rows[index];}
    void add(std::uint32_t id,std::uint32_t tag){
        if(!ready)return;
        for(unsigned i=0;i<active;++i)if(rows[i].id==id){
            auto& r=rows[i];if(r.count>=30)return;
            for(unsigned j=0;j<r.count;++j)if(r.tags[j]==tag)return;
            r.tags[r.count++]=tag;return;
        }
        if(active>=64)throw std::out_of_range("455 tracked sound table overflow");
        auto& r=rows[active];r.id=id;
        if(r.count>=30)throw std::out_of_range("455 reused tracked sound row overflow");
        r.tags[r.count++]=tag;++active;
    }
    template<class Stop>bool remove(std::uint32_t id,std::uint32_t tag,Stop stop){
        if(!ready)return false;
        for(unsigned i=0;i<active;++i)if(rows[i].id==id){
            auto& r=rows[i];for(unsigned j=0;j<r.count;++j)if(r.tags[j]==tag){
                stop(id,tag);for(unsigned k=j;k+1<r.count;++k)r.tags[k]=r.tags[k+1];
                if(!--r.count){for(unsigned k=i;k+1<active;++k)rows[k]=rows[k+1];--active;}
                return true;
            }
        }
        return false;
    }
    template<class Stop>void stopAll(Stop stop){
        if(!ready)return;
        for(unsigned i=0;i<active;++i){auto& r=rows[i];if(!r.count)continue;
            for(unsigned j=0;j<r.count;++j)stop(r.id,r.tags[j]);
            r.id=0; //8BD780 does NOT clear its count or the logical group count.
        }
    }
};
static_assert(sizeof(RF455LoopSoundRegistry::Row)==128,"455 tracked loop row");

struct RF455EquipmentEffectOwner {
    void* object=nullptr;std::uint32_t index=0xffffffff;std::uint8_t race=255;
    const float* position=nullptr;float yaw=0;
};
struct RF455EquipmentEffectLocal {
    std::uint32_t index=0xffffffff,action=0;std::uint8_t walkMode=0;
};
//7DBD50 is a shared0.2-second gate. Its clock is read again when storing the
//new timestamp;registering a tracked loop does not itself start/replay sound.
struct RF455EquipmentSoundGate {
    std::uint32_t previousID=0;float previousTime=0;
    template<class Clock,class Play>void play(std::uint32_t id,const float* position,std::uint32_t loop,Clock clock,Play invoke){
        if(previousID!=id||clock()-previousTime>=0.2){previousID=id;previousTime=static_cast<float>(clock());invoke(id,position,loop);}
    }
};
class RF455EquipmentEffectBackend {
public:
    virtual ~RF455EquipmentEffectBackend()=default;
    virtual bool effectExists(std::uint32_t)=0;
    virtual void expireMagic(std::uint32_t,float)=0;
    virtual std::uint32_t startMagic(const RF455EquipmentEffectOwner&,std::uint32_t,bool)=0;
    virtual RF455EquipmentEffectLocal localActor()=0;
    virtual void playWave(std::uint32_t,const float*,std::uint32_t)=0;
    virtual void stopWave(std::uint32_t,std::uint32_t)=0;
    virtual void trackLoop(std::uint32_t,std::uint32_t)=0;
    virtual void untrackLoop(std::uint32_t,std::uint32_t)=0;
};

//46D3D0/46D660. Resource and sound ownership are explicit dependencies;
//recording those dependencies in a probe does not implement their game bodies.
struct RF455EquipmentEffectState {
    std::uint32_t magic=0,sound=0;
    void clear(RF455EquipmentEffectBackend& backend){
        if(magic){backend.expireMagic(magic,0.0f);magic=0;}
        if(sound){backend.stopWave(sound,0);backend.untrackLoop(sound,0);sound=0;}
    }
    void process(const RF455EquipmentEffectOwner& owner,const float* equipmentPosition,std::uint32_t rawMesh,
                 std::uint8_t itemKind,bool renderFlag,std::uint32_t mode,RF455EquipmentEffectBackend& backend){
        if(!owner.object)return;
        const std::uint32_t mesh=(rawMesh&0xff0fffff)|(std::uint32_t(owner.race)<<20);
        const std::uint32_t id=0x50000000u|(mesh<<4)|mode;
        clear(backend);
        if(backend.effectExists(id))magic=backend.startMagic(owner,id,renderFlag);
        const auto local=backend.localActor();if(local.index==0xffffffff)return;
        if(itemKind!=8||!mode)return;
        if(mode==3&&local.index==owner.index){
            sound=id-3;backend.playWave(sound,equipmentPosition,1);backend.trackLoop(sound,0);return;
        }
        if(local.index==owner.index){
            backend.playWave(id,equipmentPosition,0);
            if(mode==2&&local.walkMode==2&&local.action==0x10000001)backend.untrackLoop(id+1,0);
        }else if(mode!=3)backend.playWave(id,equipmentPosition,0);
        sound=0;
    }
};
