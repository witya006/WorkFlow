#include "client455_rvp.h"
#include "client455_camera.h"
#include <cmath>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <stdexcept>

static void check(bool value,const char* message){if(!value)throw std::runtime_error(message);}
static std::uint32_t bits(float value){std::uint32_t out;std::memcpy(&out,&value,4);return out;}
static void string(FILE* file,const std::string& value) {
    std::fputc('"',file);
    for(unsigned char c:value) {
        if(c<32||c>=127||c=='"'||c=='\\')std::fprintf(file,"\\u%04x",unsigned(c));
        else std::fputc(c,file);
    }
    std::fputc('"',file);
}
static void dump(FILE* file,const RF455RvpDocument& doc) {
    std::fprintf(file,"{\"flags\":%u,\"totalFrame\":%u,\"ignoredTokens\":%zu,\"actors\":[",
        doc.flags,doc.totalFrame,doc.ignoredTokens);
    bool first=true;
    for(const auto& a:doc.actors) {
        if(!first)std::fputc(',',file);first=false;
        std::fprintf(file,"{\"flags\":%u,\"color\":%u,\"meshId\":%u,\"magicIndex\":%u,"
            "\"linkedActor\":%u,\"traceAction\":%u,\"traceOn\":%u,\"traceOff\":%u,"
            "\"scale\":%u,\"waveDistance\":%u,\"xAngle\":%u,\"yAngle\":%u",
            a.flags,a.color,a.meshId,a.magicIndex,a.linkedActor,a.traceAction,a.traceOn,a.traceOff,
            bits(a.scale),bits(a.waveDistance),bits(a.xAngle),bits(a.yAngle));
        const std::string* values[]={&a.name,&a.mesh,&a.bone,&a.texturePath,&a.wave,&a.swordTrace,&a.magicId,&a.mapDummy};
        const char* names[]={"name","mesh","bone","texturePath","wave","swordTrace","magicId","mapDummy"};
        for(unsigned i=0;i<8;++i){std::fprintf(file,",\"%s\":",names[i]);string(file,*values[i]);}
        std::fputs(",\"animations\":[",file);bool begin=true;
        for(const auto& name:a.animations){if(!begin)std::fputc(',',file);begin=false;string(file,name);}
        std::fputs("]}",file);
    }
    std::fputs("],\"tracks\":[",file);first=true;
    for(const auto& track:doc.tracks) {
        if(!first)std::fputc(',',file);first=false;
        std::fprintf(file,"{\"kind\":%u,\"frame\":%u,\"first\":%u,\"second\":%u,\"actor\":%u,\"value\":%u,\"reference\":",
            unsigned(track.kind),bits(track.frame),bits(track.first),bits(track.second),track.actor,track.value);
        string(file,track.reference);std::fputs(",\"resource\":",file);string(file,track.resource);
        std::fputs(",\"attachment\":",file);string(file,track.attachment);std::fputc('}',file);
    }
    std::fputs("]}\n",file);
}
static void malformed() {
    const char* rejected[]={"[track] camera", "[object] *unit", "[object] *a mesh color 1 2",
        "[track] *frame 1e999", "[object] *a m ani a ani b ani c ani d ani e ani f ani g"};
    RF455RvpDocument sentinel;sentinel.flags=0xabcdef12;std::string error;
    for(auto input:rejected) {
        check(!RF455_ParseRvp(input,std::strlen(input),sentinel,&error),"malformed accepted");
        check(sentinel.flags==0xabcdef12&&!error.empty(),"nontransactional failure");
    }
    std::string longToken(256,'a');check(!RF455_ParseRvp(longToken.data(),longToken.size(),sentinel),"fscanf overflow");
    const char nul[]={'a',0,'b'};check(!RF455_ParseRvp(nul,sizeof(nul),sentinel),"embedded NUL");
    check(!RF455_ParseRvp(nullptr,1,sentinel),"null data");
    check(RF455_ParseRvp(nullptr,0,sentinel)&&sentinel.actors.empty()&&sentinel.tracks.empty(),"empty document");
}
static void interpolation() {
    RF455RvpDocument doc;RF455RvpTrack a,b,other;
    a.kind=b.kind=RF455RvpKind::Blur;a.frame=0;a.first=.2f;b.frame=10;b.first=.8f;
    other.kind=RF455RvpKind::Camera;other.frame=3;doc.tracks={a,other,b};float value=123;
    check(!RF455_RvpInterpolate(doc,0,RF455RvpKind::Blur,5,value)&&value==123,"no previous key");
    check(RF455_RvpInterpolate(doc,2,RF455RvpKind::Blur,5,value)&&value==.5f,"skip unrelated key");
    check(RF455_RvpInterpolate(doc,1,RF455RvpKind::Blur,20,value)&&std::abs(value-1.4f)<1e-6f,"unclamped interpolation");
    value=123;check(!RF455_RvpInterpolate(doc,3,RF455RvpKind::Blur,5,value)&&value==123,"no next key");
    doc.tracks[2].frame=0;check(RF455_RvpInterpolate(doc,1,RF455RvpKind::Blur,1,value)&&std::isinf(value),"duplicate-key division");
    doc.tracks[1].frame=-1;check(!RF455_RvpInterpolate(doc,1,RF455RvpKind::Blur,0,value),"sentinel stops search");
    doc.tracks={a,b};doc.tracks[0].frame=16777216.f;doc.tracks[1].frame=16777220.f;
    doc.tracks[0].first=-0.1234567f;doc.tracks[1].first=9.876543f;
    check(RF455_RvpInterpolate(doc,1,RF455RvpKind::Blur,16777218.f,value),"float boundary interpolation");
    check(bits(value)==bits(float(double(.5f)*(double(doc.tracks[1].first)-doc.tracks[0].first)+doc.tracks[0].first)),"x87 store boundary");
}
int main() {
    try {
        malformed();interpolation();std::ifstream inputs("inputs.txt");check(bool(inputs),"input list");
        std::string path;unsigned files=0,actors=0,tracks=0;
        while(std::getline(inputs,path)) {
            if(path.empty())continue;RF455RvpDocument doc;std::string error;
            RF455CameraDocument camera;RF455CameraDummy dummy{};std::strcpy(dummy.name,"Dummy");camera.dummies.push_back(dummy);
            check(RF455_LoadRvp(path.c_str(),doc,&error,&camera),error.c_str());
            const auto output=path+".semantic.json";FILE* file=std::fopen(output.c_str(),"wb");check(file!=nullptr,"semantic output");
            dump(file,doc);check(!std::fclose(file),"close semantic output");++files;
            actors+=unsigned(doc.actors.size());tracks+=unsigned(doc.tracks.size());
        }
        FILE* output=std::fopen("result.json","wb");check(output!=nullptr,"result");
        std::fprintf(output,"{\"status\":\"PASS\",\"files\":%u,\"actors\":%u,\"tracks\":%u,"
            "\"malformed_transactional\":true,\"cursor_interpolation\":true,\"full_RVP_player\":false,\"full_Tutorial\":false}\n",files,actors,tracks);
        std::fclose(output);return 0;
    } catch(const std::exception& error) {std::fprintf(stderr,"RVP probe: %s\n",error.what());return 1;}
}
