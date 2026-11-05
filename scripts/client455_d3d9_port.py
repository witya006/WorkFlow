"""Byte-preserving D3D9 source migration;never aliases a D3D8 COM interface."""
import re
from audit_client455_normal_character_api import code_only

TYPES={name+'8':name+'9' for name in ['IDirect3D','IDirect3DDevice','IDirect3DResource','IDirect3DBaseTexture','IDirect3DTexture','IDirect3DCubeTexture','IDirect3DVolumeTexture','IDirect3DVertexBuffer','IDirect3DIndexBuffer','IDirect3DSurface','IDirect3DVolume','IDirect3DSwapChain','LPDIRECT3D','LPDIRECT3DDEVICE','LPDIRECT3DRESOURCE','LPDIRECT3DBASETEXTURE','LPDIRECT3DTEXTURE','LPDIRECT3DCUBETEXTURE','LPDIRECT3DVOLUMETEXTURE','LPDIRECT3DVERTEXBUFFER','LPDIRECT3DINDEXBUFFER','LPDIRECT3DSURFACE','LPDIRECT3DVOLUME','LPDIRECT3DSWAPCHAIN','D3DCAPS','D3DMATERIAL','D3DLIGHT','D3DVIEWPORT','D3DADAPTER_IDENTIFIER']}
SAMPLERS=['ADDRESSU','ADDRESSV','ADDRESSW','BORDERCOLOR','MAGFILTER','MINFILTER','MIPFILTER','MIPMAPLODBIAS','MAXMIPLEVEL','MAXANISOTROPY']
ENGINE_DEFINITIONS=['WIN32','NDEBUG','_MBCS','_LIB','RF_CLIENT_455_HELPER_LOADER','RF_CLIENT_455_WEATHER','RF_CLIENT_455_RESOURCE_IO','RF_CLIENT_455_CLOCK','RF_CLIENT_455_MAP_TIME','RF_CLIENT_455_TIME_COMMANDS','RF_CLIENT_455_ANIMATION_TIMING','RF_CLIENT_455_LOOP_CLOCK','RF_CLIENT_455_X87_MATH']

def pointer_calls(raw):
    code=code_only(raw);result=[]
    for match in re.finditer(rb'->\s*(\w+)\s*\(',code):
        start=match.end();depth=1;at=start;commas=[];brackets=braces=0
        while at<len(code) and depth:
            ch=code[at]
            if ch==40:depth+=1
            elif ch==41:depth-=1
            elif ch==91:brackets+=1
            elif ch==93:brackets-=1
            elif ch==123:braces+=1
            elif ch==125:braces-=1
            elif ch==44 and depth==1 and not brackets and not braces:commas.append(at)
            if brackets<0 or braces<0:raise ValueError('Unbalanced call arguments')
            at+=1
        if depth:raise ValueError('Unterminated pointer call')
        bounds=[start-1,*commas,at-1];args=[raw[a+1:b].strip() for a,b in zip(bounds,bounds[1:])]
        # Joining arguments must not move the next comma onto a // comment.
        args=[v+(b'\r\n' if b'\r\n' in raw else b'\n') if b'//' in v.rsplit(b'\n',1)[-1] else v for v in args]
        if args==[b'']:args=[]
        # Receivers in the current source are identifiers/member chains or
        # ordinary calls. Bound the receiver;never consume a preceding statement.
        left=match.start()-1
        while left>=0 and code[left] in b' \t':left-=1
        nested=0;end=left+1
        while left>=0:
            ch=code[left]
            if ch in b')]':nested+=1
            elif ch in b'([':
                if not nested:break
                nested-=1
            elif not nested and not (ch in b'_.->:' or 48<=ch<=57 or 65<=ch<=90 or 97<=ch<=122):break
            left-=1
        receiver=raw[left+1:end]
        result.append({'method':match[1].decode('ascii'),'args':args,'method_start':match.start(1),'start':left+1,'end':at,'receiver':receiver})
    return result

def migrate(raw):
    edits=[]
    for old,new in TYPES.items():
        pattern=rb'\b'+old.encode()+rb'\b';raw,n=re.subn(pattern,new.encode(),raw)
        if n:edits.append({'kind':'type','old':old,'new':new,'count':n})
    raw,n=re.subn(rb'(?im)^([ \t]*#[ \t]*include[ \t]*[<"])(d3dx?8)([^>"\r\n]*[>"])',lambda m:m[1]+m[2][:-1]+b'9'+m[3],raw)
    if n:edits.append({'kind':'includes','count':n})
    raw,n=re.subn(rb'(?i)(#\s*pragma\s+comment\s*\(\s*lib\s*,\s*")(d3dx?8d?)(\.lib")',lambda m:m[1]+(b'd3dx9_36' if m[2].lower().startswith(b'd3dx') else b'd3d9')+m[3],raw)
    if n:edits.append({'kind':'import_libraries','count':n})
    raw,n=re.subn(rb'\bGetD3dDevice8\b',b'GetD3dDevice9',raw)
    if n:edits.append({'kind':'getter_name','count':n})
    replacements=[]
    arities={'CreateVertexBuffer':5,'CreateIndexBuffer':5,'CreateTexture':7,'CreateCubeTexture':6,'CreateVolumeTexture':8}
    for call in pointer_calls(raw):
        method=call['method'];args=call['args'];name=method;whole=False
        if method in arities and len(args)==arities[method]:args=args+[b'NULL']
        elif method=='SetStreamSource' and len(args)==3:args=args[:2]+[b'0']+args[2:]
        elif method=='SetIndices' and len(args)==2:
            if args[1] not in [b'0',b'0L',b'NULL']:raise ValueError('Nonzero SetIndices base requires caller-specific port')
            args=args[:1]
        elif method=='DrawIndexedPrimitive' and len(args)==5:args=args[:1]+[b'0']+args[1:]
        elif method=='GetRenderTarget' and len(args)==1:args=[b'0']+args
        elif method=='GetBackBuffer' and len(args)==3:args=[b'0']+args
        elif method=='GetDisplayMode' and len(args)==1:args=[b'0']+args
        elif method=='GetFrontBuffer' and len(args)==1:name='GetFrontBufferData';args=[b'0']+args
        elif method=='CreateImageSurface' and len(args)==4:name='CreateOffscreenPlainSurface';args=args[:3]+[b'D3DPOOL_SCRATCH']+args[3:]+[b'NULL']
        elif method=='CreateRenderTarget' and len(args)==6:args=args[:4]+[b'0']+args[4:]+[b'NULL']
        elif method=='CreateDepthStencilSurface' and len(args)==5:args=args[:4]+[b'0',b'FALSE']+args[4:]+[b'NULL']
        elif method=='CheckDeviceMultiSampleType' and len(args)==5:args=args+[b'NULL']
        elif method in ['SetVertexShaderConstant','SetPixelShaderConstant']:name=method+'F';args=[args[0],b'reinterpret_cast<const float*>('+args[1]+b')',args[2]]
        elif method in ['GetVertexShaderConstant','GetPixelShaderConstant']:name=method+'F';args=[args[0],b'reinterpret_cast<float*>('+args[1]+b')',args[2]]
        elif method=='Lock' and len(args)==4:args=[args[0],args[1],b'reinterpret_cast<void**>('+args[2]+b')',args[3]]
        elif method=='SetTextureStageState' and len(args)==3 and args[1].startswith(b'D3DTSS_') and args[1][7:].decode('ascii') in SAMPLERS:name='SetSamplerState';args=[args[0],args[1].replace(b'D3DTSS_',b'D3DSAMP_'),args[2]]
        elif method=='SetRenderTarget' and len(args)==2:name='RF455_SetTargetAndDepth';args=[call['receiver']]+args;whole=True
        elif method=='SetVertexShader' and len(args)==1 and (b'D3DFVF_' in args[0] or args[0] in [b'm_dwFVF',b'dwFVF',b'D3D_EL_2D']):name='RF455_SetFixedVertexFormat';args=[call['receiver']]+args;whole=True
        else:continue
        start=call['start'] if whole else call['method_start'];replacement=name.encode()+b'('+b', '.join(args)+b')';replacements.append((start,call['end'],replacement));edits.append({'kind':'call','method':method,'new':name})
    right=len(raw)+1
    for start,end,value in sorted(replacements,reverse=True):
        if end>right:raise ValueError('Overlapping migration calls need explicit source patch')
        raw=raw[:start]+value+raw[end:];right=start
    return raw,edits
