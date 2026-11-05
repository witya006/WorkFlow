"""Explicit compiler migration edits,kept separate from confirmed455behavior."""
import re
from pathlib import Path
from audit_client455_normal_character_api import code_only
from compare_client_binaries import WS

def function(raw,name,replacement):
    code=code_only(raw);matches=[]
    for match in re.finditer(rb'\b'+name.encode()+rb'\s*\(',code):
        at=match.end();depth=1
        while at<len(code) and depth:depth+=(code[at]==40)-(code[at]==41);at+=1
        while at<len(code) and code[at] in b' \r\n\t':at+=1
        if at==len(code) or code[at]!=123:continue
        start=code.rfind(b'\n',0,match.start())+1;end=at+1;depth=1
        while end<len(code) and depth:depth+=(code[end]==123)-(code[end]==125);end+=1
        if depth:raise ValueError('Unclosed function:'+name)
        matches.append((start,end))
    if len(matches)!=1:raise ValueError('Nonunique function definition:'+name)
    start,end=matches[0];nl=b'\r\n' if b'\r\n' in raw else b'\n';return raw[:start]+replacement.replace(b'\n',nl)+raw[end:]
def replace(raw,old,new,expected=1):
    if raw.count(old)!=expected:raise ValueError('Changed manual port anchor:'+repr(old[:100]))
    return raw.replace(old,new)
def manual_edits(name,raw):
    before=raw
    if name=='R3Engine/1stclass/r3d3d8.cpp':
        for symbol in ['LoadAndCreateShader','ReleaseVShader','CreateVShader']:raw=function(raw,symbol,b'')
    elif name=='R3Engine/1stclass/r3d3dtex.cpp':raw=replace(raw,b'm_pRenderToSurface->EndScene();',b'm_pRenderToSurface->EndScene(D3DX_FILTER_NONE);')
    elif name=='R3Engine/2ndclass/r3font.h':
        for field in [b'm_dwSavedStateBlock',b'm_dwDrawTextStateBlock']:raw=replace(raw,b'DWORD '+field,b'IDirect3DStateBlock9* '+field)
    elif name=='R3Engine/2ndclass/r3font.cpp':
        for field in [b'm_dwSavedStateBlock',b'm_dwDrawTextStateBlock']:raw=replace(raw,b'm_pd3dDevice->DeleteStateBlock( '+field+b' );',field+b'->Release();')
    elif name=='R3Engine/2ndclass/r3d3dapp.cpp':
        raw=replace(raw,b'Direct3DCreate8',b'Direct3DCreate9');raw=replace(raw,b'D3DENUM_NO_WHQL_LEVEL',b'0')
        raw=replace(raw,b'GetAdapterModeCount( iAdapter )',b'GetAdapterModeCount( iAdapter, D3DFMT_X8R8G8B8 )');raw=replace(raw,b'EnumAdapterModes( iAdapter, iMode, &DisplayMode )',b'EnumAdapterModes( iAdapter, D3DFMT_X8R8G8B8, iMode, &DisplayMode )')
        raw=replace(raw,b'pDevice->d3dCaps.Caps2 & D3DCAPS2_CANRENDERWINDOWED',b'SUCCEEDED(m_pD3D->CheckDeviceType(iAdapter,pDevice->DeviceType,pAdapter->d3ddmDesktop.Format,pAdapter->d3ddmDesktop.Format,TRUE))',2)
    elif name=='R3Engine/d3d/include/d3dutil.h':
        raw=replace(raw,b'TCHAR* strFilename, DWORD* pdwVertexDecl,',b'TCHAR* strFilename, const D3DVERTEXELEMENT9* pdwVertexDecl,');raw=replace(raw,b'DWORD* pdwVertexShader );',b'RF455R3VertexProgram* pdwVertexShader );')
    elif name=='R3Engine/d3d/d3dutil.cpp':raw=function(raw,'D3DUtil_CreateVertexShader',b'#include "client455_r3_shader_assemble.inc"')
    elif name=='R3Engine/1stclass/r3vertexshader.cpp':
        raw=replace(raw,b'DWORD stGrassVertexShader;',b'RF455R3VertexProgram stGrassVertexShader;');raw=replace(raw,b'DWORD stDetailTexVertexShader;',b'RF455R3VertexProgram stDetailTexVertexShader;')
        for symbol,elements in [('stEntityVertexDecl',[(0,2,0),(12,4,10),(16,1,5)]),('stDetailTexVertexDecl',[(0,2,0),(12,2,3),(24,4,10),(28,1,5),(36,1,5)])]:
            pattern=rb'DWORD '+symbol.encode()+rb'\[\]\s*=\s*\{[\s\S]*?\};';replacement=b'const D3DVERTEXELEMENT9 '+symbol.encode()+b'[]={'+b','.join(('{0,%d,%d,0,%d,%d}'%(offset,kind,usage,int(index==4))).encode() for index,(offset,kind,usage) in enumerate(elements))+b',D3DDECL_END()};'
            raw,count=re.subn(pattern,lambda m:replacement,raw)
            if count!=1:raise ValueError('Vertex declaration anchor')
        raw=function(raw,'LoadCreateShader',b'#include "client455_r3_shader_load.inc"')
        raw=replace(raw,b',stEntityVertexDecl,0,SHADERTYPE_VERTEX, &stGrassVertexShader)',b',stEntityVertexDecl, &stGrassVertexShader)');raw=replace(raw,b',stDetailTexVertexDecl,0,SHADERTYPE_VERTEX, &stDetailTexVertexShader)',b',stDetailTexVertexDecl, &stDetailTexVertexShader)')
        for symbol in [b'stGrassVertexShader',b'stDetailTexVertexShader']:raw=replace(raw,b'pd3dDevice->SetVertexShader( '+symbol+b' );',b'RF455_BindR3VertexProgram(pd3dDevice, '+symbol+b');')
        raw=function(raw,'ReleaseVertexShaderList',b'void ReleaseVertexShaderList(){RF455_ReleaseR3VertexProgram(stGrassVertexShader);RF455_ReleaseR3VertexProgram(stDetailTexVertexShader);}')
    return raw,[{'kind':'manual_d3d9_source_edit','file':name}] if before!=raw else []
