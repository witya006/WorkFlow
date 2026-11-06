#include "client455_rvp_actor.h"
#include "anicamera.h"
#include "level.h"
#include "r3bsp.h"
#include "r3util.h"
#include "commonutil.h"
#include "r3math.h"
#include "core.h"
#include <algorithm>
#include <cstring>
#include <stdexcept>

namespace {
bool resolve(RF455RvpActorRuntime& actor,const RF455RvpActor& source,
             ChInterface& renderer,RF455CharacterManager* body) {
    if(!actor.bone)actor.bone=renderer.LookupBone455(source.bone.c_str());
    if(!actor.bone)return false;
    if(!actor.mesh)actor.mesh=renderer.LookupMesh455(body,source.mesh.c_str());
    return actor.mesh!=nullptr;
}
unsigned blendCount(const ObjectMesh& mesh) {
    unsigned result;std::memcpy(&result,mesh.bytes+522,4);return result;
}
}

void RF455_LoadRvpActor(RF455RvpActorRuntime& actor,const RF455RvpActor& source,
    ChInterface& renderer,RF455CharacterManager* body,AnimationManager& animations) {
    actor.color=source.color;
    //8D4020 updates the renderer directory,not the record SetTexPath field.
    std::strncpy(renderer.native.textures.directory,source.texturePath.c_str(),255);
    renderer.RegisterBone455(source.bone.c_str());actor.bone=renderer.LookupBone455(source.bone.c_str());
    renderer.RegisterMesh455(body,source.mesh.c_str(),actor.bone);
    actor.mesh=renderer.LookupMesh455(body,source.mesh.c_str());
    if(!actor.mesh)return;
    auto bounds=source.bone;const auto dot=bounds.find_last_of('.');
    if(dot!=std::string::npos)bounds.resize(dot);bounds+=".BBX";
    if(!renderer.ImportBoundBox(&bounds[0],actor.low,actor.high))renderer.ModelBounds455(actor.mesh,actor.low,actor.high);
    std::swap(actor.low[1],actor.low[2]);std::swap(actor.high[1],actor.high[2]);
    //OneTimeScene registers again;AnimationManager retains its first record.
    for(const auto& name:source.animations)animations.AddAnimation(const_cast<char*>(name.c_str()));
}
void RF455_RvpActorAnimation(RF455RvpActorRuntime& actor,const RF455RvpActor& source,
    ChInterface& renderer,AnimationManager& animations,unsigned selection) {
    actor.previousFrame=actor.frame=0;
    if(source.animations.empty())return;
    selection=(std::min)(selection,static_cast<unsigned>(source.animations.size()-1));
    if(!actor.bone)return;
    renderer.AnimationReset(actor.bone);
    renderer.MatchAnimationToMesh(animations.GetAnimationData(const_cast<char*>(source.animations[selection].c_str())),actor.bone);
    ++actor.animationSelections;
    //8D41E0 does not update the actor's nowAction field.
}
void RF455_SaveRvpPalette(RF455RvpActorRuntime& actor) {
    if(actor.mesh->m_MaxObj>70)throw std::runtime_error("RVP exceeds455 palette part limit70");
    actor.palette.resize(actor.mesh->m_MaxObj);
    for(unsigned i=0;i<actor.mesh->m_MaxObj;++i) {
        auto& saved=actor.palette[i];const auto& mesh=actor.mesh->m_pMesh[i];saved.count=blendCount(mesh);
        //The reference would overwrite its256-byte slot for counts>4. Reject
        //this unsafe domain;do not silently clamp the number of matrices.
        if(saved.count>4)throw std::runtime_error("RVP palette count exceeds original actor slot");
        std::memcpy(saved.bytes.data(),mesh.bytes+(saved.count?646:4830),saved.count?saved.count*64:64);
    }
}
void RF455_RestoreRvpPalette(const RF455RvpActorRuntime& actor) {
    if(actor.palette.size()!=actor.mesh->m_MaxObj)throw std::runtime_error("RVP has no saved actor pose");
    for(unsigned i=0;i<actor.mesh->m_MaxObj;++i) {
        const auto& saved=actor.palette[i];
        std::memcpy(actor.mesh->m_pMesh[i].bytes+(saved.count?646:4830),saved.bytes.data(),saved.count?saved.count*64:64);
    }
}
void RF455_RvpActorFrame(RF455RvpActorRuntime& actor,const RF455RvpActor& source,
    ChInterface& renderer,RF455CharacterManager* body,CAniCamera& camera) {
    if(!resolve(actor,source,renderer,body))return;
    actor.previousFrame=actor.frame;
    actor.frame=float(double(R3GetLoopTime())*30*160+actor.frame);
    actor.bone->m_Frame=static_cast<unsigned>(actor.frame);
    //The published bone frame stays unwrapped for this tick.
    if(actor.bone->m_OMaxFrame+160<actor.bone->m_Frame)actor.frame=160;
    float scaling[4][4];MatrixScale(scaling,source.scale,source.scale,source.scale);
    camera.GetDummyMatrix(actor.matrix,actor.dummy,camera.GetNowFrame());
    MatrixMultiply(actor.matrix,actor.matrix,scaling);
    float low[3],high[3];
    for(unsigned i=0;i<3;++i){low[i]=float(double(actor.low[i])*source.scale);high[i]=float(double(actor.high[i])*source.scale);low[i]=float(double(low[i])+actor.matrix[3][i]);high[i]=float(double(high[i])+actor.matrix[3][i]);}
    actor.visible=IsBBoxInFrustum(low,high)!=0;
    if(!actor.visible)return;
    renderer.FrameMove(actor.bone);renderer.FrameMove(actor.mesh);
    RF455_SaveRvpPalette(actor);++actor.poseUpdates;
    //Bip01 displacement feeds only the still-unaccepted shadow/trace paths.
}
void RF455_RvpActorDraw(RF455RvpActorRuntime& actor,const RF455RvpActor& source,
    ChInterface& renderer,RF455CharacterManager* body,EffectList& effects,CLevel& level) {
    if(!actor.visible||!resolve(actor,source,renderer,body))return;
    actor.renderColor=(source.flags&1)?actor.color:level.mBsp->GetLightFromPoint(actor.matrix[3],2);
    D3DLIGHT9 light;D3DMATERIAL9 material;
    GetMatLightFromColor(&light,&material,actor.renderColor,1);
    light.Direction.x=-light.Direction.x;light.Direction.y=-light.Direction.y;light.Direction.z=-light.Direction.z;
    material.Diffuse.r+=.15f;material.Diffuse.g+=.1f;material.Diffuse.b+=.1f;
    material.Ambient.r+=.2f;material.Ambient.g+=.2f;material.Ambient.b+=.2f;
    const float alpha=float(double(actor.renderColor>>24)/255);if(alpha==0)return;
    renderer.SetAlpha(actor.mesh,alpha);renderer.SetLight(light);renderer.SetMaterial(actor.mesh,material);
    effects.SetEffect(actor.mesh,source.meshId);RF455_RestoreRvpPalette(actor);
    renderer.SetState();renderer.DrawCharacterMat(actor.mesh,reinterpret_cast<D3DXMATRIX*>(actor.matrix),0);
    renderer.UnSetState();++actor.draws;
    //8D4340 has no xrefs and is not called by the ordinary455 Frame/Render.
    //Do not add a fade tick to make the reference's unused setters look useful.
}
