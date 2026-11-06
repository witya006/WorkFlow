#pragma once
#include <cstddef>
#include <cstdint>
#include <vector>

struct RF455CameraPositionKey {float frame,value[3];};
struct RF455CameraRotationKey {float frame,value[4];};
struct RF455CameraFovKey {float frame,value[4];};
struct RF455CameraNode {
    float matrix[16],position[3],rotation[4];
    std::vector<RF455CameraPositionKey> positions;
    std::vector<RF455CameraRotationKey> rotations;
};
struct RF455CameraEntry {
    char name[64];float fov,distance;
    std::vector<RF455CameraFovKey> fovKeys;
    std::vector<RF455CameraNode> hierarchy;
};
struct RF455CameraDummy {char name[64],parentName[64];RF455CameraNode node;};
struct RF455CameraDocument {
    float version=0;std::uint32_t start=0,end=0;
    std::vector<RF455CameraEntry> cameras;
    std::vector<RF455CameraDummy> dummies;
    std::vector<std::uint8_t> trailer;
};
bool RF455_ParseCamera(const void*,std::size_t,RF455CameraDocument&);
bool RF455_LoadCameraFile(const char*,RF455CameraDocument&);
void RF455_StoreCameraDocument(const void*,RF455CameraDocument&&);
const RF455CameraDocument* RF455_GetCameraDocument(const void*);
void RF455_ForgetCameraDocument(const void*);
bool RF455_CameraFov(const void*,std::size_t camera,float seconds,float& scaledFov);

struct RF455CameraPlayback {
    std::uint32_t start,end,flag;
    float startTick,oldFrame,nowFrame;
};
struct RF455CameraClock {void* context;float(*read)(void*);};
bool RF455_AdvanceCamera(RF455CameraPlayback&,float speed,bool paused,const RF455CameraClock&);
