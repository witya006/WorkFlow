"""Keep the active scene resident across a Reset on the same D3D9 device."""


def port_scene_device(raw, relative, section):
    if relative == 'gameprogress/cgp_maingame.cpp':
        owner = b'CGP_MainGame'
        load = b'_GetLand()->LoadLevel();'
    elif relative == 'gameprogress/cgp_login.cpp':
        owner = b'CGP_LogIn'
        load = br'_GetLand()->LoadLevel( ".\\map\\lobby\\lobby.BSP" );'
    else:
        return raw

    callbacks = (
        (b'::RestoreDeviceObjects( void )', load),
        (b'::InvalidateDeviceObjects( void )', b'_GetLand()->UnloadLevel();'),
    )
    for callback, call in callbacks:
        signature = owner + callback
        start, end = section(raw, signature, signature)
        body = raw[start:end]
        anchor = b'\t' + call
        if body.count(anchor) != 1:
            raise ValueError('Scene device callback changed: ' + repr(signature))
        replacement = b'\tif (!RF455_IsSceneReset455()) ' + call
        if callback.startswith(b'::Restore'):
            replacement = b'\tif (!RF455_IsSceneReset455() && !' + call.rstrip(b';') + b') return E_FAIL;'
        raw = raw[:start] + body.replace(anchor, replacement) + raw[end:]

    return b'extern bool RF455_IsSceneReset455();\r\n' + raw


def port_mainapp_device_results(raw, section):
    for method in (b'RestoreDeviceObjects', b'InvalidateDeviceObjects'):
        signature = b'CMainApp::' + method + b'( void )'
        start, end = section(raw, signature, signature)
        body = raw[start:end]
        call = b'R3D3dWrapper::' + method + b'();'
        if body.count(call) != 1:
            raise ValueError('MainApp device callback changed: ' + repr(signature))
        result = b'const HRESULT deviceResult = ' + call
        if method == b'RestoreDeviceObjects':
            result += b'''
    if (FAILED(deviceResult)) return deviceResult;
    if (RF455_IsSceneReset455()) {
        const HRESULT spriteResult = RF455_RestoreCharacterSprite455(m_pd3dDevice);
        if (FAILED(spriteResult)) return spriteResult;
    } else if (RF455_IsDeviceReplacement455()) {
        const HRESULT characterResult = RF455_RestoreCharacterDeviceReplacement455(m_pd3dDevice);
        if (FAILED(characterResult)) return characterResult;
    }'''
            stage = b'm_pGameProgress->RestoreDeviceObjects();'
            if body.count(stage) != 1:
                raise ValueError('MainApp stage restore boundary changed')
            body = body.replace(stage, b'''{
        const HRESULT stageResult = m_pGameProgress->RestoreDeviceObjects();
        if (FAILED(stageResult)) return stageResult;
    }''')
            callback_result = b'return deviceResult;'
        else:
            result = b'''const HRESULT spriteResult = RF455_IsSceneReset455()
        ? RF455_InvalidateCharacterSprite455(m_pd3dDevice) : S_OK;
    ''' + result
            callback_result = b'''if (FAILED(spriteResult)) return spriteResult;
    if (FAILED(deviceResult) || !RF455_IsDeviceReplacement455()) return deviceResult;

    try {
        std::vector<RF455CharacterManager*> models;
        if (_GetBoneMgr()) {
            for (unsigned i = 0; i < MAX_BONE_MGR; ++i)
                if (auto* manager = _GetBoneMgr()->GetBoneMgr(i)) models.push_back(&manager->native);
        }
        if (_GetMeshMgr()) {
            for (unsigned i = 0; i < MAX_MESH_MGR; ++i)
                if (auto* manager = _GetMeshMgr()->GetMeshMgr(i)) models.push_back(&manager->native);
        }
        return RF455_PrepareCharacterDeviceReplacement455(m_pd3dDevice, models,
            RF455_ReleaseInactiveRvpDeviceResources455());
    } catch (const std::bad_alloc&) {
        return E_OUTOFMEMORY;
    }'''
        if body.count(b'return S_OK;') != 1:
            raise ValueError('MainApp device callback result changed: ' + repr(signature))
        body = body.replace(call, result).replace(b'return S_OK;', callback_result)
        raw = raw[:start] + body + raw[end:]
    anchor = b'CMainApp::RestoreDeviceObjects( void )'
    start, _ = section(raw, anchor, anchor)
    at = raw.rfind(b'HRESULT', 0, start)
    if raw[at:start].strip() != b'HRESULT':
        raise ValueError('MainApp device callback declaration boundary changed')
    raw = raw[:at] + b'''extern bool RF455_IsSceneReset455();
extern bool RF455_IsDeviceReplacement455();

''' + raw[at:]
    return b'''#include "client455_normal_renderer_math.h"
#include "client455_rvp_effects.h"
#include <new>
''' + raw
