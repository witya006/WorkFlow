"""Build a derived engine with confirmed455startup fixes;preserve engine033."""
import hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    base=WS/'work/client455-port';root=base/'startup-engine';art=WS/'artifacts/client455-startup-engine';art.mkdir(parents=True,exist_ok=True);root.mkdir(parents=True,exist_ok=True)
    template=base/'CMakeLists.txt';cmakeText=template.read_text();sources=[]
    for match in re.finditer(r'^ "([^"]+\.cpp)"$',cmakeText,re.M):
        source=Path(match[1]);sources.append({'file':source.relative_to(WS).as_posix(),'sha256':sha(source)})
    if len(sources)!=67:raise ValueError('Base engine source list changed')
    previous=json.loads((WS/'inventory/client455-startup-engine-build.json').read_text()) if (WS/'inventory/client455-startup-engine-build.json').exists() else {};old={row['file']:row['sha256'] for row in previous.get('derived_sources',[])};derived=[]
    generationFile=root/'generated-source-hashes.json'
    generated=json.loads(generationFile.read_text()) if generationFile.exists() else {}
    from client455_particle_port import headers,particle_source,entity_source
    particleHeaders=headers(base,root,previous)
    coreInput=base/'source/R3Engine/1stclass/core.h';coreHeader=root/'include/core455.h'
    coreRaw=coreInput.read_bytes();coreAnchor=b'\tD3DXMATRIX mMatProj;'
    coreAt=coreRaw.index(b'\n',coreRaw.index(coreAnchor))+1
    coreRaw=coreRaw[:coreAt]+b'\tBOOL mOrthographic;float mOrthographicScale; //455 state,source-owned layout\n'+coreRaw[coreAt:]
    if coreHeader.exists() and coreHeader.read_bytes()!=coreRaw and sha(coreHeader)!=previous.get('core_header_overlay',{}).get('sha256'):raise ValueError('Preserving changed core declaration')
    if not coreHeader.exists() or coreHeader.read_bytes()!=coreRaw:coreHeader.write_bytes(coreRaw)
    skyInput=base/'source/R3Engine/1stclass/skybox.h';skyHeader=root/'include/skybox455.h'
    skyRaw=skyInput.read_bytes();skyAnchor=b'\tvoid DrawSkyBox('
    if skyRaw.count(skyAnchor)!=1:raise ValueError('Sky loaded getter boundary')
    skyRaw=skyRaw.replace(skyAnchor,b'\tBOOL IsLoaded455()const{return mIsSkyLoad;}\n'+skyAnchor)
    if skyHeader.exists() and skyHeader.read_bytes()!=skyRaw and sha(skyHeader)!=previous.get('sky_header_overlay',{}).get('sha256'):raise ValueError('Preserving changed sky declaration')
    if not skyHeader.exists() or skyHeader.read_bytes()!=skyRaw:skyHeader.write_bytes(skyRaw)
    bspInput=base/'source/R3Engine/1stclass/r3bsp.h';bspHeader=root/'include/r3bsp455.h'
    bspRaw=bspInput.read_bytes();bspAnchor=b'\tvoid SaveExtBsp('
    if bspRaw.count(bspAnchor)!=1:raise ValueError('CBsp owned matrix declaration boundary')
    bspRaw=bspRaw.replace(bspAnchor,(WS/'scripts/native/client455_bsp_fields.inc').read_bytes()+b'\n'+bspAnchor)
    if bspHeader.exists() and bspHeader.read_bytes()!=bspRaw and sha(bspHeader)!=previous.get('bsp_header_overlay',{}).get('sha256'):raise ValueError('Preserving changed own BSP declaration')
    if not bspHeader.exists() or bspHeader.read_bytes()!=bspRaw:bspHeader.write_bytes(bspRaw)
    # One declaration is forced into every engine/client consumer through the
    # existing shared camera overlay. Add only an own inline texture accessor;
    # CSprite layout and virtual dispatch remain unchanged.
    spriteInput=base/'source/R3Engine/2ndclass/2dsprite.h';spriteHeader=root/'include/2dsprite455.h';spriteHeader.parent.mkdir(parents=True,exist_ok=True)
    spriteRaw=spriteInput.read_bytes();spriteAnchor=b'\tchar *GetFileName();'
    if spriteRaw.count(spriteAnchor)!=1:raise ValueError('Own sprite texture accessor anchor')
    spriteRaw=spriteRaw.replace(spriteAnchor,spriteAnchor+b'\r\n\tvoid* GetFrameTexture455()const{return mPageSPrite?(mFrames[0]?mFrameInfo[0][mPage].Tex:nullptr):(mActions?mFrameInfo[mNowAction][mNowFrame].Tex:nullptr);}\r\n')
    if spriteHeader.exists() and spriteHeader.read_bytes()!=spriteRaw and sha(spriteHeader)!=previous.get('sprite_header_overlay',{}).get('sha256'):raise ValueError('Preserving changed own sprite declaration')
    if not spriteHeader.exists() or spriteHeader.read_bytes()!=spriteRaw:spriteHeader.write_bytes(spriteRaw)
    ownedParticleHeader=root/'include/particle455.h'
    particlePrefix=('#include "'+(base/'port_std.hpp').as_posix()+'"\r\n#include "c_vector.h"\r\n'+''.join('#include "'+(WS/row['file']).as_posix()+'"\r\n' for row in particleHeaders)).encode()
    particlePrefix+=('#include "'+bspHeader.as_posix()+'"\r\n').encode()
    particlePrefix=particlePrefix.replace(b'#include "c_vector.h"\r\n',('#include "'+coreHeader.as_posix()+'"\r\n#include "c_vector.h"\r\n').encode(),1)
    particlePrefix+=('#include "'+skyHeader.as_posix()+'"\r\n').encode()
    if ownedParticleHeader.exists() and ownedParticleHeader.read_bytes()!=particlePrefix and sha(ownedParticleHeader)!=previous.get('particle_header_overlay',{}).get('sha256'):raise ValueError('Preserving changed particle prefix')
    if not ownedParticleHeader.exists() or ownedParticleHeader.read_bytes()!=particlePrefix:ownedParticleHeader.write_bytes(particlePrefix)
    cameraHeader=base/'source/R3Engine/2ndclass/anicamera.h';ownedHeader=root/'include/anicamera455.h';ownedHeader.parent.mkdir(parents=True,exist_ok=True)
    header=cameraHeader.read_bytes();anchor=b'void SetNowFrame( DWORD frame);'
    if header.count(anchor)!=1:raise ValueError('Camera seconds declaration boundary changed')
    header=('#include "'+(base/'port_std.hpp').as_posix()+'"\r\n#include "c_vector.h"\r\n').encode()+header.replace(anchor,anchor+b'\r\n\tvoid SetNowFrame(float seconds); //4558D1D90 float argument')
    header=header.replace(b'#include "c_vector.h"\r\n',b'#include "c_vector.h"\r\n'+''.join('#include "'+(WS/row['file']).as_posix()+'"\r\n' for row in particleHeaders).encode(),1)
    firstInclude=('#include "'+(base/'port_std.hpp').as_posix()+'"\r\n').encode()
    header=header.replace(firstInclude,firstInclude+('#include "'+spriteHeader.as_posix()+'"\r\n').encode(),1)
    header=header.replace(firstInclude,firstInclude+('#include "'+coreHeader.as_posix()+'"\r\n').encode(),1)
    header+=('\r\n#include "'+bspHeader.as_posix()+'"\r\n').encode()
    header+=('#include "'+skyHeader.as_posix()+'"\r\n').encode()
    if ownedHeader.exists() and ownedHeader.read_bytes()!=header and sha(ownedHeader)!=previous.get('camera_header_overlay',{}).get('sha256'):raise ValueError('Preserving changed owned camera declaration')
    if not ownedHeader.exists() or ownedHeader.read_bytes()!=header:ownedHeader.write_bytes(header)
    for filename in ['jerror.cpp','r3enginekernel.cpp','r3d3dwrapper.cpp','r3text.cpp','r3d3dtex.cpp','anicamera.cpp','level.cpp','r3d3d8.cpp','rtmovie.cpp','r3util.cpp','r3particle.cpp','entity.cpp','r3sound.cpp','bsp.cpp','core.cpp','skybox.cpp','r3vertexbuffer.cpp']:
        folder='common' if filename=='jerror.cpp' else ('1stclass' if filename in ['r3d3dtex.cpp','r3d3d8.cpp','r3particle.cpp','entity.cpp','bsp.cpp','core.cpp','skybox.cpp','r3vertexbuffer.cpp'] else ('extension' if filename=='rtmovie.cpp' else '2ndclass'))
        source=base/'source/R3Engine'/folder/filename;raw=source.read_bytes()
        if filename=='jerror.cpp':
            from prepare_client455_normal import section
            start,end=section(raw,b'void Warning(',b'void Warning(')
            raw=raw[:start]+(WS/'scripts/native/client455_warning.inc').read_bytes()+raw[end:]
        elif filename=='r3enginekernel.cpp':
            anchor=b'GetR3State()->mbFullScreen = TRUE;'
            if raw.count(anchor)!=1:raise ValueError('Legacy forced fullscreen changed')
            raw=raw.replace(anchor,b'GetR3State()->mRenderBits = 32; // 455:8ED5A0;preserve configured window mode')
            raw=b'#include "client455_movie_state.h"\r\n'+raw
            anchor=b'\tInitCore();'
            if raw.count(anchor)!=1:raise ValueError('Core initialization FOV boundary changed')
            raw=raw.replace(anchor,anchor+b'\r\n\tRF455_SetDefaultCameraFov(0.6f);GetR3State()->mFov=0.6f; //4558C3477/7D')
        elif filename=='r3d3dwrapper.cpp':
            anchor=b'\tCreate(hInstance);'
            if raw.count(anchor)!=1:raise ValueError('Legacy Create wrapper changed')
            raw=raw.replace(anchor,b'\tif(Create(hInstance)!=S_OK) exit(0); // 455:8EDB72..7A;any nonzero result')
        elif filename=='r3text.cpp':
            anchor=b'static CR3Font stCR3Font;'
            if raw.count(anchor)!=1:raise ValueError('Legacy active text boundary changed')
            header=(WS/'scripts/native/client455_font.h').as_posix()
            raw=(f'#include "{header}"\n'.encode()+raw[:raw.index(anchor)]+(WS/'scripts/native/client455_text_bridge.inc').read_bytes())
        elif filename=='r3d3dtex.cpp':
            from prepare_client455_normal import section
            start,end=section(raw,b'void *GetDDSTexFromBuffer(',b'void *GetDDSTexFromBuffer(')
            raw=raw[:start]+(WS/'scripts/native/client455_sprite_texture.inc').read_bytes()+raw[end:]
        elif filename=='bsp.cpp':
            from prepare_client455_normal import section
            raw=b'#include "client455_bsp_light.h"\n'+raw
            start,end=section(raw,b'void CBsp::DrawDynamicLightSub(',b'void CBsp::DrawDynamicLightSub(');raw=raw[:start]+raw[end:]
            start,end=section(raw,b'void CBsp::DrawMagicLightSub(',b'void CBsp::DrawMagicLightSub(');raw=raw[:start]+(WS/'scripts/native/client455_bsp_light.inc').read_bytes()+raw[end:]
            start,end=section(raw,b'short CBsp::GetLeafNum(',b'short CBsp::GetLeafNum(');raw=raw[:start]+(WS/'scripts/native/client455_bsp_leaf.inc').read_bytes()+raw[end:]
            start,end=section(raw,b'void CBsp::ClearVariable()',b'void CBsp::ClearVariable()');body=raw[start:end];at=body.index(b'{')+1
            raw=raw[:start]+body[:at]+b'\nD3DXMatrixIdentity(&mWorldMatrix455);D3DXMatrixIdentity(&mInverseWorldMatrix455);'+body[at:]+raw[end:]
        elif filename=='level.cpp':
            from prepare_client455_normal import section
            raw=b'#include "client455_sky_atmosphere.h"\n'+raw
            raw+=b'\n'+(WS/'scripts/native/client455_sky_atmosphere.inc').read_bytes()
            raw=b'#include "client455_sky_day.h"\n'+raw
            raw+=b'\n'+(WS/'scripts/native/client455_sky_day.inc').read_bytes()
            clockAnchor=b'    RF455_AdvanceDayClock();'
            if raw.count(clockAnchor)!=1:raise ValueError('Ordinary sky day frame boundary')
            raw=raw.replace(clockAnchor,clockAnchor+b'\n    RF455_UpdateSkyNightWeight();\n    RF455_UpdateSunValues();')
            loadFirst,loadLast=section(raw,b'void CLevel::LoadLevel(',b'void CLevel::LoadLevel(');loadBody=raw[loadFirst:loadLast]
            if loadBody.count(b'\tfclose(fp);')!=1:raise ValueError('Map scene flags reset boundary')
            raw=raw[:loadFirst]+loadBody.replace(b'\tfclose(fp);',b'\tfclose(fp);\n    state->mEnvironmentSceneFlags=0;')+raw[loadLast:]
            skyAt=raw.index(b'\t\tstrcat(tempname,"\\\\sky\\\\");');skyFirst=raw.rfind(b'\t\tstrcpy(tempname,state->MapPath);',0,skyAt)
            skyEnd=raw.index(b'\t\tmSkyTexMemSize+= GetNowTexMemSize();',skyAt)
            if skyFirst<0:raise ValueError('Ordinary map sky selection boundary')
            raw=raw[:skyFirst]+(WS/'scripts/native/client455_map_sky.inc').read_bytes()+b'\n'+raw[skyEnd:]
            raw=('#include "'+(WS/'scripts/native/client455_quake.h').as_posix()+'"\r\n').encode()+raw
            first,last=section(raw,b'CLevel::~CLevel()',b'CLevel::~CLevel()')
            raw=raw[:first]+(WS/'scripts/native/client455_level_destroy.inc').read_bytes()+raw[last:]
            first,last=section(raw,b'void CLevel::SetViewMatrix(',b'void CLevel::SetViewMatrix(')
            raw=raw[:first]+(WS/'scripts/native/client455_level_view.inc').read_bytes()+raw[last:]
            first,last=section(raw,b'void CLevel::DrawSkyBoxRender()',b'void CLevel::DrawSkyBoxRender()')
            raw=raw[:first]+(WS/'scripts/native/client455_sky_projection.inc').read_bytes()+raw[last:]
            raw,count=re.subn(rb'(?m)^(\s*)mIsLoadedBsp=TRUE;\r?\n(\s*)ClearDynamicLight',rb'\1RF455_StopCameraSway();\n\1mIsLoadedBsp=TRUE;\n\2ClearDynamicLight',raw)
            if count!=1:raise ValueError('455 successful map-load sway reset boundary')
        elif filename=='core.cpp':
            anchor=b'memset(&stState,0,sizeof(_R3ENGINE_STATE));'
            if raw.count(anchor)!=1:raise ValueError('Core initialization boundary')
            raw=raw.replace(anchor,anchor+b'\n\tstState.mOrthographic=FALSE;stState.mOrthographicScale=5.0f; //4558C3614/20')
        elif filename=='skybox.cpp':
            from prepare_client455_normal import section
            raw=b'#include "client455_sky_day.h"\n#include "client455_sky_fade_math.h"\n#include "client455_sky_atmosphere.h"\n'+raw
            first,last=section(raw,b'void CSkyBox::DrawSkyBox(',b'void CSkyBox::DrawSkyBox(')
            raw=raw[:first]+(WS/'scripts/native/client455_sky_material.inc').read_bytes()+raw[last:]
        elif filename=='r3vertexbuffer.cpp':
            raw+=b'''\n//4558C64F0:prepass binding changes the declaration without clearing its shader.
void RF455_SetVPIPTex1KeepingShader(void* vb,void* ib,IDirect3DVertexDeclaration9* declaration){
    auto* device=GetD3dDevice();
    if(vb!=stOldVB){device->SetStreamSource(0,static_cast<IDirect3DVertexBuffer9*>(vb),0,36);stOldVB=static_cast<BYTE*>(vb);}
    if(ib!=stOldIB){device->SetIndices(static_cast<IDirect3DIndexBuffer9*>(ib));stOldIB=static_cast<BYTE*>(ib);}
    device->SetVertexDeclaration(declaration);
}
'''
        elif filename=='r3d3d8.cpp':
            from prepare_client455_normal import section
            raw=b'#include "client455_sky_atmosphere.h"\n'+raw
            first,last=section(raw,b'HRESULT D3D_R3RestoreDevice()',b'HRESULT D3D_R3RestoreDevice()');body=raw[first:last];anchor=b'\tInitFullScreenEffect();'
            if body.count(anchor)!=1:raise ValueError('Sky resources restore boundary')
            raw=raw[:first]+body.replace(anchor,anchor+b'\n    RF455_CreateSkyResources();')+raw[last:]
            first,last=section(raw,b'HRESULT D3D_R3InvalidateDevice()',b'HRESULT D3D_R3InvalidateDevice()');body=raw[first:last];at=body.index(b'{')+1
            raw=raw[:first]+body[:at]+b'\n    RF455_ReleaseSkyResources();'+body[at:]+raw[last:]
            raw=b'#include "client455_bsp_light.h"\n'+raw
            anchor=b'\tstPd3dDevice=pd3dDevice;'
            if raw.count(anchor)!=1:raise ValueError('BSP light declaration device init boundary')
            raw=raw.replace(anchor,anchor+b'\n\t{const HRESULT hr=RF455_CreateBspLightDeclaration(pd3dDevice);if(FAILED(hr))return hr;}')
            start,end=section(raw,b'HRESULT D3D_R3DeleteDevice()',b'HRESULT D3D_R3DeleteDevice()');body=raw[start:end];at=body.index(b'{')+1
            raw=raw[:start]+body[:at]+b'\n\tRF455_ReleaseBspLightDeclaration();'+body[at:]+raw[end:]
            raw=b'#include "client455_fullscreen_effect.h"\r\n'+raw
            anchor=b'static DWORD stTexSize;'
            if raw.count(anchor)!=1:raise ValueError('Full-screen effect state boundary changed')
            raw=raw.replace(anchor,anchor+b'\r\nstatic float st455FullScreenDensity=0.25f;\r\nvoid RF455_SetFullScreenEffectDensity(float value){st455FullScreenDensity=value;}\r\nfloat RF455_GetFullScreenEffectDensity(){return st455FullScreenDensity;}')
            first,last=section(raw,b'if( stFullScreenEffectState & _FSE_MOTION_BLUR )',b'if( stFullScreenEffectState & _FSE_MOTION_BLUR )')
            raw=raw[:first]+(WS/'scripts/native/client455_fullscreen_motion.inc').read_bytes()+raw[last:]
            first,last=section(raw,b'BOOL R3BeginScene()',b'BOOL R3BeginScene()');body=raw[first:last];anchor=b'\t\tstRToTMain.BeginScene();'
            if body.count(anchor)!=1:raise ValueError('Full-screen Begin result boundary changed')
            body=body.replace(anchor,b'\t\treturn stRToTMain.BeginScene();');raw=raw[:first]+body+raw[last:]
            first,last=section(raw,b'void InitFullScreenEffect()',b'void InitFullScreenEffect()');body=raw[first:last]
            pattern=rb'if\( state->mThisVidMemLevel == 2 \).*?stTexSize = 256;.*?else\s+stTexSize = 512;'
            body,count=re.subn(pattern,b'stTexSize = 512; //4558CD9F4,independent of legacy video-memory level',body,flags=re.S)
            if count!=1:raise ValueError('Full-screen texture size boundary changed')
            raw=raw[:first]+body+raw[last:]
            raw=b'#include "client455_movie_state.h"\r\n'+raw
            raw+=b'\r\nstatic float st455DefaultCameraFov=0.6f;\r\nvoid RF455_SetDefaultCameraFov(float value){st455DefaultCameraFov=value;}\r\nfloat RF455_GetDefaultCameraFov(){return st455DefaultCameraFov;}\r\n'
            first,last=section(raw,b'void SetDefaultFov()',b'void SetDefaultFov()')
            raw=raw[:first]+b'void SetDefaultFov(){SetFov(RF455_GetDefaultCameraFov());}'+raw[last:]
            first,last=section(raw,b'void R3ClearFrameBuffer()',b'void R3ClearFrameBuffer()')
            raw=raw[:first]+(WS/'scripts/native/client455_clear_frame.inc').read_bytes()+raw[last:]
        elif filename=='rtmovie.cpp':
            raw=b'#include "RTMovie.h"\n#include "client455_movie_state.h"\n#include "client455_rvp_runtime.h"\n#include "r3move.h"\nstatic DWORD stRTMovieFlag=0;\n'+(WS/'scripts/native/client455_movie_state.inc').read_bytes()+b'\n'+(WS/'scripts/native/client455_rvp_engine.inc').read_bytes()
        elif filename=='r3util.cpp':
            from prepare_client455_normal import section
            raw=b'#include "client455_sky_fade_math.h"\n'+raw
            first,last=section(raw,b'DWORD GetColorToColorAlpha(',b'DWORD GetColorToColorAlpha(')
            raw=raw[:first]+b'DWORD GetColorToColorAlpha(DWORD source,DWORD destination,float alpha){return RF455_FadeColor(source,destination,alpha);}\n'+raw[last:]
            alphaAnchor=b'(DWORD)(alpha*255)'
            first,last=section(raw,b'void SetFadeFactor(',b'void SetFadeFactor(');body=raw[first:last]
            if body.count(alphaAnchor)!=1:raise ValueError('Fade factor alpha conversion boundary')
            raw=raw[:first]+body.replace(alphaAnchor,b'RF455_FadeAlphaByte(alpha)')+raw[last:]
            first,last=section(raw,b'void SetFadeSky(',b'void SetFadeSky(')
            # FtoDW remains between the two original functions.
            raw=raw[:first]+raw[last:]
            first,last=section(raw,b'BOOL DrawFadeSKy()',b'BOOL DrawFadeSKy()')
            raw=raw[:first]+(WS/'scripts/native/client455_sky_fade.inc').read_bytes()+raw[last:]
            raw=('#include "'+(WS/'scripts/native/client455_quake.h').as_posix()+'"\r\n').encode()+raw
            first=raw.index(b'static float stQuakeTime;');last,end=section(raw,b'void R3EnvironmentQuake(',b'void R3EnvironmentQuake(')
            raw=raw[:first]+(WS/'scripts/native/client455_quake.inc').read_bytes()+raw[end:]
            first,last=section(raw,b'float GetDensityFromPos(',b'float GetDensityFromPos(')
            raw=raw[:first]+(WS/'scripts/native/client455_quake_density.inc').read_bytes()+raw[last:]
            first,last=section(raw,b'BOOL DrawFadeScreen()',b'BOOL DrawFadeScreen()');body=raw[first:last];at=body.index(b'{')+1
            bars=b'\r\n\tif(GetR3State()->mWideOn){const LONG width=LONG(GetR3State()->mScreenXsize),height=LONG(GetR3State()->mScreenYsize);const LONG image=LONG(double(0.55f)*GetR3State()->mScreenXsize);const LONG border=LONG(double(GetR3State()->mScreenYsize)-image)/2;Draw2DRectangle(0,0,width,border,0xff000000);Draw2DRectangle(0,height-border,width,height,0xff000000);}\r\n'
            raw=raw[:first]+body[:at]+bars+body[at:]+raw[last:]
        elif filename=='r3particle.cpp':raw=particle_source(raw)
        elif filename=='entity.cpp':raw=entity_source(raw)
        elif filename=='r3sound.cpp':
            marker=b'static _IM_WAVE_LIST *stIM_WaveList=NULL;'
            if raw.count(marker)!=1:raise ValueError('Immediate sound table source changed')
            start=raw.rfind(b'typedef struct{',0,raw.index(marker))
            if start<0:raise ValueError('Immediate sound record boundary missing')
            raw=raw[:start]+(WS/'scripts/native/client455_sound_im.inc').read_bytes()+b'\r\n#endif\r\n'
        else:
            from prepare_client455_normal import section
            raw=('#include "'+(WS/'scripts/native/client455_camera.h').as_posix()+'"\n#include <utility>\n').encode()+raw
            for method,inc in [(b'CAniCamera::LoadAniCamera(', 'client455_camera_load.inc'),(b'CAniCamera::PlayAniCamera(', 'client455_camera_play.inc')]:
                start,end=section(raw,method,method);raw=raw[:start]+(WS/'scripts/native'/inc).read_bytes()+raw[end:]
            method=b'CAniCamera::ReleaseAniCamera(';start,end=section(raw,method,method);body=raw[start:end];at=body.index(b'{')+1
            body=body[:at]+b'\r\n\tRF455_ForgetCameraDocument(this);'+body[at:];raw=raw[:start]+body+raw[end:]
            anchor=b'SetFov(ani_camera->fov);'
            if raw.count(anchor)!=1:raise ValueError('Camera FOV firstframe boundary changed')
            raw=raw.replace(anchor,b'SetFov(ani_camera->fov*0.788f); //455:8D1B4C')
            start,end=section(raw,b'void CAniCamera::SetNowFrame(',b'void CAniCamera::SetNowFrame(')
            raw=raw[:start]+b'void CAniCamera::SetNowFrame(DWORD seconds){SetNowFrame(float(seconds));}\r\nvoid CAniCamera::SetNowFrame(float seconds){mStartTick=float((double(R3GetTime())-seconds)-double(mPlayStartFrame)/30.0);}\r\n'+raw[end:]
        target=root/'source'/filename;target.parent.mkdir(parents=True,exist_ok=True)
        key=target.relative_to(WS).as_posix()
        if target.exists() and target.read_bytes()!=raw and sha(target) not in {old.get(key),generated.get(key)}:raise ValueError('Preserving changed derived source')
        if not target.exists() or target.read_bytes()!=raw:target.write_bytes(raw)
        generated[key]=sha(target);generationFile.write_text(json.dumps(generated,indent=2)+'\n')
        derived.append({'file':target.relative_to(WS).as_posix(),'sha256':sha(target),'original':source.relative_to(WS).as_posix(),'original_sha256':sha(source)})
        cmakeText=cmakeText.replace(source.as_posix(),target.as_posix())
    cmakeText=cmakeText.replace('R3Engine455','R3Engine455Startup')
    #Weather allocates CParticle/CEntity and must see their expanded declarations.
    #Other helper kernels stay free of legacy camera/global declarations.
    redirected={row['original']:row['file'] for row in derived}
    for row in sources:
        isEngine=(WS/row['file']).is_relative_to(base/'source/R3Engine')
        if not isEngine and row['file']!='scripts/native/client455_weather.cpp':continue
        actual=WS/redirected.get(row['file'],row['file'])
        declaration=ownedHeader if isEngine else ownedParticleHeader
        cmakeText+='\nset_property(SOURCE "'+actual.as_posix()+'" APPEND PROPERTY COMPILE_OPTIONS "/FI'+declaration.as_posix()+'")\n'
    (root/'CMakeLists.txt').write_text(cmakeText)
    info=json.loads((WS/'inventory/msvc-verification.json').read_text());cmake=Path(info['installation_path'])/'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe';build=root/'build';oldLibrary=base/'build-vs2026/Release/R3Engine455.lib';oldHash=sha(oldLibrary)
    config=subprocess.run([str(cmake),'-S',str(root),'-B',str(build),'-G','Visual Studio 18 2026','-A','Win32','-T','v145','-DCMAKE_SYSTEM_VERSION=10.0.26100.0'],capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW);(art/'configure.txt').write_bytes(config.stdout+config.stderr)
    if config.returncode:raise ValueError('Derived engine configure failed')
    result=subprocess.run([str(cmake),'--build',str(build),'--config','Release','--target','R3Engine455Startup','--parallel','4'],capture_output=True,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW);log=art/'build.txt';log.write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Derived engine build:'+str(log))
    library=build/'Release/R3Engine455Startup.lib';objects=list((build/'R3Engine455Startup.dir/Release').glob('*.obj'))
    if len(objects)!=67 or sha(oldLibrary)!=oldHash or any(sha(WS/row['file'])!=row['sha256'] for row in sources):raise ValueError('Engine source/object/baseline drift')
    report={'scope':'Derived source engine with455color32 call and strict Create exit policy;remaining wrapper/camera/console/whole startup semantics open','architecture':'x86','build_exit':0,'objects':67,'library':library.relative_to(WS).as_posix(),'library_sha256':sha(library),'base_cmake':{'file':template.relative_to(WS).as_posix(),'sha256':sha(template)},'base_sources':sources,'derived_sources':derived,'baseline_library':{'file':oldLibrary.relative_to(WS).as_posix(),'sha256':oldHash},'cmake':{'file':(root/'CMakeLists.txt').relative_to(WS).as_posix(),'sha256':sha(root/'CMakeLists.txt')},'log':{'file':log.relative_to(WS).as_posix(),'sha256':sha(log)},'script_sha256':sha(WS/'scripts/build_client455_engine_startup.py'),'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    report['text_bridge']={name:sha(WS/'scripts/native'/name) for name in ['client455_text_bridge.inc','client455_font.h']}
    report['sprite_texture']={'client455_sprite_texture.inc':sha(WS/'scripts/native/client455_sprite_texture.inc')}
    report['warning']={'client455_warning.inc':sha(WS/'scripts/native/client455_warning.inc')}
    report['quake']={name:sha(WS/'scripts/native'/name) for name in ['client455_quake.h','client455_quake.inc','client455_quake_density.inc','client455_level_view.inc']}
    report['bsp_light']={name:sha(WS/'scripts/native'/name) for name in ['client455_bsp_light.h','client455_bsp_fields.inc','client455_bsp_light.inc']}
    report['bsp_leaf']={'client455_bsp_leaf.inc':sha(WS/'scripts/native/client455_bsp_leaf.inc')}
    report['sky_projection']={'client455_sky_projection.inc':sha(WS/'scripts/native/client455_sky_projection.inc')}
    report['sky_fade']={name:sha(WS/'scripts/native'/name) for name in ['client455_sky_fade_math.h','client455_sky_fade.inc']}
    report['sky_material']={name:sha(WS/'scripts/native'/name) for name in ['client455_sky_day.h','client455_sky_day.inc','client455_map_sky.inc','client455_sky_material.inc']}
    report['sky_atmosphere']={name:sha(WS/'scripts/native'/name) for name in ['client455_sky_atmosphere.h','client455_sky_atmosphere.inc']}
    report['core_header_overlay']={'file':coreHeader.relative_to(WS).as_posix(),'sha256':sha(coreHeader),'original':coreInput.relative_to(WS).as_posix(),'original_sha256':sha(coreInput)}
    report['sky_header_overlay']={'file':skyHeader.relative_to(WS).as_posix(),'sha256':sha(skyHeader),'original':skyInput.relative_to(WS).as_posix(),'original_sha256':sha(skyInput)}
    report['bsp_header_overlay']={'file':bspHeader.relative_to(WS).as_posix(),'sha256':sha(bspHeader),'original':bspInput.relative_to(WS).as_posix(),'original_sha256':sha(bspInput)}
    report['camera']={name:sha(WS/'scripts/native'/name) for name in ['client455_camera.h','client455_camera_load.inc','client455_camera_play.inc']}
    report['fullscreen_effect']={name:sha(WS/'scripts/native'/name) for name in ['client455_fullscreen_effect.h','client455_fullscreen_motion.inc']}
    report['movie_state']={name:sha(WS/'scripts/native'/name) for name in ['client455_movie_state.h','client455_movie_state.inc','client455_clear_frame.inc']}
    report['rvp_runtime']={name:sha(WS/'scripts/native'/name) for name in ['client455_rvp_runtime.h','client455_rvp_engine.inc']}
    report['camera_header_overlay']={'file':ownedHeader.relative_to(WS).as_posix(),'sha256':sha(ownedHeader),'original':cameraHeader.relative_to(WS).as_posix(),'original_sha256':sha(cameraHeader)}
    report['sprite_header_overlay']={'file':spriteHeader.relative_to(WS).as_posix(),'sha256':sha(spriteHeader),'original':spriteInput.relative_to(WS).as_posix(),'original_sha256':sha(spriteInput)}
    report['particle_headers']=particleHeaders
    report['particle_header_overlay']={'file':ownedParticleHeader.relative_to(WS).as_posix(),'sha256':sha(ownedParticleHeader),'extra_consumer':'scripts/native/client455_weather.cpp'}
    report['particle_port']={'script':{'file':'scripts/client455_particle_port.py','sha256':sha(WS/'scripts/client455_particle_port.py')}}
    report['immediate_sound']={name:sha(WS/'scripts/native'/name) for name in ['client455_sound_im.h','client455_sound_im.inc']}
    (WS/'inventory/client455-startup-engine-build.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:derived67engine units;033source/library preserved;455color32/Create policy built')
if __name__=='__main__':main()
