"""Derived455 vertex normals and real material/entity lighting consumers."""
from compare_client_binaries import WS
from prepare_client455_normal import section


def replace(raw,old,new):
    if raw.count(old)!=1:raise ValueError('Lighting port boundary '+repr(old))
    return raw.replace(old,new)


def vertex_header(raw):
    raw=replace(raw,b'#define D3DFVF_R3VERTEX_TEX1  (D3DFVF_XYZ |D3DFVF_DIFFUSE| D3DFVF_TEX1)',b'#define D3DFVF_R3VERTEX_TEX1  (D3DFVF_XYZ |D3DFVF_NORMAL|D3DFVF_DIFFUSE| D3DFVF_TEX1)')
    newline=b'\r\n' if b'\r\n' in raw else b'\n'
    raw=replace(raw,newline.join([b'\tfloat y,z;',b'\tDWORD color;',b'\tfloat u,v;']),newline.join([b'\tfloat y,z;',b'\tfloat nx,ny,nz; //455 entity vertex normal',b'\tDWORD color;',b'\tfloat u,v;']))
    return raw+b'\nstatic_assert(sizeof(_D3DR3VERTEX_TEX1)==36,"455 entity vertex stride");\n'


def entity(raw):
    raw=b'#include "client455_entity_normals.h"\n'+raw
    raw=replace(raw,b'\tBOOL IsLightEnable=0;',b'\tVector3f* normals455=(Vector3f*)Dmalloc(static_vertexnum*sizeof(Vector3f));\n\tif(normals455)memset(normals455,0,static_vertexnum*sizeof(Vector3f));\n\tBOOL IsLightEnable=0;')
    anchor=b'\t\ttemp_v_num = static_v_cnt;'
    raw=replace(raw,anchor,anchor+b'''
        //The accumulator persists between material groups,including normals
        //already normalized by the preceding group,as in4558E1464/8E1684.
        for(int face455=0;face455<read_entity_m_group[i].face_num;++face455){
            const WORD id455=f_id[read_entity_m_group[i].face_start_id+face455];
            const auto& face=entity_face[id455];Vector4f normal455;
            GetNormal(normal455,vertex[v_id[face.v_start_id]],vertex[v_id[face.v_start_id+1]],vertex[v_id[face.v_start_id+2]]);
            for(unsigned corner=0;corner<face.v_num;++corner){const WORD id=v_id[face.v_start_id+corner];
                for(unsigned axis=0;axis<3;++axis)normals455[id][axis]+=normal455[axis];}
        }
''')
    anchor=b'\t\t\t\tstatic_vertexbp[static_v_cnt].z = vertex[v_id[vr_id]][2];'
    raw=replace(raw,anchor,anchor+b'''
                float* normal455=normals455[v_id[vr_id]];
                if(normal455[0]==0&&normal455[1]==0&&normal455[2]==0)normal455[1]=1;
                RF455_NormalizeEntityNormal(normal455);
                static_vertexbp[static_v_cnt].nx=normal455[0];static_vertexbp[static_v_cnt].ny=normal455[1];static_vertexbp[static_v_cnt].nz=normal455[2];
''')
    start,end=section(raw,b'BOOL CEntity::LoadEntity(',b'BOOL CEntity::LoadEntity(');body=raw[start:end]
    anchor=b'\tmStaticVertexBuffer.VPUnLock();';body=replace(body,anchor,anchor+b'\n\tDfree(normals455);')
    return raw[:start]+body+raw[end:]


def render_entity(raw):
    start,end=section(raw,b'void CEntity::SetVertexShaderID(',b'void CEntity::SetVertexShaderID(');raw=raw[:start]+raw[end:]
    anchor=b'#include "r3VertexShader.h"';raw=replace(raw,anchor,anchor+b'\n#include "client455_entity_lighting.inc"')
    start,end=section(raw,b'BOOL CEntity::DrawEntity(',b'BOOL CEntity::DrawEntity(');body=raw[start:end]
    first=body.index(b'\tD3DMATERIAL9 mtrl;');last=body.index(b'\tSetVPIPTex1(',first)
    body=body[:first]+b'''    const float alpha=float(double(color>>24)/255.0);
    if(mFlag&_ENTITY_Z_DISABLE)pd3dDevice->SetRenderState(D3DRS_ZENABLE,FALSE);
    prepareEntityLighting455(mFlag,mMapColor,color);
'''+body[last:]
    body=replace(body,b'pd3dDevice->SetTextureStageState( 0, D3DTSS_COLOROP,   D3DTOP_MODULATE2X );',b'//455 preparation already selected MODULATE or MODULATE2X.')
    first=body.index(b'\tif( mFlag & _ENTITY_MAP_COLOR )');last=body.index(b'\tfor(i=0;',first);body=body[:first]+body[last:]
    first=body.index(b'\tBlendOff();');last=body.index(b'\tif( mFlag & _ENTITY_Z_DISABLE )',first)
    body=body[:first]+b'''    BlendOff();
    pd3dDevice->SetRenderState(D3DRS_ALPHABLENDENABLE,FALSE);
    pd3dDevice->SetRenderState(D3DRS_COLORVERTEX,FALSE);
    pd3dDevice->SetRenderState(D3DRS_SPECULARENABLE,TRUE);
    if(!(mFlag&0x40)&&(color&0xffffffu)==0xffffffu)pd3dDevice->SetRenderState(D3DRS_EMISSIVEMATERIALSOURCE,D3DMCS_MATERIAL);
'''+body[last:]
    raw=raw[:start]+body+raw[end:]
    start,end=section(raw,b'BOOL CEntity::DrawEntityVS(',b'BOOL CEntity::DrawEntityVS(');body=raw[start:end]
    body=replace(body,b'\tSetVertexShaderID(e_list,color);',b'\tprepareEntityShader455(mFlag,mMapColor,mAddFrame,e_list,world_mat,color);')
    body=replace(body,b'pd3dDevice->SetTextureStageState( 0, D3DTSS_COLOROP,   D3DTOP_MODULATE2X );',b'pd3dDevice->SetTextureStageState(0,D3DTSS_COLOROP,(mFlag&0x40)?D3DTOP_MODULATE:D3DTOP_MODULATE2X);')
    body=replace(body,b'\tBlendOff();',b'\tBlendOff();\n\tpd3dDevice->SetVertexShader(nullptr);pd3dDevice->SetPixelShader(nullptr);')
    return raw[:start]+body+raw[end:]


def material(raw):
    raw=b'#include "client455_entity_lighting.h"\n#include "client455_sky_lighting.h"\n'+raw
    raw+=b'\nstatic BOOL bumpEnvironment455=FALSE;\nvoid RF455_SetLightingCaps(const D3DCAPS9* caps){bumpEnvironment455=(caps->TextureOpCaps>>21)&1;}\nBOOL RF455_HasBumpEnvironment(){return bumpEnvironment455;}\n'
    start,end=section(raw,b'void GetBumpFactor(',b'void GetBumpFactor(')
    raw=raw[:start]+b'''void GetBumpFactor(Vector4f factor){
    const float a=float(double(R3GetTime())*2),ca=float(cos(double(a)));
    factor[0]=float(double(ca)*double(.01f));
    const float b=float(double(R3GetTime())*2),sb=float(sin(double(b)));
    factor[1]=float(double(sb)*double(-.01f));
    const float c=float(double(R3GetTime())*2),sc=float(sin(double(c)));
    factor[2]=float(double(sc)*double(.01f));
    const float d=float(double(R3GetTime())*2),cd=float(cos(double(d)));
    factor[3]=float(double(cd)*double(.01f));
}
'''+raw[end:]
    #Only the main pre/after pair uses the new checked capability. Other callers
    #are separate contracts and remain listed as gaps.
    for token in [b'void PreRenderOneLayer(',b'void AfterRenderOneLayer(']:
        start,end=section(raw,token,token);body=raw[start:end]
        body=replace(body,b'if( mat->m_Layer[1].m_dwFlag & _MAT_ENV_BUMP)',b'if((mat->m_Layer[1].m_dwFlag&_MAT_ENV_BUMP)&&RF455_HasBumpEnvironment())')
        if token.startswith(b'void Pre'):
            body=replace(body,b'if( !(mat->m_Layer[0].m_dwFlag & _UV_METAL) )',b'if(!(mat->m_Layer[0].m_dwFlag&0xAu))')
            anchor=b'\t\t//env';at=body.index(anchor);body=body[:at]+b'\t\tpd3dDevice->SetRenderState(D3DRS_ALPHATESTENABLE,FALSE);\n'+body[at:]
        else:
            anchor=b'\t\t//env';at=body.index(anchor);last=body.index(b'\n\t}',at)
            body=body[:at]+b'''        pd3dDevice->SetTextureStageState(0,D3DTSS_TEXCOORDINDEX,0);
        pd3dDevice->SetTextureStageState(1,D3DTSS_TEXCOORDINDEX,1);
        pd3dDevice->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_DISABLE);
        pd3dDevice->SetTextureStageState(0,D3DTSS_TEXTURETRANSFORMFLAGS,D3DTTFF_DISABLE);
        pd3dDevice->SetTextureStageState(1,D3DTSS_TEXTURETRANSFORMFLAGS,D3DTTFF_DISABLE);
        pd3dDevice->SetTextureStageState(0,D3DTSS_COLORARG1,D3DTA_TEXTURE);
        pd3dDevice->SetTextureStageState(0,D3DTSS_COLORARG2,D3DTA_DIFFUSE);
        pd3dDevice->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);
        pd3dDevice->SetTextureStageState(0,D3DTSS_ALPHAARG2,D3DTA_DIFFUSE);
        pd3dDevice->SetTextureStageState(0,D3DTSS_ALPHAARG1,D3DTA_TEXTURE);
        pd3dDevice->SetTextureStageState(0,D3DTSS_ALPHAOP,D3DTOP_SELECTARG2);
        pd3dDevice->SetTextureStageState(1,D3DTSS_COLORARG1,D3DTA_TEXTURE);
        pd3dDevice->SetTextureStageState(1,D3DTSS_COLORARG2,D3DTA_CURRENT);
        pd3dDevice->SetTextureStageState(1,D3DTSS_COLOROP,D3DTOP_MODULATE2X);
        pd3dDevice->SetRenderState(D3DRS_CULLMODE,D3DCULL_CCW);
        pd3dDevice->SetRenderState(D3DRS_TEXTUREFACTOR,RF455_GetSkyTintColor());
'''+body[last:]
        ending=body.rfind(b'}')
        tail=b'\n    if(mat->m_dwFlag&0x40u)MultiTexOff();\n' if token.startswith(b'void Pre') else b'\n    if(mat->m_dwFlag&0x40u){MultiTexOn();pd3dDevice->SetTextureStageState(0,D3DTSS_COLOROP,D3DTOP_MODULATE);}\n    pd3dDevice->SetTextureStageState(0,D3DTSS_COLORARG2,D3DTA_DIFFUSE);\n'
        body=body[:ending]+tail+body[ending:]
        raw=raw[:start]+body+raw[end:]
    return raw


def shader(raw):
    raw=b'#include "client455_entity_lighting.h"\n#include "r3util.h"\n'+raw
    #The pinned declaration includes normal/float3 at12,color at24,UV at28.
    old=b'const D3DVERTEXELEMENT9 stEntityVertexDecl[]={{0,0,2,0,0,0},{0,12,4,0,10,0},{0,16,1,0,5,0},D3DDECL_END()};'
    new=b'const D3DVERTEXELEMENT9 stEntityVertexDecl[]={{0,0,2,0,0,0},{0,12,2,0,3,0},{0,24,4,0,10,0},{0,28,1,0,5,0},D3DDECL_END()};'
    raw=replace(raw,old,new)
    anchor=b'#include "client455_r3_shader_load.inc"'
    raw=replace(raw,anchor,anchor+b'''
static RF455R3VertexProgram stLitGrass455;
#if defined(RF_CLIENT_455_CACHED_VERTEX_SHADER)
static RF455R3VertexProgram stReflection455;
static RF455R3VertexProgram stFilterBlit455;
static RF455R3VertexProgram stTransitionVertex455;
static RF455R3VertexProgram stLampParticleVertex455;
static IDirect3DPixelShader9* stBlurBlit455;
static IDirect3DPixelShader9* stTransitionPixel455;
static IDirect3DPixelShader9* stLampParticlePixel455;

static const D3DVERTEXELEMENT9 stFilterBlitDecl455[] = {
    {0, 0, D3DDECLTYPE_FLOAT3, D3DDECLMETHOD_DEFAULT, D3DDECLUSAGE_POSITION, 0},
    {0, 12, D3DDECLTYPE_FLOAT2, D3DDECLMETHOD_DEFAULT, D3DDECLUSAGE_TEXCOORD, 0},
    D3DDECL_END(),
};
static const D3DVERTEXELEMENT9 stTransitionDecl455[] = {
    {0, 0, D3DDECLTYPE_FLOAT3, D3DDECLMETHOD_DEFAULT, D3DDECLUSAGE_POSITION, 0},
    {0, 12, D3DDECLTYPE_FLOAT2, D3DDECLMETHOD_DEFAULT, D3DDECLUSAGE_TEXCOORD, 0},
    {0, 20, D3DDECLTYPE_FLOAT2, D3DDECLMETHOD_DEFAULT, D3DDECLUSAGE_TEXCOORD, 1},
    D3DDECL_END(),
};
static const D3DVERTEXELEMENT9 stLampParticleDecl455[] = {
    {0, 0, D3DDECLTYPE_FLOAT3, D3DDECLMETHOD_DEFAULT, D3DDECLUSAGE_POSITION, 0},
    D3DDECL_END(),
};
#endif
''')
    start,_=section(raw,b'BOOL LoadVertexShaderList()',b'BOOL LoadVertexShaderList()')
    raw=raw[:start]+br'''#if defined(RF_CLIENT_455_CACHED_VERTEX_SHADER)
void RF455_LoadReflectionShader()
{
    // 455 x86 RVA 0x4DA17D loads the optional shader from device startup.
    D3DCAPS9 caps{};
    auto* device = GetD3dDevice();
    if (!device || FAILED(device->GetDeviceCaps(&caps)) || caps.VertexShaderVersion < D3DVS_VERSION(1, 1))
        return;

    bool unavailable;
    loadCreateShader455(".\\System\\shader\\Reflection.vso", stDetailTexVertexDecl,
                        &stReflection455, unavailable);
}
#endif

'''+raw[start:]
    start,end=section(raw,b'BOOL LoadVertexShaderList()',b'BOOL LoadVertexShaderList()');body=raw[start:end]
    opening = body.index(b'{') + 1
    closing = body.rindex(b'\treturn TRUE;')
    existing = body[opening:closing]
    cached = br'''
#if defined(RF_CLIENT_455_CACHED_VERTEX_SHADER)
    bool unavailable;
    const auto grass = loadCreateShader455(".\\System\\shader\\Grass1.vso",
                                           stEntityVertexDecl, &stGrassVertexShader, unavailable);
    if (unavailable) {
        if (FAILED(D3DUtil_CreateVertexShader(GetD3dDevice(), ".\\System\\shader\\Grass1.vsh",
                                              stEntityVertexDecl, &stGrassVertexShader)))
            return FALSE;
    } else if (grass != S_OK) {
        return FALSE;
    }

    const auto detail = loadCreateShader455(".\\System\\shader\\DetailTex.vso",
                                            stDetailTexVertexDecl, &stDetailTexVertexShader, unavailable);
    if (!unavailable && detail != S_OK) return FALSE;
    char litGrass[] = ".\\System\\shader\\LitGrass1.vso";
    LoadCreateShader(litGrass, stEntityVertexDecl, &stLitGrass455);

    // Optional compiled programs loaded by the 455 x86 startup, RVA 0x4DA0C0.
    D3DCAPS9 caps{};
    auto* device = GetD3dDevice();
    if (device && SUCCEEDED(device->GetDeviceCaps(&caps))) {
        const bool vertexShaders = caps.VertexShaderVersion >= D3DVS_VERSION(1, 1);
        const bool pixelShaders = caps.PixelShaderVersion >= D3DPS_VERSION(1, 1);
        if (vertexShaders && pixelShaders && caps.MaxSimultaneousTextures >= 4) {
            const auto filter = loadCreateShader455(".\\System\\shader\\FilterBlit.vso",
                                                    stFilterBlitDecl455, &stFilterBlit455, unavailable);
            if (filter == S_OK || unavailable)
                loadCreatePixelShader455(".\\System\\shader\\BlurBlit.pso", stBlurBlit455);
        }

        const bool transitionReady = !vertexShaders ||
            loadCreateShader455(".\\System\\shader\\transition.vso", stTransitionDecl455,
                                &stTransitionVertex455, unavailable) == S_OK;
        if (transitionReady && pixelShaders)
            loadCreatePixelShader455(".\\System\\shader\\transition.pso", stTransitionPixel455);

        if (vertexShaders && pixelShaders) {
            const auto lamp = loadCreateShader455(".\\System\\shader\\lampparticle.vso",
                                                  stLampParticleDecl455, &stLampParticleVertex455, unavailable);
            if (lamp == S_OK || unavailable)
                loadCreatePixelShader455(".\\System\\shader\\lampparticle.pso", stLampParticlePixel455);
        }
    }
#else
'''
    optional = b'\tif(IsExistFile(".\\\\System\\\\shader\\\\LitGrass1.vso"))LoadCreateShader(".\\\\System\\\\shader\\\\LitGrass1.vso",stEntityVertexDecl,&stLitGrass455);\n'
    body=body[:opening]+cached+existing+optional+b'#endif\n'+body[closing:]
    raw=raw[:start]+body+raw[end:]
    inc=(WS/'scripts/native/client455_lit_grass.inc').read_bytes().replace(b'static RF455R3VertexProgram stLitGrass455;\n',b'')
    raw=replace(raw,b'void ReleaseVertexShaderList(){',b'''void ReleaseVertexShaderList(){
#if defined(RF_CLIENT_455_CACHED_VERTEX_SHADER)
    RF455_ReleaseR3VertexProgram(stReflection455);
    RF455_ReleaseR3VertexProgram(stFilterBlit455);
    releasePixelShader455(stBlurBlit455);
    RF455_ReleaseR3VertexProgram(stTransitionVertex455);
    releasePixelShader455(stTransitionPixel455);
    RF455_ReleaseR3VertexProgram(stLampParticleVertex455);
    releasePixelShader455(stLampParticlePixel455);
#endif
    RF455_ReleaseR3VertexProgram(stLitGrass455);
''')
    return raw+b'''
#if defined(RF_CLIENT_455_CACHED_VERTEX_SHADER)
#include "client455_screen_transition_draw.inc"
#include "client455_filter_blit_draw.inc"
#endif
'''+inc
