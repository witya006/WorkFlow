#pragma once
#include "client455_animation.h"

struct RF455PoseMath {
    RF455MeshMatrixOps matrix;
    void* (__stdcall *slerp)(void*,const void*,const void*,float);
    void* (__stdcall *rotationQuaternion)(void*,const void*);
};
struct RF455PoseSpan {const unsigned char* bytes;std::size_t length;};
struct RF455PoseKeyPair {const unsigned char* left;const unsigned char* right;unsigned index;float ratio;};
enum RF455PoseStatus {RF_POSE_OK=0,RF_POSE_ARGUMENT=1,RF_POSE_BOUNDS=2,RF_POSE_MATRIX=3,RF_POSE_LOAD=4,RF_POSE_SECONDARY=5};
struct RF455PoseScratch {float previous[16],current[16];unsigned initialized;};
struct RF455PoseContext {
    const RF455CharacterLoadContext* load;
    RF455PoseMath math;
    RF455PoseScratch* scratch;
    float blendDuration; // renderer+33844,not frame delta.
    void* ownerContext;
    int (__cdecl *resolveOwner)(void*,const RF455AnimationData*,RF455PoseSpan*);
};
extern "C" {
// signed key times; lowWORD count; count1 still uses a second key if contained
// in the owner allocation. No clamping before first/after last key.
RF455PoseStatus RF455_SelectPoseKeys(const RF455AnimationChannel*,unsigned stride,
    int frame,int linearSearch,const RF455PoseSpan*,RF455PoseKeyPair*);
RF455PoseStatus RF455_ApplyPoseScale(float* matrix,int frame,const RF455MeshStorage*,
    const RF455AnimationData*,const RF455PoseSpan*,const RF455PoseMath*);
RF455PoseStatus RF455_ApplyPoseRotation(float* matrix,int frame,const RF455MeshStorage*,
    const RF455AnimationData*,const RF455PoseSpan*,const RF455PoseMath*);
RF455PoseStatus RF455_ApplyPoseTranslation(float* matrix,int frame,const RF455MeshStorage*,
    const RF455AnimationData*,const RF455PoseSpan*);
// Recovered FrameMove pose/transition/ramp/parent/bone phases. Secondary motion
// with model1184!=0 is explicitly unsupported,never a successful no-op.
// Normal game consumers/secondary motion/profiling owner are separate work.
RF455PoseStatus RF455_UpdateCharacterPose(RF455CharacterStorage*,const RF455PoseContext*);
}
