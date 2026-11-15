"""Seven54-byte runtime layers;preserve46-byte serialized R3M records."""
from prepare_client455_normal import section
from pathlib import Path
import re


def replace(raw,old,new):
    if raw.count(old)!=1:raise ValueError('Material migration boundary '+repr(old))
    return raw.replace(old,new)


def header(raw):
    raw=replace(raw,b'#define _MAX_MATERIALS\t\t1024',b'#define _MAX_MATERIALS\t\t2048')
    raw=replace(raw,b'#define _MAX_LAYER_NUM\t\t4',b'#define _MAX_LAYER_NUM\t\t7')
    raw=replace(raw,b'}_ONE_LAYER;',b'    float m_fSpecularFlickeringScale; //455 runtime+46,not serialized\n    float m_fSpecularFlickeringSpeed; //455 runtime+50,not serialized\n}_ONE_LAYER;')
    return raw+b'\n#include <cstddef>\nstatic_assert(sizeof(_ONE_LAYER)==54 && offsetof(_ONE_LAYER,m_fSpecularFlickeringScale)==46 && offsetof(_ONE_LAYER,m_fSpecularFlickeringSpeed)==50,"455 runtime layer");\nstatic_assert(sizeof(_R3MATERIAL)==526 && offsetof(_R3MATERIAL,m_Layer)==148,"455 runtime material");\n'


def material(raw):
    start,end=section(raw,b'_R3MATERIAL* LoadIndependenceR3M(',b'_R3MATERIAL* LoadIndependenceR3M(');body=raw[start:end]
    warnings=re.findall(rb'Warning\(name,"[^"\r\n]*"\);',body)
    if len(warnings)!=2:raise ValueError('R3M missing/version diagnostic boundaries changed')
    checked=(Path(__file__).resolve().parent/'native/client455_r3m_stream.inc').read_bytes()
    checked=checked.replace(b'@@MISSING_WARNING@@',warnings[0]).replace(b'@@VERSION_WARNING@@',warnings[1])
    raw=raw[:start]+checked+raw[end:]
    start,end=section(raw,b'_R3MATERIAL* LoadMainR3M(',b'_R3MATERIAL* LoadMainR3M(');body=raw[start:end]
    opening=body.index(b'{')+1
    sidecar=body.index(b'\tchar buf[256];')
    reset=body[opening:sidecar]
    body=body[:opening]+b'\n    if (!name || !*name || strnlen_s(name, 256) == 256) return NULL;\n'+body[sidecar:]
    body=replace(body,b'strcat(buf,".r3x");',b'''if (strlen(buf) > sizeof(buf) - sizeof(".r3x")) return NULL;
    strcat(buf,".r3x");

    auto candidate = RF455_PrepareR3m(name, prepared);
    if (!candidate) return NULL;
    const int textureCount = GetNowR3D3DTexCnt();
    const auto base = static_cast<long long>(textureCount) - 1;
    // R3X can reserve at most one lens flare slot, never at the INT_MAX cap.
    const auto upperBase = textureCount >= 1 && textureCount < INT_MAX ? base + 1 : base;
    if (!RF455_CanRebaseR3m(candidate.get(), base, upperBase)) return NULL;
''' + reset)
    release=body.index(b'\tif( R3material )')
    publish=body.index(b'\tstdwMaterialNum = R3material->m_iMatNum;',release)
    body=body[:release]+b'''    RF455_RebaseR3m(candidate.get(), static_cast<long long>(GetNowR3D3DTexCnt()) - 1);
    if(R3material)ReleaseMainMaterial();
    R3material=candidate.release();
'''+body[publish:]
    body=replace(body,b'_R3MATERIAL* LoadMainR3M(char *name)',
                 b'static _R3MATERIAL* LoadMainR3m455(char* name, const RF455ResourceBytes* prepared)')
    wrappers=b'''

_R3MATERIAL* LoadMainR3M(char* name)
{
    return LoadMainR3m455(name, nullptr);
}

_R3MATERIAL* RF455_LoadPreparedMainR3m455(char* name, const RF455ResourceBytes& source)
{
    return LoadMainR3m455(name, &source);
}
'''
    raw=raw[:start]+body+wrappers+raw[end:]
    start,end=section(raw,b'static void LoadOneLayer(',b'static void LoadOneLayer(');body=raw[start:end]
    anchor=b'\t}\n\tif( material->m_Layer[l_id].m_sANIAlphaFlickerAni == 0 )'
    extra=b'''        if(!strcmp(hole,"specular_flikering_scale")){
            fscanf(fp,"%s",hole);material->m_Layer[l_id].m_dwFlag|=0x800001u;
            material->m_Layer[l_id].m_fSpecularFlickeringScale=float(atof(hole));
        }
        if(!strcmp(hole,"specular_flikering_speed")){
            fscanf(fp,"%s",hole);material->m_Layer[l_id].m_dwFlag|=0x800002u;
            material->m_Layer[l_id].m_fSpecularFlickeringSpeed=float(atof(hole));
        }
'''
    body=replace(body,anchor,extra+anchor);raw=raw[:start]+body+raw[end:]
    #Preserve exact flag packing,including the whole-DWORD shift for light_object.
    start,end=section(raw,b'static void LoadOneMaterial(',b'static void LoadOneMaterial(');body=raw[start:end]
    anchor=b'\tGetR3State()->mSceneTextureDetail = temp_texture_detail;'
    if body.count(anchor)!=1:raise ValueError('Material texture-detail restore boundary')
    loop_end=body.rfind(b'\t}',0,body.index(anchor))
    extra=b'''        if(!strcmp(hole,"sky_sun_light"))material->m_dwFlag|=4u;
        if(!strcmp(hole,"sky_night"))material->m_dwFlag|=8u;
        if(!strcmp(hole,"sky_day"))material->m_dwFlag|=16u;
        if(!strcmp(hole,"sky_rotate_y"))material->m_dwFlag|=32u;
        if(!strcmp(hole,"texture_splatting"))material->m_dwFlag|=64u;
        if(!strcmp(hole,"shader_object")){fscanf(fp,"%s",hole);material->m_dwFlag|=0x1000000u;material->m_dwFlag+=DWORD(atol(hole));}
        if(!strcmp(hole,"light_object")){fscanf(fp,"%s",hole);material->m_dwFlag<<=8;material->m_dwFlag=(material->m_dwFlag+DWORD(atol(hole)))|0x11000000u;}
'''
    body=body[:loop_end]+extra+body[loop_end:];return raw[:start]+body+raw[end:]


def port_mst_resources(raw,section):
    """Bind the startup-engine MST parsers to bounded archive or loose input."""
    raw=b'#include "client455_resource_io.h"\n#include "client455_resource_text.h"\n#include <cstdlib>\n#include <new>\n#include <vector>\n'+raw
    wrappers=b'''
namespace {
bool OpenMst455(RF455ResourceText& input, char* path)
{
    constexpr std::size_t maxBytes = 1024u * 1024u;
    auto* cache = RF455_GetCharacterRfsCache();
    if (stIsReLoad) cache->RemoveLooseBytes(path);
    const auto budget = stIsReLoad ? 0 : cache->ByteBudget();
    const auto limit = budget < maxBytes ? budget : maxBytes;
    if (limit) {
        const auto source = RF455_ReadResourceBytes(path, limit);
        if (input.bind(source)) return true;
        if (source.status != RF455ResourceReadStatus::ReadError || source.declaredSize <= limit)
            return false;
    }
    std::uint64_t archiveBytes = 0;
    auto* stream = RF455_OpenResourceTextStream455(path, archiveBytes);
    return input.openStream(stream, archiveBytes);
}

bool ReadMstField455(RF455ResourceText& input, char (&token)[256])
{
    return input.read(token) && *token && std::strcmp(token, "}") != 0;
}

bool AppendMstPath455(char (&path)[256], const char* directory, const char* name, const char* suffix = "")
{
    if (!directory || !*directory || !name || !*name) return false;
    const auto length = std::strlen(directory) + std::strlen(name) + std::strlen(suffix);
    if (length >= sizeof(path)) return false;
    std::strcpy(path, directory);
    std::strcat(path, name);
    std::strcat(path, suffix);
    return true;
}
}

'''
    read=rb'fscanf\(fp,"%s",(?:&hole\[0\]|hole)\);'
    def fields(body, failure):
        return re.sub(read,b'if (!ReadMstField455(fp, hole)) '+failure,body)

    key=b'static void LoadOneLayer('
    start,end=section(raw,key,key)
    body=raw[start:end]
    body=replace(body,b'static void LoadOneLayer(FILE *fp,',b'static bool LoadOneLayer(RF455ResourceText& fp,')
    body=replace(body,b'        fscanf(fp,"%s",&hole[0]);\n        if (!strcmp(hole,"}"))',
                 b'        if (!fp.read(hole)) return false;\n        if (!strcmp(hole,"}"))')
    body=fields(body,b'return false;')
    body=replace(body,b'strcpy(name,stTexturePath);\n\t\t\tstrcat(name,hole);',
                 b'if (!AppendMstPath455(name, stTexturePath, hole)) return false;')
    body=replace(body,b'\t\t\t\t\tLONG get_tex_num;',b'''                    // The animation loader expects a dollar-terminated stem and three-byte extension.
                    const char* dollar = std::strchr(hole, '$');
                    const char* extension = std::strchr(hole, '.');
                    if (!dollar || !extension || dollar >= extension || extension - hole >= 128 ||
                        std::strlen(extension) < 4 || std::strlen(stTexturePath) + (dollar - hole) + 8 >= sizeof(name))
                        return false;
                    LONG get_tex_num;''')
    body=body[:-1]+b'    return !fp.failed();\n}'
    raw=raw[:start]+wrappers+body+raw[end:]

    key=b'static void LoadOneMaterial('
    start,end=section(raw,key,key)
    body=raw[start:end]
    first=body.index(b'\tFILE *fp;')
    last=body.index(b'\tif( stIsReLoad ==FALSE )',first)
    body=body[:first]+b'''    RF455ResourceText fp;
    char hole[256], texture[256];
    int l_id;
    bool sub = false;
    if (!OpenMst455(fp, name)) {
        Warning("MST", " could not open child material");
        return false;
    }
    _R3MATERIAL staged = *output;
    auto* material = &staged;

'''+body[last:]
    body=replace(body,b'static void LoadOneMaterial(char *name,_R3MATERIAL *material)',
                 b'static bool LoadOneMaterial(char* name, _R3MATERIAL* output)')
    body=replace(body,b'\tDWORD temp_texture_detail = GetR3State()->mSceneTextureDetail;',b'''    struct DetailRestore {
        DWORD saved = GetR3State()->mSceneTextureDetail;
        ~DetailRestore() { GetR3State()->mSceneTextureDetail = saved; }
    } restore;
    const auto reject = [&] {
        Warning("MST", " rejected malformed child material");
        return false;
    };''')
    body=replace(body,b'if( fscanf(fp,"%s",&hole[0])==EOF)\tbreak;',
                 b'if (!fp.read(hole) || !strcmp(hole,"end")) break;')
    body=fields(body,b'return reject();')
    body=replace(body,b'material->m_dwLayerNum = atoi(hole);',b'''const int count = atoi(hole);
            if (count < 0 || count > _MAX_LAYER_NUM) return reject();
            material->m_dwLayerNum = count;''')
    body=replace(body,b'strcpy(name,stTexturePath);\n\t\t\tstrcat(name,hole);',
                 b'if (!AppendMstPath455(texture, stTexturePath, hole)) return reject();')
    body=replace(body,b'R3GetPreTextureId(name)',b'R3GetPreTextureId(texture)')
    body=replace(body,b'LoadOneLayer(fp,material,l_id);',
                 b'if (l_id < 0 || l_id >= _MAX_LAYER_NUM || !LoadOneLayer(fp, material, l_id)) return reject();')
    body=replace(body,b'\tGetR3State()->mSceneTextureDetail = temp_texture_detail;\n\n\tfclose(fp);',
                 b'''    if (fp.failed()) return reject();
    *output = staged;
    return true;''')
    raw=raw[:start]+body+raw[end:]

    table=b'''
namespace {
bool ReadMstTable455(RF455ResourceText& input, const char* directory, int count, _R3MATERIAL* materials)
{
    char token[256];
    if (!input.read(token) || std::strcmp(token, "{") != 0) return false;
    struct Child { char name[sizeof(_R3MATERIAL::m_name)]; int id; };
    std::vector<Child> children;
    try { children.resize(count); }
    catch (const std::bad_alloc&) { return false; }
    char path[256];
    for (int i = 0; i < count; ++i) {
        if (!ReadMstField455(input, token) || std::strlen(token) >= sizeof(children[i].name) ||
            !AppendMstPath455(path, directory, token, ".mst")) return false;
        std::strcpy(children[i].name, token);
        if (!ReadMstField455(input, token)) return false;
        char* end = nullptr;
        const long id = std::strtol(token, &end, 10);
        if (end == token || *end || id < 0 || id >= count) return false;
        children[i].id = static_cast<int>(id);
    }
    for (int i = 0; i < count; ++i) {
        const auto& child = children[i];
        std::strcpy(materials[i].m_name, child.name);
        AppendMstPath455(path, directory, child.name, ".mst");
        LoadOneMaterial(path, &materials[child.id]);
    }
    return true;
}
}

'''
    key=b'static _R3MATERIAL* LoadIndependenceMaterial('
    start,end=section(raw,key,key)
    body=raw[start:end]
    first=body.index(b'\tFILE *fp;')
    last=body.index(b'\t_R3ENGINE_STATE *r3_state',first)
    body=body[:first]+b'''    RF455ResourceText fp;
    char hole[256], name[256];
    int m_num = 0;
    int i;
    std::unique_ptr<_R3MATERIAL, decltype(&Dfree)> mat(nullptr, &Dfree);
    if (!AppendMstPath455(name, matpath, "MainMaterial.mst") || !OpenMst455(fp, name)) {
        Warning("MST", " could not open master material");
        return nullptr;
    }
    std::strcpy(stTexturePath, matpath);
    const auto reject = []() -> _R3MATERIAL* {
        Warning("MST", " rejected malformed master material");
        return nullptr;
    };

'''+body[last:]
    first=body.index(b'\t\tif( fscanf(fp,')
    last=body.index(b'\t\tstrupr(hole);',first)
    body=body[:first]+b'        if (!fp.read(hole) || !strcmp(hole,"end")) break;\n'+body[last:]
    first=body.index(b'        if (!strcmp(hole,"*MATERIAL_NUM"))')
    last=body.index(b'        RF455_ReadSkyFogToken(fp,hole);',first)
    body=body[:first]+b'''        if (!strcmp(hole,"*MATERIAL_NUM")) {
            if (mat || !ReadMstField455(fp, hole)) return reject();
            m_num = atoi(hole);
            if (m_num < 1 || m_num >= _MAX_MATERIALS) return reject();
            mat.reset(static_cast<_R3MATERIAL*>(Dmalloc(m_num * sizeof(_R3MATERIAL))));
            if (!mat) return nullptr;
            for (int index = 0; index < m_num; ++index) MatInit(mat.get() + index);
            if (!ReadMstTable455(fp, matpath, m_num, mat.get())) return reject();
        }

'''+body[last:]
    body=fields(body,b'return reject();')
    body=replace(body,b'RF455_ReadSkyFogToken(fp,hole);',b'if (!RF455_ReadSkyFogToken(fp, hole)) return reject();')
    body=replace(body,b'RF455_ReadWeatherTokens(fp,hole);',b'if (!RF455_ReadWeatherTokens(fp, hole)) return reject();')
    body=replace(body,b'strcpy(name,matpath);\n\t\t\tstrcat(name,hole);',
                 b'if (!AppendMstPath455(name, matpath, hole) || strlen(name) >= sizeof(r3_state->mLensTexName)) return reject();')
    body=replace(body,b'strcpy(r3_state->mEnvEntityName,hole);',
                 b'if (strlen(hole) >= sizeof(r3_state->mEnvEntityName)) return reject();\n            strcpy(r3_state->mEnvEntityName,hole);')
    first=body.index(b'\tmat->m_iMatNum')
    body=body[:first]+b'''    if (!mat || fp.failed()) return reject();
    mat->m_iMatNum = static_cast<WORD>(m_num);
    return mat.release();
}'''
    raw=raw[:start]+table+body+raw[end:]

    key=b'_R3MATERIAL* LoadMainMaterial('
    start,end=section(raw,key,key)
    body=replace(raw[start:end],b'stdwMaterialNum = R3material->m_iMatNum;',
                 b'stdwMaterialNum = R3material ? R3material->m_iMatNum : 0;')
    raw=raw[:start]+body+raw[end:]

    key=b'void ReLoadMaterial('
    start,end=section(raw,key,key)
    raw=raw[:start]+b'''void ReLoadMaterial(char* matpath, _R3MATERIAL* now_material)
{
    if (!now_material) return;
    RF455ResourceText fp;
    char hole[256], name[256];
    if (!AppendMstPath455(name, matpath, "MainMaterial.mst")) return;
    RF455_GetCharacterRfsCache()->RemoveLooseBytes(name);
    if (!fp.openStream(std::fopen(name, "rt"))) return;
    std::strcpy(stTexturePath, matpath);
    while (fp.read(hole) && std::strcmp(hole, "end") != 0) {
        if (std::strcmp(hole, "*MATERIAL_NUM") != 0) continue;
        if (!ReadMstField455(fp, hole)) break;
        const int count = atoi(hole);
        if (count < 1 || count >= _MAX_MATERIALS || count > now_material->m_iMatNum ||
            !ReadMstTable455(fp, matpath, count, now_material)) break;
    }
}'''+raw[end:]
    return raw
