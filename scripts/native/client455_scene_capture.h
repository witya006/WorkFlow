#pragma once
#include <d3d9.h>
class CTextureRender;
// Borrowed resource views. InitFullScreenEffect/ReleaseFullScreenEffect own them.
CTextureRender* RF455_GetSceneCaptureTarget(); //455 VA8CD890 /1164038.
CTextureRender* RF455_GetAuxiliarySceneTarget(); //4551164010,512x512 with depth.
IDirect3DTexture9* RF455_GetPerturbationTexture(); //4551163FBC.
// Between scenes, return the borrowed capture texture on success or nullptr.
IDirect3DTexture9* RF455_CaptureCurrentScene(); // RVA 0x4CE020.
// Called during a successful MainGame scene. False means the scene could not be reopened.
bool RF455_CompositeWorldBloom(unsigned quality);
bool RF455_CompositeClassicLobbyBloom(unsigned quality);
