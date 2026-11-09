#pragma once
#include <d3d9.h>
class CTextureRender;
// Borrowed resource views. InitFullScreenEffect/ReleaseFullScreenEffect own them.
CTextureRender* RF455_GetSceneCaptureTarget(); //455 VA8CD890 /1164038.
CTextureRender* RF455_GetAuxiliarySceneTarget(); //4551164010,512x512 with depth.
IDirect3DTexture9* RF455_GetPerturbationTexture(); //4551163FBC.
IDirect3DTexture9* RF455_CaptureCurrentScene(); //4558CE020.
