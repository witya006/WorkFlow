#include "client455_rvp.h"
#include "client455_camera.h"
#include "client455_character_rfs.h"
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <utility>

namespace {
static_assert(sizeof(long)==4,"RVP atoi/atol conversion requires Windows long32");
bool space(unsigned char c) {return c==' '||c=='\t'||c=='\r'||c=='\n'||c=='\v'||c=='\f';}
std::string lower(std::string text) {
    for(auto& c:text)if(c>='A'&&c<='Z')c=char(c-'A'+'a');
    return text;
}
struct Reader {
    const char* data; std::size_t size, at=0;
    bool next(std::string& text) {
        while(at<size&&space(static_cast<unsigned char>(data[at])))++at;
        if(at==size)return false;
        const auto begin=at;
        while(at<size&&!space(static_cast<unsigned char>(data[at]))) {
            if(data[at]==0)throw std::runtime_error("embedded NUL token");
            ++at;
        }
        if(at-begin>255)throw std::runtime_error("token exceeds455 fscanf buffer");
        text.assign(data+begin,at-begin);return true;
    }
    std::string argument() {
        std::string text;if(!next(text))throw std::runtime_error("missing command argument");return text;
    }
};
std::uint32_t integer(const std::string& text) {
    // Windows long is32 bits; MSVC strtol has the same prefix/overflow contract
    // as the target's atol. This translation unit is verified as x86/MSVC.
    return static_cast<std::uint32_t>(std::strtol(text.c_str(),nullptr,10));
}
float real(const std::string& text) {
    const float result=static_cast<float>(std::strtod(text.c_str(),nullptr));
    if(!std::isfinite(result))throw std::runtime_error("nonfinite numeric domain is unaccepted");
    return result;
}
void fixed(const std::string& text,std::size_t capacity) {
    if(text.size()>=capacity)throw std::runtime_error("actor string exceeds455 member");
}
std::uint32_t named(const RF455RvpDocument& doc,const std::string& name,std::size_t limit) {
    for(std::size_t i=0;i<limit;++i)
        if(!(doc.actors[i].flags&2)&&doc.actors[i].name==name)return static_cast<std::uint32_t>(i);
    return 0xffffffffu;
}
std::uint32_t magic(const RF455RvpDocument& doc,std::uint32_t index) {
    for(std::size_t i=0;i<doc.actors.size();++i)
        if((doc.actors[i].flags&2)&&doc.actors[i].magicIndex==index)return static_cast<std::uint32_t>(i);
    return 0xffffffffu;
}
}

bool RF455_ParseRvp(const void* input,std::size_t bytes,RF455RvpDocument& output,std::string* error,
                    const RF455CameraDocument* camera) {
    if(error)error->clear();
    if(!input&&bytes){if(error)*error="null input";return false;}
    try {
        if(input)if(const auto end=std::memchr(input,0x1a,bytes))
            bytes=static_cast<const char*>(end)-static_cast<const char*>(input); //fopen rt DOS EOF
        Reader reader={static_cast<const char*>(input),bytes};RF455RvpDocument doc;
        unsigned mode=0;float frame=0;std::string token;
        while(reader.next(token)) {
            token=lower(token);
            if(token=="[object]"){mode=1;continue;}
            if(token=="[preparetrack]"){mode=2;continue;}
            if(token=="[track]"){mode=3;continue;}
            if(!mode){++doc.ignoredTokens;continue;}
            if(mode==1) {
                if(token[0]=='*') {
                    RF455RvpActor actor;
                    if(token=="*magic") {actor.flags=2;actor.magicIndex=integer(reader.argument());}
                    else {fixed(token,32);actor.name=token;actor.mesh=reader.argument();fixed(actor.mesh,48);}
                    doc.actors.push_back(std::move(actor));continue;
                }
                if(doc.actors.empty()){++doc.ignoredTokens;continue;}
                auto& actor=doc.actors.back();
                if(token=="collision"){actor.flags|=4;continue;}
                if(token=="shadow"){actor.flags|=8;continue;}
                if(token=="color") {
                    const auto r=static_cast<std::int32_t>(integer(reader.argument()))/2;
                    const auto g=static_cast<std::int32_t>(integer(reader.argument()))/2;
                    const auto b=static_cast<std::int32_t>(integer(reader.argument()))/2;
                    actor.color=0xff000000u|(std::uint32_t(r)<<16)|(std::uint32_t(g)<<8)|std::uint32_t(b);
                    actor.flags|=1;continue;
                }
                if(token=="trace_on_off") {
                    actor.traceAction=integer(reader.argument());actor.traceOn=integer(reader.argument());
                    actor.traceOff=integer(reader.argument());continue;
                }
                if(token=="mesh_id"){actor.meshId=integer(reader.argument());continue;}
                if(token=="scale"){actor.scale=real(reader.argument());continue;}
                if(token=="wav_dist"){actor.waveDistance=real(reader.argument());continue;}
                if(token=="x_angle"){actor.xAngle=real(reader.argument());continue;}
                if(token=="y_angle"){actor.yAngle=real(reader.argument());continue;}
                if(token=="texpath"){actor.texturePath=reader.argument();fixed(actor.texturePath,48);continue;}
                if(token=="bone"||token=="char_dummy") {actor.bone=reader.argument();fixed(actor.bone,48);continue;}
                if(token=="wav") {
                    actor.wave=reader.argument();if(actor.waveDistance==0)actor.waveDistance=200;continue;
                }
                if(token=="sword_trace"){actor.swordTrace=reader.argument();continue;}
                if(token=="magic_id"){actor.magicId=reader.argument();continue;}
                if(token=="ani") {
                    auto name=reader.argument();fixed(name,48);
                    if(actor.animations.size()==6)throw std::runtime_error("animation member overflow");
                    actor.animations.push_back(std::move(name));continue;
                }
                if(token=="char_link") {
                    actor.texturePath=reader.argument();fixed(actor.texturePath,48);
                    const auto link=named(doc,actor.texturePath,doc.actors.size()-1);
                    if(link!=0xffffffffu)actor.linkedActor=link;continue;
                }
                if(token=="map_dummy") {
                    actor.mesh=reader.argument();fixed(actor.mesh,48);actor.mapDummy=actor.mesh;continue;
                }
                ++doc.ignoredTokens;continue;
            }
            if(mode==3&&token=="*frame"){frame=real(reader.argument());continue;}
            if(mode==2) {
                if(token=="total_frame") {
                    const auto value=real(reader.argument());
                    if(value<0||double(value)>4294967295.0)throw std::runtime_error("total_frame domain");
                    doc.totalFrame=static_cast<std::uint32_t>(value);continue;
                }
                if(token=="no_camera"){doc.flags|=4;continue;}
                if(token=="wide"){doc.flags|=1;continue;}
                if(token=="logo"){doc.flags|=2;continue;}
                if(token=="screen"){doc.flags|=8;continue;}
                if(token[0]=='*') {
                    const auto actor=named(doc,token,doc.actors.size());
                    // Target warns and continues WITHOUT consuming the dummy
                    // token if the actor was not found.
                    if(actor==0xffffffffu){++doc.ignoredTokens;continue;}
                    doc.actors[actor].mapDummy=reader.argument();continue;
                }
            }
            RF455RvpTrack track;track.frame=frame;
            if(token=="camera"){track.kind=RF455RvpKind::Camera;track.reference=lower(reader.argument());}
            else if(token=="fade_in"||token=="fade_out") {
                track.kind=token=="fade_in"?RF455RvpKind::FadeIn:RF455RvpKind::FadeOut;
                track.value=integer(reader.argument());
            } else if(token=="ani"||token=="char_fade_in"||token=="char_fade_out") {
                track.kind=token=="ani"?RF455RvpKind::Animation:
                    token=="char_fade_in"?RF455RvpKind::CharacterFadeIn:RF455RvpKind::CharacterFadeOut;
                track.actor=named(doc,reader.argument(),doc.actors.size());
                if(track.actor==0xffffffffu){++doc.ignoredTokens;continue;}
                track.value=integer(reader.argument());
            } else if(token=="magic"||token=="throw") {
                track.kind=token=="magic"?RF455RvpKind::Magic:RF455RvpKind::Throw;
                track.actor=magic(doc,integer(reader.argument()));
                if(track.actor==0xffffffffu){++doc.ignoredTokens;continue;}
                if(track.kind==RF455RvpKind::Throw) {
                    track.reference=reader.argument();
                    if(!camera)throw std::runtime_error("throw needs camera dummy names");
                    const auto stripped=track.reference.substr(1);
                    const bool dummy=std::any_of(camera->dummies.begin(),camera->dummies.end(),
                        [&](const RF455CameraDummy& row){return row.name==stripped;});
                    if(!dummy) {
                        const auto target=named(doc,track.reference,doc.actors.size()-1);
                        if(target==0xffffffffu){++doc.ignoredTokens;continue;}
                        track.attachment=reader.argument();fixed(track.attachment,32);
                    }
                }
            } else if(token=="quake") {
                track.kind=RF455RvpKind::Quake;track.first=real(reader.argument());track.second=real(reader.argument());
            } else if(token=="wav") {
                track.kind=RF455RvpKind::Wave;track.reference=reader.argument();
                track.resource=reader.argument();track.first=real(reader.argument());
            } else if(token=="blur"||token=="timer_rate") {
                track.kind=token=="blur"?RF455RvpKind::Blur:RF455RvpKind::TimerRate;
                track.first=real(reader.argument());
            } else {++doc.ignoredTokens;continue;}
            doc.tracks.push_back(std::move(track));
        }
        output=std::move(doc);return true;
    } catch(const std::exception& ex) {if(error)*error=ex.what();return false;}
}

bool RF455_LoadRvp(const char* path,RF455RvpDocument& output,std::string* error,
                   const RF455CameraDocument* camera) {
    if(!path){if(error)*error="null filename";return false;}
    // Client 455 x86 RVA 0x4D69E0 opens RVP as a loose text file. The
    // parser applies its DOS EOF rule to the retained original bytes.
    constexpr std::uint64_t maxBytes = 64u * 1024u * 1024u;
    const auto source = RF455_GetCharacterRfsCache()->ReadLooseBytes(path, maxBytes);
    if (source.status == RF455ResourceReadStatus::Unavailable) {
        if (error) *error = "open RVP";
        return false;
    }
    if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) {
        if (error) *error = "read RVP";
        return false;
    }
    return RF455_ParseRvp(source.bytes->data(), source.bytes->size(), output, error, camera);
}

bool RF455_RvpInterpolate(const RF455RvpDocument& doc,std::size_t cursor,
                         RF455RvpKind kind,float frame,float& value) {
    if(cursor>doc.tracks.size()||!cursor)return false;
    auto before=cursor;
    while(before&&doc.tracks[before-1].kind!=kind)--before;
    if(!before)return false;--before;
    auto after=cursor;
    while(after<doc.tracks.size()) {
        if(doc.tracks[after].frame==-1)return false;
        if(doc.tracks[after].kind==kind)break;
        ++after;
    }
    if(after==doc.tracks.size())return false;
    const auto& first=doc.tracks[before];const auto& second=doc.tracks[after];
    // Keep the target divide-by-zero/NaN result for duplicate key frames. The
    // caller decides whether its numeric domain has been accepted.
    const float amount=static_cast<float>((double(frame)-first.frame)/(double(second.frame)-first.frame));
    value=static_cast<float>(double(amount)*(double(second.first)-first.first)+first.first);return true;
}
