#include "client455_camera.h"
#include <cmath>
#include <cstdio>
#include <cstring>
#include <limits>
#include <new>
#include <stdexcept>
#include <unordered_map>
#include <utility>
namespace {
struct Reader {
    const std::uint8_t* p;std::size_t left;
    bool read(void* out,std::size_t n){if(n>left)return false;if(n)std::memcpy(out,p,n);p+=n;left-=n;return true;}
    template<class T>bool scalar(T& out){return read(&out,sizeof(out));}
    template<class T>bool array(std::vector<T>& out,std::uint32_t count){if(count>left/sizeof(T)||count>0x7fffffffU/sizeof(T)||count>out.max_size())return false;out.resize(count);return read(out.data(),count*sizeof(T));}
};
std::unordered_map<const void*,RF455CameraDocument>& documents(){
    // Camera owners may release from other global destructors. Keep the small
    // registry itself alive through CRT teardown;Release erases each document.
    static auto* values=new std::unordered_map<const void*,RF455CameraDocument>;return *values;
}
bool node(Reader& r,RF455CameraNode& out){
    std::uint32_t positions,rotations;
    return r.read(out.matrix,64)&&r.read(out.position,12)&&r.read(out.rotation,16)&&r.scalar(positions)&&r.scalar(rotations)&&std::uint64_t(positions)*16+std::uint64_t(rotations)*20<=0x7fffffffU&&r.array(out.positions,positions)&&r.array(out.rotations,rotations);
}
}
static_assert(sizeof(RF455CameraPositionKey)==16&&sizeof(RF455CameraRotationKey)==20&&sizeof(RF455CameraFovKey)==20,"455 serialized camera key widths");
bool RF455_ParseCamera(const void* data,std::size_t size,RF455CameraDocument& output){
    if(!data||size<8)return false;
    try{
        Reader r={static_cast<const std::uint8_t*>(data),size};RF455CameraDocument doc;std::uint32_t cameras;
        if(!r.scalar(doc.version)||!std::isfinite(doc.version)||doc.version<1.2||!r.scalar(cameras))return false;
        if(cameras){
            if(!r.scalar(doc.start)||!r.scalar(doc.end)||cameras>r.left/76||cameras>0x7fffffffU/88||cameras>doc.cameras.max_size())return false;
            doc.cameras.resize(cameras);
            for(auto& camera:doc.cameras){
                std::uint32_t count,fovCount=0;
                if(!r.read(camera.name,64)||!r.scalar(camera.fov)||!r.scalar(camera.distance)||!r.scalar(count))return false;
                if(doc.version>=1.3f&&(!r.scalar(fovCount)||!r.array(camera.fovKeys,fovCount)))return false;
                if(count>r.left/100||count>0x7fffffffU/349||count>camera.hierarchy.max_size())return false;camera.hierarchy.resize(count);
                for(auto& object:camera.hierarchy)if(!node(r,object))return false;
            }
            std::uint32_t dummies;if(!r.scalar(dummies)||dummies>r.left/228||dummies>0x7fffffffU/349||dummies>doc.dummies.max_size())return false;doc.dummies.resize(dummies);
            for(auto& dummy:doc.dummies)if(!r.read(dummy.name,64)||!r.read(dummy.parentName,64)||!node(r,dummy.node))return false;
        }
        doc.trailer.assign(r.p,r.p+r.left);output=std::move(doc);return true;
    }catch(const std::bad_alloc&){return false;}catch(const std::length_error&){return false;}
}
bool RF455_LoadCameraFile(const char* path,RF455CameraDocument& doc){
    if(!path)return false;FILE* file=std::fopen(path,"rb");if(!file)return false;
    if(std::fseek(file,0,SEEK_END)){std::fclose(file);return false;}const long bytes=std::ftell(file);
    if(bytes<0||std::fseek(file,0,SEEK_SET)){std::fclose(file);return false;}
    std::vector<std::uint8_t> data;
    try{data.resize(static_cast<std::size_t>(bytes));}catch(const std::bad_alloc&){std::fclose(file);return false;}
    const bool read=std::fread(data.data(),1,data.size(),file)==data.size();std::fclose(file);
    return read&&RF455_ParseCamera(data.data(),data.size(),doc);
}
void RF455_StoreCameraDocument(const void* owner,RF455CameraDocument&& doc){documents()[owner]=std::move(doc);}
const RF455CameraDocument* RF455_GetCameraDocument(const void* owner){auto& all=documents();const auto found=all.find(owner);return found==all.end()?nullptr:&found->second;}
void RF455_ForgetCameraDocument(const void* owner){documents().erase(owner);}
bool RF455_CameraFov(const void* owner,std::size_t index,float seconds,float& result){
    const auto* doc=RF455_GetCameraDocument(owner);if(!doc||index>=doc->cameras.size())return false;
    const auto& camera=doc->cameras[index];float fov=camera.fov;
    if(!camera.fovKeys.empty()){
        const float frame=static_cast<float>(static_cast<double>(seconds)*30.0);std::size_t root=camera.fovKeys.size()-1,next=root;float alpha=0;
        for(std::size_t i=0;i+1<camera.fovKeys.size();++i)if(camera.fovKeys[i].frame<=frame&&camera.fovKeys[i+1].frame>frame){root=i;next=i+1;alpha=static_cast<float>((static_cast<double>(frame)-camera.fovKeys[i].frame)/(static_cast<double>(camera.fovKeys[i+1].frame)-camera.fovKeys[i].frame));break;}
        fov=static_cast<float>((static_cast<double>(camera.fovKeys[next].value[0])-camera.fovKeys[root].value[0])*alpha+camera.fovKeys[root].value[0]);
    }
    result=static_cast<float>(static_cast<double>(fov)*0.788f);return !camera.fovKeys.empty();
}
bool RF455_AdvanceCamera(RF455CameraPlayback& state,float speed,bool paused,const RF455CameraClock& clock){
    float frame=state.nowFrame;
    if(!paused){const float elapsed=static_cast<float>((static_cast<double>(clock.read(clock.context))-state.startTick)*speed);frame=static_cast<float>(static_cast<double>(state.start)/30.0+(state.end>=state.start?elapsed:-static_cast<double>(elapsed)));}
    bool playing=true;
    if(state.end>=state.start){
        const double end=static_cast<double>(state.end)/30.0;
        if(frame>=end){if(state.flag)frame=static_cast<float>(end);else {frame=static_cast<float>(state.start);state.startTick=clock.read(clock.context);}playing=false;}
    }else if(frame<=0.0f){
        if(state.flag)frame=0;else {frame=static_cast<float>(static_cast<double>(state.end)/30.0);state.startTick=clock.read(clock.context);}playing=false;
    }
    state.oldFrame=state.nowFrame;state.nowFrame=frame;return playing;
}
