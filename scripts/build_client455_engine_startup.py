"""Build a derived engine with confirmed455startup fixes;preserve engine033."""
import argparse
import hashlib,json,os,re,subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_ninja_msvc import ninja_has_header, prepare_ninja_dependencies

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def port_ext_dummy_resource(raw, native, section):
    anchor = b'BOOL CExtDummy::LoadExtDummy('
    start, end = section(raw, anchor, anchor)
    return raw[:start] + (native / 'client455_ext_dummy_load.inc').read_bytes() + raw[end:]

def port_resource_allocator(raw, native):
    marker = b'static int Dmalloc_size = 0;'
    if raw.count(marker) != 1:
        raise ValueError('Engine resource allocator boundary changed')
    return raw.split(marker, 1)[0] + (native / 'client455_dmalloc.inc').read_bytes()


def port_r3t_resources(raw, native, section):
    # These consumers live in the legacy texture translation unit and use its
    # private texture slots/main device. Replace only their owned read paths.
    for anchor, source in (
        (b'void LoadR3T(R3Texture *tex)', None),
        (b'_LIGHTMAP **LoadR3TLightMap(', 'client455_lightmap_stream.inc'),
        (b'R3Texture *R3GetTexInfoR3T(', 'client455_r3t_load.inc'),
        (b'LPDIRECT3DTEXTURE9 R3LoadDDSAndTextureMem(char *name)\n{', 'client455_dds_d3dx.inc'),
        (b'LPDIRECT3DTEXTURE9 R3LoadDDS(', 'client455_dds_load.inc'),
        (b'LPDIRECT3DTEXTURE9 R3LoadDDSFromFP(', 'client455_dds_stream.inc'),
        (b'BOOL CTextureRender::CreateTexture(', None),
        (b'void CTextureRender::ReleaseTexture()', 'client455_render_texture_lifetime.inc'),
    ):
        if source == 'client455_dds_d3dx.inc' and anchor not in raw:
            anchor = anchor.replace(b'\n', b'\r\n')
        start, end = section(raw, anchor, anchor)
        replacement = (native / source).read_bytes() if source else b''
        raw = raw[:start] + replacement + raw[end:]
    anchor = b'LPDIRECT3DTEXTURE9 R3GetSurface('
    start, end = section(raw, anchor, anchor)
    body = raw[start:end]
    if body.count(b'id <= stR3D3DTexCnt') != 1:
        raise ValueError('Texture slot boundary changed')
    body = body.replace(b'id <= stR3D3DTexCnt', b'stR3D3DTexture && id < stR3D3DTexCnt')
    from client455_mst_texture_port import port_mst_texture_registry
    return port_mst_texture_registry(raw[:start] + body + raw[end:], native, section)


def guard_level_material_load(raw, section):
    anchor = b'void CLevel::LoadLevel('
    start, end = section(raw, anchor, anchor)
    body = raw[start:end]
    load = b'\t\t\tLoadMainR3M(load_name);'
    if body.count(load) != 2:
        raise ValueError('Map R3M caller boundaries changed')
    # The client branch must leave before BSP and texture consumers on failure.
    checked = b'''            auto* materials = LoadMainR3M(load_name);
            if (!materials) {
                mIsLoadedBsp = FALSE;
                mBsp->SetIsLoaded(FALSE);
                return;
            }
            // R3X can reserve a lens flare slot before R3M IDs are rebased.
            const int anticipatedFirst = GetNowR3D3DTexCnt();'''
    body = body.replace(load, checked, 1)
    text_load = b'\t\t\tLoadMainMaterial(load_name);'
    if body.count(text_load) != 1:
        raise ValueError('Map MST caller boundary changed')
    body = body.replace(text_load, b'''            if (!LoadMainMaterial(load_name)) {
                mIsLoadedBsp = FALSE;
                mBsp->SetIsLoaded(FALSE);
                return;
            }''')
    reserve = b'R3Texture *t_tex = R3GetTexInfoR3T(load_name,0);'
    upload = b'LoadR3T(t_tex);'
    if body.count(reserve) != 1 or body.count(upload) != 1:
        raise ValueError('Map R3T reservation/upload boundaries changed')
    body = body.replace(reserve, b'RF455ResourceRead mapTextures;\n'
                       b'\t\t\tR3Texture* t_tex = RF455_ReserveMapR3T(load_name, mapTextures);')
    no_lod = b'SetNoLodTextere();'
    reserve_at = body.index(b'RF455_ReserveMapR3T(load_name, mapTextures);')
    no_lod_at = body.index(no_lod, reserve_at)
    bind = b'''RF455_BindMapMaterialTextures(materials, anticipatedFirst,
                                             t_tex ? t_tex->mStartID : 0,
                                             t_tex ? t_tex->mTexNum : 0);
\t\t\t'''
    body = body[:no_lod_at] + bind + body[no_lod_at:]
    body = body.replace(upload, b'RF455_LoadMapR3T(t_tex, mapTextures);')
    declarations = b'''#include "client455_resource_io.h"
#include "r3d3dtex.h"
#include "r3material.h"
R3Texture* RF455_ReserveMapR3T(char* name, RF455ResourceRead& source);
void RF455_LoadMapR3T(R3Texture* tex, const RF455ResourceRead& source);
void RF455_BindMapMaterialTextures(_R3MATERIAL* materials, int anticipatedFirst, DWORD actualFirst, DWORD textureCount);
_R3MATERIAL* RF455_LoadPreparedMainR3m455(char* name, const RF455ResourceBytes& source);
'''
    return declarations + raw[:start] + body + raw[end:]


def port_r3x_resource(raw, section):
    anchor = b'void LoadR3X('
    start, end = section(raw, anchor, anchor)
    body = raw[start:end]
    newline = b'\r\n' if b'\r\n' in body else b'\n'
    weather = b'#if defined(RF_CLIENT_455_WEATHER)' + newline
    first = body.index(b'\t#if defined(RF_CLIENT_455_RESOURCE_IO)')
    checked = body.index(weather, first)
    legacy = body.index(b'#else' + newline + b'\tfread(&version,', checked)
    version_decl = b'\tfloat version;' + newline
    stream_decl = b'\tFILE *fp;' + newline
    warning = re.findall(rb'Warning\(name,"[^"\r\n]*"\);', body[checked:legacy])
    if len(warning) != 1 or body.count(version_decl) != 1 or body.count(stream_decl) != 1:
        raise ValueError('R3X stream and diagnostic boundaries changed')
    legacy_open = body[first:checked].lstrip()
    checked_reader = b'''#if defined(RF_CLIENT_455_WEATHER)
    // Client 455 x86 RVA 0x50AED0 uses the archive-aware resource resolver.
    {
        constexpr std::uint64_t maxBytes = 1024u * 1024u;
        const auto source = RF455_ReadResourceBytes(name, maxBytes);
        if (source.status == RF455ResourceReadStatus::Unavailable) return;
        const bool ready = source.status == RF455ResourceReadStatus::Ready && source.bytes;
        if (!ready || !RF455_ParseExtMaterial(source.bytes->data(), source.bytes->size(), &ext_mat)) {
            if (ready) RF455_GetCharacterRfsCache()->RemovePayloadBytes(source.bytes);
            ''' + warning[0] + b'''
            return;
        }
    }
    state->mEnvironmentSceneFlags=ext_mat.mSceneFlags;
#else
    float version;
    FILE* fp;
'''
    body = body[:first] + checked_reader.replace(b'\n', newline) + legacy_open + body[legacy + len(b'#else' + newline):]
    body = body.replace(version_decl, b'', 1).replace(stream_decl, b'', 1)
    tail = b'\tfclose(fp);' + newline + b'}'
    if not body.endswith(tail):
        raise ValueError('R3X final resource close boundary changed')
    body = body[:-len(tail)] + b'#if !defined(RF_CLIENT_455_WEATHER)' + newline + tail[:-1] + b'#endif' + newline + b'}'
    includes = b'#include "client455_resource_io.h"\n'
    return includes + raw[:start] + body + raw[end:]


def port_scene_bsp_header(raw):
    declarations = (
        (b'class  CBsp{', b'class RF455SceneInput455;\n\nclass  CBsp{'),
        (b'void LoadBsp(char *name);',
         b'BOOL LoadBsp(char *name, const RF455SceneInput455* prepared = nullptr);'),
        (b'void ReadDynamicDataFillVertexBuffer(FILE *fp)', b'bool ReadDynamicDataFillVertexBuffer(RF455SceneInput455& input)'),
        (b'ReadDynamicDataExtBsp(FILE *fp)', b'ReadDynamicDataExtBsp(RF455SceneInput455& input)'),
    )
    for old, new in declarations:
        if raw.count(old) != 1:
            raise ValueError('BSP input declaration changed: ' + str(old))
        raw = raw.replace(old, new)
    return b'#include "client455_map_shader_lights.h"\n' + raw


def port_scene_bsp(raw, section):
    from audit_client455_normal_character_api import code_only

    def offset_in_method(name, edit):
        nonlocal raw
        start, end = section(raw, name, name)
        raw = raw[:start] + edit(raw[start:end]) + raw[end:]

    def cache_reads(body, expected):
        # The header preflight checks the sum of every active read in these
        # methods. Keep commented reference readers out of the substitutions.
        operations = list(re.finditer(rb'fread\(([^,]+),([^,]+),1,fp\);', code_only(body)))
        if len(operations) != expected:
            raise ValueError('BSP sequential reads changed')
        for op in reversed(operations):
            name, count = (body[op.start(i):op.end(i)] for i in (1, 2))
            body = body[:op.start()] + b'input.read(' + name + b', ' + count + b');' + body[op.end():]
        return body

    def bsp(body):
        begin = body.index(b'\tFILE *fp;')
        after = body.index(b'\tmNowCFaceId=0;', begin)
        body = body[:begin] + b'''    if (!IsInitR3Engine()) return FALSE;
    auto input = prepared ? *prepared : RF455SceneInput455(name);
    if (!input.validateBsp()) {
        input.reject(name);
        return FALSE;
    }
    // Material IDs refer to the table loaded for this specific level.
    if (!input.validateBspMaterials(GetMainMaterial() ? GetMainMaterialNum() : 0) ||
        !input.readBsp(mBSPHeader)) return FALSE;
    int size;

''' + body[after:]
        begin = body.index(b'\tfread(&mBSPHeader')
        end = body.index(b'\tmLeafNum=', begin)
        body = body[:begin] + body[end:]
        body = cache_reads(body, 8)
        skip = b'fseek(fp,skip_file_size,SEEK_CUR);'
        read = b'ReadDynamicDataFillVertexBuffer(fp);'
        if body.count(skip) != 1 or body.count(read) != 1 or body.count(b'fclose(fp);') != 1:
            raise ValueError('BSP input consumption changed')
        body = body.replace(skip, b'input.skip(skip_file_size);')
        body = body.replace(read, b'''if (!ReadDynamicDataFillVertexBuffer(input)) {
        if (input.failed()) input.reject(name);
        ReleaseBsp();
        return FALSE;
    }''')
        body = re.sub(rb'(?m)^\tfclose\(fp\);\r?\n', b'', body)
        # When the optional event-ID lane is absent, the allocated words are
        # still consumed by animation lookups. Zero the unused part.
        event = b'input.read(mEventObjectID, mBSPHeader.EventObjectID.size);'
        body = body.replace(event, b'memset(mEventObjectID, 0, mObjectNum * sizeof(WORD));\n\t' + event)
        convert = b'\tConvAniObject(mBSPHeader.Object.size/sizeof(_READ_ANI_OBJECT),track,r_object,mObject);'
        if body.count(convert) != 1:
            raise ValueError('BSP animation object conversion boundary changed')
        prepared = b'''    for (DWORD index = 0; index < mObjectNum; ++index) {
        auto& record = r_object[index];
        // Bind geometry uses these parents before 455's later parent cleanup.
        if (record.parent > mObjectNum) record.parent = 0;
        if (!record.Pos_cnt) record.pos_offset = 0;
        if (!record.Rot_cnt) record.rot_offset = 0;
        if (!record.Scale_cnt) record.scale_offset = 0;
        mObject[index].AniFrameCache = 0;
    }
'''
        body = body.replace(convert, prepared + convert)
        return body[:-1] + b'    return TRUE;\n}'

    def ext_bsp(body):
        begin = body.index(b'\tFILE *fp;')
        after = body.index(b'\tmCFVertexNum', begin)
        body = body[:begin] + b'''    RF455SceneInput455 input(name);
    if (!input.readExtBsp(mExtBSPHeader, mLeafNum)) {
        input.reject(name);
        return;
    }
    int size;

''' + body[after:]
        count = body.index(b'mSoundEntitiesListNum=')
        begin = body.index(b'\t//', body.index(b'\n', count))
        end = body.index(b'\tmExtBspStaticAllocSize=0;', begin)
        body = body[:begin] + body[end:]
        body = cache_reads(body, 9)
        read = b'ReadDynamicDataExtBsp(fp);'
        if body.count(read) != 1 or body.count(b'fclose(fp);') != 1:
            raise ValueError('EBP input consumption changed')
        body = body.replace(read, b'''ReadDynamicDataExtBsp(input);
    if (input.failed()) {
        input.reject(name);
        return;
    }''')
        sounds = b'mSoundEntityList = (_SOUND_ENTITY_LIST *)&mExtBspStaticAlloc[size];'
        if body.count(sounds) != 1:
            raise ValueError('EBP sound initialization boundary changed')
        body = body.replace(sounds, sounds+b'\n    memset(mSoundEntityList, 0, mSoundEntityListNum * sizeof(_SOUND_ENTITY_LIST));')
        return re.sub(rb'(?m)^\tfclose\(fp\);\r?\n', b'', body)

    def dynamic(body, reads):
        signature = b'(FILE *fp)'
        if body.count(signature) != 1:
            raise ValueError('BSP dynamic input signature changed')
        return cache_reads(body.replace(signature, b'(RF455SceneInput455& input)'), reads)

    def geometry(body):
        body = dynamic(body, 10).replace(b'void CBsp::', b'bool CBsp::', 1)
        newline = b'\r\n' if b'\r\n' in body else b'\n'

        def bind(old, new):
            nonlocal body
            old, new = (part.replace(b'\n', newline) for part in (old, new))
            if body.count(old) != 1:
                raise ValueError('BSP vertex buffer lifetime boundary changed: ' + repr(old))
            body = body.replace(old, new)

        bind(b'\tint i,j,k;\n', b'''    if (input.failed()) {
        Dfree(v_normal);
        Dfree(read_alloc_buf);
        return false;
    }
	int i,j,k;
''')
        bind(b'\tint static_vertexnum = 0;', b'''    // The raw lease identifies the source generation. Only local positions
    // are shared; materials, normals, transforms and GPU buffers are rebuilt.
    static RF455BspPositionCache positionCache;
    const auto positionCount = mBSPHeader.VertexId.size / sizeof(DWORD);
    const auto cachedPositions = positionCache.find(input.resourceBytes(), positionCount);
    auto newPositions = cachedPositions ? nullptr : positionCache.stage(positionCount);
    const auto* positions = cachedPositions ? cachedPositions.get() : newPositions.get();

	int static_vertexnum = 0;''')
        decode = b'GetVertexFromCompress[function_id](t_v,(void*)((BYTE *)vertex+vertexid[v_id]*function_id*3),&readmatgroup[i]);'
        if body.count(decode) != 2:
            raise ValueError('BSP position decoding boundaries changed')
        first = b'''const auto corner = all_static_v_cnt + temp_static_v_cnt;
                if (cachedPositions) {
                    Vector3fCopy((*cachedPositions)[corner].coordinates, t_v);
                } else {
                    ''' + decode + b'''
                    if (newPositions) Vector3fCopy(t_v, (*newPositions)[corner].coordinates);
                }'''
        second = b'''if (positions) {
                    Vector3fCopy((*positions)[all_static_v_cnt + static_v_cnt].coordinates, t_v);
                } else {
                    ''' + decode + b'''
                }'''
        before, between, after = body.split(decode)
        body = before + first.replace(b'\n', newline) + between + second.replace(b'\n', newline) + after
        bind(b'\t\t\tmMatGroup[i].MultiSourceUV = (void*)&m_uv[uv_num];',
             b'''            auto corner = all_static_v_cnt + temp_v_num;
			mMatGroup[i].MultiSourceUV = (void*)&m_uv[uv_num];''')
        bind(b'\t\t\t\tint temp_st_num=st_num;\n\n\t\t\t\tfor(k=0; k<face[f_id].v_num; k++)',
             b'\t\t\t\tint temp_st_num=st_num;\n\n\t\t\t\tfor(k=0; k<face[f_id].v_num; ++k, ++corner)')
        metal = b'GetVertexFromCompress[function_id](tex2temp[k],(void*)((BYTE *)vertex+vertexid[v_id]*function_id*3),&readmatgroup[i]);'
        bind(metal, b'''if (positions) {
                            Vector3fCopy((*positions)[corner].coordinates, tex2temp[k]);
                        } else {
                            ''' + metal + b'''
                        }''')
        bind(b'\tstatic_vertexbp=(_D3DR3VERTEX_TEX2 *)mStaticVertexBuffer[static_vb_cnt].VPLock();\n'
             b'\tstatic_indexbp =(WORD *)mStaticIndexedBuffer.VPLock();',
             b'''    static_vertexbp = reinterpret_cast<_D3DR3VERTEX_TEX2*>(mStaticVertexBuffer[0].VPLock());
    static_indexbp = reinterpret_cast<WORD*>(mStaticIndexedBuffer.VPLock());
    const auto abortGeometry = [&]() {
        if (static_vertexbp) mStaticVertexBuffer[static_vb_cnt].VPUnLock();
        if (static_indexbp) mStaticIndexedBuffer.VPUnLock();
        Dfree(v_normal);
        Dfree(read_alloc_buf);
        return false;
    };
    if ((mVBVertexNum[0] && !static_vertexbp) || (static_trinum && !static_indexbp))
        return abortGeometry();''')
        bind(b'\t\t\tstatic_vb_cnt++;\n'
             b'\t\t\tstatic_vertexbp=(_D3DR3VERTEX_TEX2 *)mStaticVertexBuffer[static_vb_cnt].VPLock();',
             b'''            ++static_vb_cnt;
            static_vertexbp = nullptr;
            if (static_cast<DWORD>(static_vb_cnt) < mStaticVBCnt) {
                static_vertexbp = reinterpret_cast<_D3DR3VERTEX_TEX2*>(mStaticVertexBuffer[static_vb_cnt].VPLock());
                if (!static_vertexbp) return abortGeometry();
            }''')
        bind(b'\t}\n\tmStaticVertexBuffer[static_vb_cnt].VPUnLock();',
             b'\t}\n    if (static_vertexbp) mStaticVertexBuffer[static_vb_cnt].VPUnLock();')
        bind(b'\t\treturn;\n\t}', b'\t\treturn true;\n\t}')
        return body[:-1] + b'    if (newPositions) positionCache.publish(input.resourceBytes(), std::move(newPositions));' + newline + b'    return true;' + newline + b'}'

    offset_in_method(b'void CBsp::LoadBsp(', bsp)
    raw = raw.replace(b'void CBsp::LoadBsp(char *name)',
                      b'BOOL CBsp::LoadBsp(char *name, const RF455SceneInput455* prepared)', 1)
    offset_in_method(b'void CBsp::LoadExtBsp(', ext_bsp)
    offset_in_method(b'void CBsp::ReadDynamicDataFillVertexBuffer(', geometry)
    offset_in_method(b'void CBsp::ReadDynamicDataExtBsp(', lambda body: dynamic(body, 3))

    def guard_leaf_consumer(name, old, new):
        def edit(body):
            if body.count(old) != 1:
                raise ValueError('Optional EBP leaf access boundary changed')
            return body.replace(old, new)
        offset_in_method(name, edit)

    guard_leaf_consumer(b'void CBsp::WalkLeaf(', b'\tif( mEntityListNum )',
                        b'    if (mEntityListNum && static_cast<DWORD>(leaf_id) < mLeafEntityListNum)')
    guard_leaf_consumer(b'void CBsp::HearMapSound(', b'\tGetCameraPos(&pos);',
                        b'    if (static_cast<DWORD>(mNowLeafNum) >= mLeafSoundEntityListNum) return;\n\tGetCameraPos(&pos);')
    guard_leaf_consumer(b'void CBsp::ReleaseBsp()', b'\tDWORD i;', b'''    // Other rendering passes can bind buffers directly. Consult the device
    // before releasing the scene's own references, then forget cached state.
    if (auto* device = mStaticVBCnt ? GetD3dDevice() : nullptr) {
        IDirect3DVertexBuffer9* boundVertex = nullptr;
        UINT offset = 0, stride = 0;
        if (SUCCEEDED(device->GetStreamSource(0, &boundVertex, &offset, &stride)) && boundVertex) {
            for (DWORD index = 0; index < mStaticVBCnt; ++index) {
                if (mStaticVertexBuffer[index].m_lpVertexBuffer == boundVertex) {
                    device->SetStreamSource(0, nullptr, 0, 0);
                    break;
                }
            }
            boundVertex->Release();
        }
        IDirect3DIndexBuffer9* boundIndex = nullptr;
        if (SUCCEEDED(device->GetIndices(&boundIndex)) && boundIndex) {
            if (mStaticIndexedBuffer.m_lpIndexBuffer == boundIndex) device->SetIndices(nullptr);
            boundIndex->Release();
        }
    }
    ResetVertexBufferCache();
\tDWORD i;''')
    return b'#include "client455_scene_input.h"\n#include "client455_bsp_positions.h"\n' + raw


def port_buffer_create_failure(raw):
    from prepare_client455_normal import section

    renames = (
        (rb'static BYTE \*stOldVB=NULL;\r?\nstatic BYTE \*stOldIB=NULL;',
         b'static RF455BufferBindings<IDirect3DDevice9, IDirect3DVertexBuffer9, IDirect3DIndexBuffer9> bufferBindings455;'),
        (rb'stOldVB\s*=\s*NULL;\r?\n\s*stOldIB\s*=\s*NULL;', b'bufferBindings455.reset();'),
    )
    for (old, new), expected in zip(renames, (1, 3)):
        raw, count = re.subn(old, new, raw)
        if count != expected:
            raise ValueError('D3D9 binding cache declaration changed')

    def edit(signature, transform):
        nonlocal raw
        start, end = section(raw, signature, signature)
        raw = raw[:start] + transform(raw[start:end]) + raw[end:]

    for number in (b'1', b'2'):
        def bind(body):
            start = body.index(b'\tif( vb != stOldVB )')
            end = body.index(b'\tRF455_SetFixedVertexFormat(', start)
            return body[:start] + b'''    if (!pd3dDevice) return;
    bufferBindings455.bind(pd3dDevice, static_cast<IDirect3DVertexBuffer9*>(vb),
        static_cast<IDirect3DIndexBuffer9*>(ib), sizeof(_D3DR3VERTEX_TEX''' + number + b'''));
''' + body[end:]
        edit(b'void SetVPIPTex' + number + b'(', bind)

    for kind, member, iface, creator, extra in (
        (b'Vertex', b'm_lpVertexBuffer', b'IDirect3DVertexBuffer9', b'CreateVertexBuffer', b'fvf'),
        (b'Index', b'm_lpIndexBuffer', b'IDirect3DIndexBuffer9', b'CreateIndexBuffer', b'D3DFMT_INDEX16'),
    ):
        def create(body):
            body = body[:body.index(b'{') + 1] + b'''
    Release''' + kind + b'''Buffer();
    if (size <= 0) return;

    ''' + iface + b'''* buffer = nullptr;
    if (flag == _USE_MEMORY_VP) {
        buffer = reinterpret_cast<''' + iface + b'''*>(Dmalloc(size));
    } else if (flag == _USE_DYNAMIC_VP || flag == _USE_STATIC_VP) {
        // Managed map buffers survive Reset. UV updates lock managed data
        // normally; D3DUSAGE_DYNAMIC is incompatible with D3DPOOL_MANAGED.
        if (auto* device = GetD3dDevice()) {
            if (FAILED(device->''' + creator + b'''(size, D3DUSAGE_WRITEONLY, ''' + extra + b''',
                D3DPOOL_MANAGED, &buffer, nullptr))) buffer = nullptr;
        }
    }
    if (!buffer) {
        Error("Unable to create ''' + kind.lower() + b''' buffer", "");
        return;
    }
    ''' + member + b''' = buffer;
    m_Flag = flag;
    m_Size = size;
    stTotalVertexSize += m_Size;
    ++stTotalVertexCnt;
}'''
            return body

        def release(body):
            return body[:body.index(b'{') + 1] + b'''
    auto* buffer = ''' + member + b''';
    if (!buffer) return;
    ''' + member + b''' = nullptr;
    if (m_Flag == _USE_MEMORY_VP) {
        Dfree(buffer);
    } else {
        bufferBindings455.release''' + kind + b'''(GetD3dDevice(), buffer);
        buffer->Release();
    }
    stTotalVertexSize -= m_Size;
    --stTotalVertexCnt;
    m_Flag = 0;
    m_Size = 0;
}'''

        def lock(body):
            args = b'int start,int size,DWORD option'
            if body.count(args) != 1:
                raise ValueError('D3D9 buffer lock signature changed')
            return body[:body.index(b'{') + 1].replace(args, b'int start,int size,DWORD') + b'''
    auto* buffer = ''' + member + b''';
    if (!buffer || start < 0 || size < 0 || static_cast<DWORD>(start) >= m_Size ||
        static_cast<DWORD>(size) > m_Size - start) return nullptr;
    if (m_Flag == _USE_MEMORY_VP) return reinterpret_cast<BYTE*>(buffer) + start;

    void* bytes = nullptr;
    if (FAILED(buffer->Lock(start, size, &bytes, 0))) return nullptr;
    return static_cast<BYTE*>(bytes);
}'''

        owner = b'C' + kind + b'Buffer::'
        edit(b'void ' + owner + b'Init' + kind + b'Buffer(', create)
        edit(b'void ' + owner + b'Release' + kind + b'Buffer()', release)
        edit(b'BYTE* ' + owner + b'VPLock(', lock)

    # The legacy load reset zeroes live-resource counters while other owners
    # still hold buffers. Keep the exported entry point for existing callers.
    edit(b'void ResetTotalVertexBufferInfo()', lambda body: body[:body.index(b'{') + 1] + b'\n}\n')
    return b'#include "client455_buffer_binding.h"\n' + raw + b'''
// 455 RVA 0x4C64F0 changes the declaration without clearing its shader.
void RF455_SetVPIPTex1KeepingShader(void* vb, void* ib, IDirect3DVertexDeclaration9* declaration) {
    auto* device = GetD3dDevice();
    if (!device) return;
    bufferBindings455.bind(device, static_cast<IDirect3DVertexBuffer9*>(vb),
        static_cast<IDirect3DIndexBuffer9*>(ib), sizeof(_D3DR3VERTEX_TEX1));
    device->SetVertexDeclaration(declaration);
}
'''


def port_buffer_device_lifetime(raw, section):
    for name in (b'D3D_R3RestoreDevice', b'D3D_R3InvalidateDevice', b'D3D_R3DeleteDevice'):
        start, end = section(raw, b'HRESULT ' + name + b'()', b'HRESULT ' + name + b'()')
        at = raw.index(b'{', start, end) + 1
        raw = raw[:at] + b'\n    ResetVertexBufferCache();' + raw[at:]
    return raw


def port_scene_reset_scope(raw, section):
    entry = b'HRESULT CD3DApplication::Resize3DEnvironment()'
    start, end = section(raw, entry, entry)
    body = raw[start:end]
    first = body.index(b'{') + 1
    scope = b'''
    if (!m_pd3dDevice) return E_FAIL;
    const RF455SceneResetGuard sceneReset;
'''
    marker = b'''
namespace {
bool sceneReset455 = false;
struct RF455SceneResetGuard {
    const bool previous = sceneReset455;
    RF455SceneResetGuard() { sceneReset455 = true; }
    ~RF455SceneResetGuard() { sceneReset455 = previous; }
};
}

bool RF455_IsSceneReset455() { return sceneReset455; }

'''
    return raw[:start] + marker + body[:first] + scope + body[first:] + raw[end:]


def port_device_replacement_release(raw, section):
    marker = b'bool RF455_IsSceneReset455() { return sceneReset455; }'
    if raw.count(marker) != 1:
        raise ValueError('D3D9 replacement scope boundary changed')
    raw = raw.replace(marker, marker + b'''

namespace {
bool replacingDevice455 = false;
struct RF455DeviceReplacementGuard {
    const bool previous = replacingDevice455;
    RF455DeviceReplacementGuard() { replacingDevice455 = true; }
    ~RF455DeviceReplacementGuard() { replacingDevice455 = previous; }
};
}

bool RF455_IsDeviceReplacement455() { return replacingDevice455; }
''')
    for name in (b'ForceWindowed', b'UserSelectNewDevice'):
        signature = b'HRESULT CD3DApplication::' + name + b'()'
        start, end = section(raw, signature, signature)
        body = raw[start:end]
        anchor = b'    InvalidateDeviceObjects();\n    DeleteDeviceObjects();'
        if body.count(anchor) != 1:
            raise ValueError('D3D9 replacement cleanup boundary changed: ' + repr(name))
        replacement = b'''    const RF455DeviceReplacementGuard replacement;
    if (FAILED(hr = InvalidateDeviceObjects())) return DisplayErrorMsg(hr, MSGERR_APPMUSTEXIT);
    if (FAILED(hr = DeleteDeviceObjects())) return DisplayErrorMsg(hr, MSGERR_APPMUSTEXIT);'''
        if name == b'UserSelectNewDevice':
            replacement = b'    m_bReady = FALSE;\n' + replacement
        body = body.replace(anchor, replacement)
        raw = raw[:start] + body + raw[end:]
    old = b'''    if( m_pd3dDevice->Release() > 0L )
        return DisplayErrorMsg( D3DAPPERR_NONZEROREFCOUNT, MSGERR_APPMUSTEXIT );'''
    if raw.count(old) != 2:
        raise ValueError('Full device replacement release boundary changed')
    raw = raw.replace(old, b'''    auto* retiredDevice = m_pd3dDevice;
    m_pd3dDevice = nullptr;
    if (retiredDevice && retiredDevice->Release() > 0L)
        return DisplayErrorMsg( D3DAPPERR_NONZEROREFCOUNT, MSGERR_APPMUSTEXIT );''')
    signature = b'HRESULT CD3DApplication::UserSelectNewDevice()'
    start, end = section(raw, signature, signature)
    body = raw[start:end]
    anchor = b'    // If the app is paused, trigger the rendering of the current frame'
    if body.count(anchor) != 1:
        raise ValueError('Full device replacement reactivation boundary changed')
    return raw[:start] + body.replace(anchor, b'    m_bReady = TRUE;\n\n' + anchor) + raw[end:]


def port_device_wrapper_results(raw):
    for method in (b'R3RestoreDevice()', b'R3InvalidateDevice()'):
        pattern = rb'if\( ' + re.escape(method) + rb' == E_FAIL \)\s+return E_FAIL;\s+return S_OK;'
        raw, count = re.subn(pattern, b'return ' + method + b';', raw)
        if count != 1:
            raise ValueError('R3D3dWrapper device result boundary changed: ' + repr(method))
    return raw


def port_managed_uv_lock(raw):
    update = rb'(\t\t)MakeUV\(vertexbp,m_group->VCnt,m_group->MultiSourceUV,m_group->MultiSourceST,mat,l_id\);\r?\n\r?\n\t\tvbuffer->VPUnLock\(\);'
    raw, count = re.subn(update, b'''        if (vertexbp) {
            MakeUV(vertexbp,m_group->VCnt,m_group->MultiSourceUV,m_group->MultiSourceST,mat,l_id);
            vbuffer->VPUnLock();
        }''', raw)
    if count != 1:
        raise ValueError('D3D9 material UV update boundary changed')
    return raw


def port_scene_level_header(raw):
    anchor = b'void LoadLevel(char *name=NULL);'
    if raw.count(anchor) != 1:
        raise ValueError('CLevel load declaration boundary changed')
    return b'class RF455SceneInput455;\n'+raw.replace(anchor,anchor+
        b'\n\tvoid LoadLevel(char* name, const RF455SceneInput455* prepared);')


def port_bsp_map_shader_lights(raw, section):
    render = b'void CBsp::RenderMatGroup('
    start, end = section(raw, render, render)
    body = raw[start:end]
    dispatch = b'\tif( state->mShowLightMap )'
    if body.count(dispatch) != 1:
        raise ValueError('BSP map shader light dispatch changed')
    bind = b'''    const int materialId = mMatGroup[mat_g_id].MtlId;
    const auto* materials = GetMainMaterial();
    if (materials && materialId >= 0 && static_cast<DWORD>(materialId) < GetMainMaterialNum())
        mMapShaderLights455.bind(GetD3dDevice(), materials[materialId].m_dwFlag, &state->mInvMatView._41);

'''
    raw = raw[:start] + body.replace(dispatch, bind + dispatch) + raw[end:]

    release = b'void CBsp::ReleaseBsp()'
    start, end = section(raw, release, release)
    body = raw[start:end]
    reset = b'\tClearVariable();'
    if body.count(reset) != 1:
        raise ValueError('BSP map shader light release changed')
    return raw[:start] + body.replace(reset, b'    mMapShaderLights455.clear();\n' + reset) + raw[end:]


def port_level_map_shader_lights(raw):
    anchor = rb'(        mBsp->SetEnvironmentDummies455\(&mDummy\);\r?\n#endif\r?\n)'
    load = b'''        strcpy(tempname, real_bsp_name);
        StripEXT(tempname);
        strcat(tempname, ".r3l");
        mBsp->LoadMapShaderLights455(tempname);
'''
    raw, count = re.subn(anchor, lambda match: match[0] + load, raw)
    if count != 1:
        raise ValueError('Level map shader light load changed')
    return raw


def port_scene_level(raw, section):
    anchor = b'void CLevel::LoadLevel('
    start, end = section(raw, anchor, anchor)
    body = raw[start:end]
    path = b'\tstrcat(real_bsp_name,".bsp");'
    load = b'\tmBsp->LoadBsp(real_bsp_name);'
    opens = b'\tFILE *fp;'
    closes = b'\tfclose(fp);'
    reset = b'    state->mEnvironmentSceneFlags=0;'
    if any(body.count(mark) != 1 for mark in (path, load, opens, closes, reset)):
        raise ValueError('Required BSP loader/open boundary changed')
    begin = body.index(opens)
    after = body.index(reset, begin) + len(reset)
    supplied_check = body[begin:body.index(closes, begin) + len(closes)]
    supplied_check = supplied_check.replace(b'\t\tmBsp->SetIsLoaded(FALSE);',
                                            b'\t\tmIsLoadedBsp = FALSE;\n\t\tmBsp->SetIsLoaded(FALSE);')
    supplied_check = b'\n'.join(b'        ' + line for line in supplied_check.splitlines())
    body = body[:begin] + body[after:]
    acquire = b'''
    {
        // A distinct explicit input must still be readable. The canonical path
        // needs only the immutable lease used by both validation and loading.
        if (!prepared && _stricmp(name, real_bsp_name) != 0) {
''' + supplied_check + b'''
        }
        auto bspInput = prepared ? *prepared : RF455SceneInput455(real_bsp_name);
        if (!prepared && !bspInput.validateBsp()) {
            bspInput.reject(real_bsp_name);
            mIsLoadedBsp = FALSE;
            mBsp->SetIsLoaded(FALSE);
            return;
        }
        state->mEnvironmentSceneFlags = 0;
'''
    body = body.replace(path, path + acquire)
    material_probe = b'if( IsExistFile(load_name) )'
    material_load = b'auto* materials = LoadMainR3M(load_name);'
    if body.count(material_probe) != 2 or body.count(material_load) != 1:
        raise ValueError('Prepared map R3M route changed')
    body = body.replace(material_probe,
                        b'if (prepared ? static_cast<bool>(bspInput.mapMaterialBytes()) : IsExistFile(load_name))', 1)
    body = body.replace(material_load, b'''auto* materials = prepared
                ? RF455_LoadPreparedMainR3m455(load_name, bspInput.mapMaterialBytes())
                : LoadMainR3M(load_name);''')
    guarded = b'''        if (!mBsp->LoadBsp(real_bsp_name, &bspInput)) {
            mIsLoadedBsp = FALSE;
            mBsp->SetIsLoaded(FALSE);
            return;
        }
    }'''
    body = body.replace(b'void CLevel::LoadLevel(char *name)',b'''void CLevel::LoadLevel(char *name)
{
    LoadLevel(name, nullptr);
}

void CLevel::LoadLevel(char* name, const RF455SceneInput455* prepared)''',1)
    return b'#include "client455_scene_input.h"\n' + raw[:start] + body.replace(load, guarded) + raw[end:]


def port_scene_rpk_cache(raw, section):
    def replace_calls(signature, before, after, expected=1):
        nonlocal raw
        start, end = section(raw, signature, signature)
        body = raw[start:end]
        if body.count(before) != expected:
            raise ValueError('Scene RPK ownership boundary changed: ' + repr(signature))
        raw = raw[:start] + body.replace(before, after) + raw[end:]

    owner = b'    RF455_SetResourceGroup(&mResourceGroup);'
    load = b'    mResourceGroup.LoadDirectory(GetR3State()->EntityPath);'
    start, end = section(raw, b'BOOL CBsp::LoadBsp(', b'BOOL CBsp::LoadBsp(')
    newline = b'\r\n' if load + b'\r\n' + owner in raw[start:end] else b'\n'
    replace_calls(b'BOOL CBsp::LoadBsp(', load + newline + owner,
                  b'    RF455_SelectSceneResourceGroup(&mResourceGroup,GetR3State()->EntityPath);', 2)
    replace_calls(b'void CBsp::LoadEntities(', owner,
                  b'    RF455_ActivateSceneResourceGroup(&mResourceGroup);')
    replace_calls(b'void CBsp::ReleaseBsp()', b'    mResourceGroup.Release();',
                  b'    RF455_ReleaseSceneResourceGroup(&mResourceGroup);')
    replace_calls(b'CBsp::~CBsp()', b'{', b'''{
#if defined(RF_CLIENT_455_RESOURCE_IO)
    RF455_ReleaseSceneResourceGroup(&mResourceGroup);
#endif''')
    return raw


def guard_entity_material_load(raw, section):
    anchor = b'BOOL CEntity::LoadEntity('
    start, end = section(raw, anchor, anchor)
    body = raw[start:end]
    flag = b'\tif( mFlag & _DO_NOT_MANAGE_TEXTURE )'
    failure = b'\t\t\tfclose(fp);'
    binary = b'\t\tmMat = LoadSubR3M(r3m_path);'
    text = b'\t\tmMat = LoadSubMaterial(pmat_path);'
    if body.count(flag) != 2 or body.count(binary) != 1 or body.count(text) != 1:
        raise ValueError('Entity material caller boundaries changed')
    body = body.replace(flag, b'    const DWORD previousManageFlag = GetR3TexManageFlag();\n' + flag, 1)
    body = body.replace(binary, binary + b'''
        if (!mMat) {
            SetR3TexManageFlag(previousManageFlag);
            fclose(fp);
            return FALSE;
        }''')
    at = body.index(failure, body.index(text))
    body = body[:at] + b'            SetR3TexManageFlag(previousManageFlag);\n' + body[at:]
    return raw[:start] + body + raw[end:]


def port_entity_input(raw, section):
    anchor = b'BOOL CEntity::LoadEntity('
    start, end = section(raw, anchor, anchor)
    body = raw[start:end]
    first = body.index(b'\tstruct{')
    last = body.index(b'\tDWORD load_option;', first)
    warnings = re.findall(rb'Warning\(filename,([^\n]+?)\);', body[first:last])
    if len(warnings) != 2:
        raise ValueError('Entity input warning boundaries changed')
    body = body[:first] + b'''    // The sibling material and texture paths each occupy a 256-byte buffer.
    if (!filename || !*filename || strnlen_s(filename, 252) == 252) return FALSE;
    _strlwr(filename);
    std::unique_ptr<BYTE[]> inputStaging;
    _ENTITY_FILE_HEADER inputHeader{};
    {
        const auto source = RF455_ReadResourceBytes(filename, RF455EntityInputMaxBytes);
        // The engine warning formatter appends its own text to a fixed buffer.
        char warningPath[192];
        if (source.status != RF455ResourceReadStatus::Ready || !source.bytes) {
            strncpy_s(warningPath, sizeof(warningPath), filename, _TRUNCATE);
            Warning(warningPath, ''' + warnings[0] + b''');
            return FALSE;
        }
        RF455EntityInput parsed;
        if (!RF455_ParseEntityInput(source.bytes->data(), source.bytes->size(), parsed)) {
            RF455_GetCharacterRfsCache()->RemovePayloadBytes(source.bytes);
            strncpy_s(warningPath, sizeof(warningPath), filename, _TRUNCATE);
            Warning(warningPath, ''' + warnings[1] + b''');
            return FALSE;
        }
        inputStaging.reset(new (std::nothrow) BYTE[parsed.payloadSize]);
        if (!inputStaging) return FALSE;
        std::memcpy(inputStaging.get(), parsed.payload, parsed.payloadSize);
        inputHeader = parsed.header;
    }
    mMapColor = 0xff808080;
    mStartTime = 0;
    mFlag = option;
    mHeader = inputHeader;

''' + body[last:]
    body, removed = re.subn(rb'^[ \t]*fclose\(fp\);\r?\n', b'', body, flags=re.M)
    if removed != 3:
        raise ValueError('Entity stream close boundaries changed')
    first = body.index(b'\tbuf_size=0;')
    last = body.index(b'\tbuf_size=0;', first + 1)
    body = body[:first] + b'\tload_buf=inputStaging.get();\n' + body[last:]
    first = body.index(b'\tfread(comp_header,')
    last = body.index(b'\tint divide,vertex_num;', first)
    body = body[:first] + body[last:]
    body, removed = re.subn(rb'^[ \t]*Dfree\(load_buf\);\r?\n', b'', body, flags=re.M)
    if removed != 2:
        raise ValueError('Entity input staging ownership boundaries changed')
    body = body.replace(b'\tfloat version=_ENTITY_VERSION;\n', b'')
    body = body.replace(b'\tfloat version=_ENTITY_VERSION;\r\n', b'')
    # The source vertex IDs address this accumulator before expansion.
    old_normals = b'static_vertexnum*sizeof(Vector3f)'
    if body.count(old_normals) != 2:
        raise ValueError('Entity source normal allocation boundaries changed')
    body = body.replace(old_normals, b'vertex_num*sizeof(Vector3f)')
    includes = b'#include "client455_entity_input.h"\n#include "client455_resource_io.h"\n#include <memory>\n#include <new>\n'
    return includes + raw[:start] + body + raw[end:]


def sprite_access_header(raw):
    anchor = b'\tchar *GetFileName();'
    if raw.count(anchor) != 1:
        raise ValueError('Own sprite texture accessor anchor')
    return raw.replace(anchor, anchor + b'''
    bool IsLoaded455() const { return mIsLoadedTexMem != FALSE; }
    bool LoadMinimapSprite455(const char* name);
    bool HasFrame455(DWORD action,DWORD frame) const {
        return action < mActions && frame < mFrames[action] && mFrameInfo[action] != nullptr;
    }
    void* GetFrameTexture455() const {
        const DWORD action=mPageSPrite ? 0 : mNowAction;
        const DWORD frame=mPageSPrite ? mPage : mNowFrame;
        return HasFrame455(action,frame) ? mFrameInfo[action][frame].Tex : nullptr;
    }
''')


def port_sprite_resources(raw, native, section):
    loader = (native / 'client455_sprite_load.inc').read_bytes()
    load = b'void CSprite::LoadSprite('
    restore = b'void CSprite::RestoreTexMemSprite('
    start, end = section(raw, restore, restore)
    raw = raw[:start] + loader + b'\n' + raw[end:]
    start, end = section(raw, load, load)
    raw = raw[:start] + raw[end:]
    for signature in (b'void CSprite::DrawSprite(', b'void CSprite::DrawSpriteRot(',
                      b'void CSprite::DrawSpriteUV(', b'void CSprite::DrawSpriteRotUV(',
                      b'void CSprite::DrawSpriteVertex(', b'WORD CSprite::GetSpriteOrgXL(',
                      b'WORD CSprite::GetSpriteOrgYL(', b'WORD CSprite::GetSpriteXL(',
                      b'WORD CSprite::GetSpriteYL(', b'void CSprite::RunAnimation(',
                      b'DWORD CSprite::GetMaxFrames('):
        start, end = section(raw, signature, signature)
        opening = raw.index(b'{', start, end) + 1
        if b'GetMaxFrames' in signature:
            check = b'if (action >= mActions) return 0;'
        elif b'WORD CSprite::GetSprite' in signature:
            check = (b'if (mPageSPrite ? !HasFrame455(0,mPage) : !HasFrame455('
                     b'action == _NOW_STATE ? mNowAction : action, frame == _NOW_STATE ? mNowFrame : frame)) return 0;')
        elif any(key in signature for key in (b'RunAnimation', b'DrawSpriteRotUV', b'DrawSpriteVertex')):
            check = b'if (!HasFrame455(mNowAction,0)) return;' if b'RunAnimation' in signature \
                else b'if (!HasFrame455(mNowAction,mNowFrame)) return;'
        else:
            check = b'if (!HasFrame455(mPageSPrite ? 0 : mNowAction,mPageSPrite ? mPage : mNowFrame)) return;'
        raw = raw[:opening] + b'\n    ' + check + b'\n' + raw[opening:]
    return raw


def port_wave_resources(raw, section):
    init = b'BOOL InitR3SoundSystem(char *wav_spt_name)\n{'
    start, end = section(raw, init, init)
    body = raw[start:end]
    driver_open = (b'\tstDigital = AIL_open_digital_driver( DIGITALRATE, DIGITALBITS, DIGITALCHANNELS, 0 );\n'
                   b'\tif( !stDigital )\n\t\treturn FALSE;')
    if body.count(driver_open) != 1:
        raise ValueError('Audio driver startup boundary changed')
    body = body.replace(driver_open, b'''    // Miles 6.5c can crash in its default backend during device selection.
    AIL_set_preference(DIG_USE_WAVEOUT, 1);
    stDigital = AIL_open_digital_driver(DIGITALRATE, DIGITALBITS, DIGITALCHANNELS,
                                        AIL_OPEN_DIGITAL_FORCE_PREFERENCE);
    if (!stDigital) {
#ifndef NO_WAVE_PLAY
        ReleaseWaveList();
#endif
        AIL_shutdown();
        return FALSE;
    }''')
    raw = raw[:start] + body + raw[end:]

    manifest = b'void LoadWaveList(char *name)\n{'
    load_start, load_end = section(raw, manifest, manifest)
    release = b'void ReleaseWaveList()\n{'
    _, end = section(raw, release, release)
    first = b'static DWORD ConvertHexa('
    body = raw[load_start:load_end]
    opening = re.findall(rb'Error\(name,[^\r\n]+?\);', body)
    path_length = re.findall(rb'Warning\(hole,[^\r\n]+?\);', body)
    if raw.count(first) != 1 or len(opening) != 1 or len(path_length) != 1:
        raise ValueError('WaveList source boundaries changed')
    start = raw.index(first)
    body = (WS / 'scripts/native/client455_wave_manifest.inc').read_bytes()
    body = body.replace(b'@@OPEN_WARNING@@', opening[0].replace(b'Error(name,', b'Warning(warningName,', 1))
    body = body.replace(b'@@LONG_WARNING@@', path_length[0])
    raw = b'#include "client455_resource_text.h"\n' + raw[:start] + body + raw[end:]

    load = b'static BOOL LoadWave('
    start, end = section(raw, load, load)
    body = raw[start:end]
    anchor = b'\tif (AIL_set_named_sample_file( *Handle, name, ptr+1, ptr[0], -1 ) == 0)'
    at = body.index(anchor)
    opening = body.index(b'{', at) + 1
    body = body[:opening] + b'\n\t\tAIL_release_sample_handle(*Handle);\n\t\t*Handle=NULL;' + body[opening:]
    body = body.replace(anchor, b'\tif (!ptr[0] || ptr[0]>0x7fffffffu || AIL_set_named_sample_file(*Handle,name,ptr+1,ptr[0],-1)==0)')
    raw = raw[:start] + body + raw[end:]

    close = b'void ReleaseR3SoundSystem()\n{'
    start, end = section(raw, close, close)
    body = raw[start:end]
    wave_cleanup = b'#ifndef\tNO_WAVE_PLAY\n\tReleaseWaveList();\n#endif\n'
    driver_gate = b'\tif( stIsInit ==0 )'
    driver_close = b'\t\tAIL_close_digital_driver( stDigital );'
    if any(body.count(anchor) != 1 for anchor in (wave_cleanup, driver_gate, driver_close)):
        raise ValueError('Audio driver shutdown boundary changed')
    body = body.replace(wave_cleanup, b'')
    body = body.replace(driver_gate, wave_cleanup + b'\tIM_ReleaseAllWaves();\n' + driver_gate)
    body = body.replace(driver_close, driver_close + b'\n\t\tstDigital=NULL;')
    raw = raw[:start] + body + raw[end:]

    play = b'void PlayWave(DWORD id,DWORD flag,float vol,float pan)'
    # The legacy file has an inactive server-debug stub before the client function.
    start, end = section(raw, b'\n'+play+b'\n{', play)
    body = raw[start:end]
    first = body.index(b'\t_WAVE_PTR_LIST *get_wav;')
    last = body.index(b'\tif( get_wav->Handle )', first)
    missing = next(line for line in body[first:last].splitlines() if b'Warning(name,' in line)
    body = body[:first] + b'''    const DWORD real_id=GetRealID(id);
    if (real_id == static_cast<DWORD>(-1)) return;
    _WAVE_PTR_LIST* get_wav=nullptr;
    if (!stWaveCache.GetCache(id,reinterpret_cast<void**>(&get_wav))) {
        char* name=stWaveList[real_id].name;
        if (!IsExistFile(name)) {
'''+missing+b'''
            return;
        }
        _WAVE_PTR_LIST candidate={};
        if (!LoadWave(name,flag,&candidate.Handle,&candidate.ptr)) return;
        LONG result;
        try {
            result=stWaveCache.HitCache(id,reinterpret_cast<void**>(&get_wav));
        } catch (const std::bad_alloc&) {
            ReleaseWavePayload455(candidate);
            return;
        }
        if (result == _HITCACHE_RET_DEL_AND_NEW) ReleaseWavePayload455(*get_wav);
        *get_wav=candidate;
        stWaveList[real_id].flag=static_cast<BYTE>(flag);
    } else {
        stWaveCache.HitCache(id,reinterpret_cast<void**>(&get_wav));
    }
''' + body[last:]
    return raw[:start] + body + raw[end:]


def copy_map_particle_template(raw):
    anchor = (b'\t\t\tmMapEntitiesList[i].Particle = particle;\n'
              b'\t\t\tmemcpy(particle,&mParticle[mMapEntitiesList[i].ID],sizeof(CParticle));')
    if raw.count(anchor) != 1:
        raise ValueError('Map particle instance boundary changed')
    return raw.replace(anchor, b'''            if (!particle->CopyTemplate455(mParticle[mMapEntitiesList[i].ID])) {
                delete particle;
                continue;
            }
            mMapEntitiesList[i].Particle = particle;''')


def copy_effect_particle_template(raw):
    anchor = b'\t\tmemcpy(particle,stEffectEntityList[real_id].Particle,sizeof(CParticle));'
    if raw.count(anchor) != 2:
        raise ValueError('Effect particle instance boundaries changed')
    return raw.replace(anchor, b'''        if (!particle->CopyTemplate455(*stEffectEntityList[real_id].Particle)) {
            delete particle;
            return NULL;
        }''')


def port_reflection_device_init(raw, section, replace):
    # The 455 optional Reflection load has its own capability gate.
    raw=b'''#if defined(RF_CLIENT_455_CACHED_VERTEX_SHADER)
void RF455_LoadReflectionShader();
#endif
'''+raw
    first,last=section(raw,b'HRESULT D3D_R3InitDevice(',b'HRESULT D3D_R3InitDevice(')
    body=replace(raw[first:last],b'    return S_OK;',b'''#if defined(RF_CLIENT_455_CACHED_VERTEX_SHADER)
    RF455_LoadReflectionShader();
#endif
    return S_OK;''')
    return raw[:first]+body+raw[last:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clean-first', action='store_true',
                        help='Recompile engine objects from retained source and headers')
    parser.add_argument('--ninja', action='store_true',
                        help='Use bundled Ninja from a VS 2026 x86 developer shell')
    args = parser.parse_args()
    if args.ninja and os.environ.get('VSCMD_ARG_TGT_ARCH') != 'x86':
        parser.error('--ninja requires a VS 2026 x86 developer shell')

    base=WS/'work/client455-port';root=base/'startup-engine';art=WS/'artifacts/client455-startup-engine';art.mkdir(parents=True,exist_ok=True);root.mkdir(parents=True,exist_ok=True)
    template=base/'CMakeLists.txt';cmakeText=template.read_text();sources=[]
    for match in re.finditer(r'^ "([^"]+\.cpp)"$',cmakeText,re.M):
        source=Path(match[1]);sources.append({'file':source.relative_to(WS).as_posix(),'sha256':sha(source)})
    if len(sources)!=67:raise ValueError('Base engine source list changed')
    previous=json.loads((WS/'inventory/client455-startup-engine-build.json').read_text()) if (WS/'inventory/client455-startup-engine-build.json').exists() else {};old={row['file']:row['sha256'] for row in previous.get('derived_sources',[])};derived=[]
    generationFile=root/'generated-source-hashes.json'
    generated=json.loads(generationFile.read_text()) if generationFile.exists() else {}
    from client455_particle_port import headers,particle_source,entity_source
    import client455_lighting_port as lighting130
    import client455_material_port as material133
    import client455_material_shader_port as shaders135
    materialInput=base/'source/R3Engine/1stclass/r3material.h';materialHeader=root/'include/r3material455.h'
    materialRaw=material133.header(materialInput.read_bytes());materialKey=materialHeader.relative_to(WS).as_posix()
    if materialHeader.exists() and materialHeader.read_bytes()!=materialRaw and sha(materialHeader) not in {previous.get('material_header_overlay',{}).get('sha256'),generated.get(materialKey)}:raise ValueError('Preserving changed material declaration')
    if not materialHeader.exists() or materialHeader.read_bytes()!=materialRaw:materialHeader.write_bytes(materialRaw)
    generated[materialKey]=sha(materialHeader);generationFile.write_text(json.dumps(generated,indent=2)+'\n')
    particleHeaders=headers(base,root,previous)
    vertexInput=base/'source/R3Engine/1stclass/r3d3d8.h';vertexHeader=root/'include/r3d3d8455.h'
    vertexRaw=lighting130.vertex_header(vertexInput.read_bytes())
    vertexKey=vertexHeader.relative_to(WS).as_posix()
    if vertexHeader.exists() and vertexHeader.read_bytes()!=vertexRaw and sha(vertexHeader) not in {previous.get('vertex_header_overlay',{}).get('sha256'),generated.get(vertexKey)}:raise ValueError('Preserving changed owned455 vertex declarations')
    if not vertexHeader.exists() or vertexHeader.read_bytes()!=vertexRaw:vertexHeader.write_bytes(vertexRaw)
    generated[vertexKey]=sha(vertexHeader);generationFile.write_text(json.dumps(generated,indent=2)+'\n')
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
    bspRaw=bspRaw.replace(bspAnchor,b'\tfriend void RF455_RenderLobbyShadows(CBsp*);\n'+(WS/'scripts/native/client455_bsp_fields.inc').read_bytes()+b'\n'+bspAnchor)
    bspRaw=port_scene_bsp_header(bspRaw)
    bspKey=bspHeader.relative_to(WS).as_posix()
    if bspHeader.exists() and bspHeader.read_bytes()!=bspRaw and sha(bspHeader) not in {previous.get('bsp_header_overlay',{}).get('sha256'),generated.get(bspKey)}:raise ValueError('Preserving changed own BSP declaration')
    if not bspHeader.exists() or bspHeader.read_bytes()!=bspRaw:bspHeader.write_bytes(bspRaw)
    generated[bspKey]=sha(bspHeader);generationFile.write_text(json.dumps(generated,indent=2)+'\n')
    # One declaration is forced into every engine/client consumer through the
    # existing shared camera overlay. Add only an own inline texture accessor;
    # CSprite layout and virtual dispatch remain unchanged.
    spriteInput=base/'source/R3Engine/2ndclass/2dsprite.h';spriteHeader=root/'include/2dsprite455.h';spriteHeader.parent.mkdir(parents=True,exist_ok=True)
    spriteRaw=sprite_access_header(spriteInput.read_bytes())
    if spriteHeader.exists() and spriteHeader.read_bytes()!=spriteRaw and sha(spriteHeader)!=previous.get('sprite_header_overlay',{}).get('sha256'):raise ValueError('Preserving changed own sprite declaration')
    if not spriteHeader.exists() or spriteHeader.read_bytes()!=spriteRaw:spriteHeader.write_bytes(spriteRaw)
    ownedParticleHeader=root/'include/particle455.h'
    particlePrefix=('#include "'+(base/'port_std.hpp').as_posix()+'"\r\n#include "c_vector.h"\r\n'+''.join('#include "'+(WS/row['file']).as_posix()+'"\r\n' for row in particleHeaders)).encode()
    particlePrefix+=('#include "'+bspHeader.as_posix()+'"\r\n').encode()
    particlePrefix=particlePrefix.replace(b'#include "c_vector.h"\r\n',('#include "'+coreHeader.as_posix()+'"\r\n#include "c_vector.h"\r\n').encode(),1)
    particlePrefix+=('#include "'+skyHeader.as_posix()+'"\r\n').encode()
    particlePrefix=particlePrefix.replace(('#include "'+(base/'port_std.hpp').as_posix()+'"\r\n').encode(),('#include "'+(base/'port_std.hpp').as_posix()+'"\r\n#include "'+vertexHeader.as_posix()+'"\r\n').encode(),1)
    particlePrefix=particlePrefix.replace(('#include "'+(base/'port_std.hpp').as_posix()+'"\r\n').encode(),('#include "'+(base/'port_std.hpp').as_posix()+'"\r\n#include "'+materialHeader.as_posix()+'"\r\n').encode(),1)
    if ownedParticleHeader.exists() and ownedParticleHeader.read_bytes()!=particlePrefix and sha(ownedParticleHeader)!=previous.get('particle_header_overlay',{}).get('sha256'):raise ValueError('Preserving changed particle prefix')
    if not ownedParticleHeader.exists() or ownedParticleHeader.read_bytes()!=particlePrefix:ownedParticleHeader.write_bytes(particlePrefix)
    levelInput=base/'source/R3Engine/2ndclass/level.h';levelHeader=root/'include/level455.h'
    levelRaw=port_scene_level_header(levelInput.read_bytes());levelAnchor=b'\tCLevel();'
    if levelRaw.count(levelAnchor)!=1:raise ValueError('CLevel weather declaration boundary')
    levelRaw=levelRaw.replace(levelAnchor,b'\tvirtual void SetWeatherColor455(DWORD color);\n\tDWORD GetWeatherColor455()const{return mWeatherColor455;}\n'+levelAnchor)
    levelEnd=levelRaw.rfind(b'};')
    levelRaw=levelRaw[:levelEnd]+b'private:\n\tDWORD mWeatherColor455; //populated by successful load or explicit setter\n'+levelRaw[levelEnd:]
    levelKey=levelHeader.relative_to(WS).as_posix()
    if levelHeader.exists() and levelHeader.read_bytes()!=levelRaw and sha(levelHeader) not in {previous.get('level_header_overlay',{}).get('sha256'),generated.get(levelKey)}:raise ValueError('Preserving changed owned level declaration')
    if not levelHeader.exists() or levelHeader.read_bytes()!=levelRaw:levelHeader.write_bytes(levelRaw)
    generated[levelKey]=sha(levelHeader);generationFile.write_text(json.dumps(generated,indent=2)+'\n')
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
    header+=('#include "'+levelHeader.as_posix()+'"\r\n').encode()
    header=header.replace(firstInclude,firstInclude+('#include "'+vertexHeader.as_posix()+'"\r\n').encode(),1)
    header=header.replace(firstInclude,firstInclude+('#include "'+materialHeader.as_posix()+'"\r\n').encode(),1)
    if ownedHeader.exists() and ownedHeader.read_bytes()!=header and sha(ownedHeader)!=previous.get('camera_header_overlay',{}).get('sha256'):raise ValueError('Preserving changed owned camera declaration')
    if not ownedHeader.exists() or ownedHeader.read_bytes()!=header:ownedHeader.write_bytes(header)
    for filename in ['jerror.cpp','jmalloc.cpp','cjcache.cpp','r3enginekernel.cpp','r3d3dwrapper.cpp','r3d3dapp.cpp','r3text.cpp','2dsprite.cpp','r3d3dtex.cpp','r3lightmap.cpp','anicamera.cpp','level.cpp','extdummy.cpp','r3d3d8.cpp','rtmovie.cpp','r3util.cpp','r3particle.cpp','entity.cpp','effectentitylist.cpp','r3sound.cpp','bsp.cpp','core.cpp','skybox.cpp','r3vertexbuffer.cpp','r3material.cpp','r3render.cpp','renderentity.cpp','r3vertexshader.cpp','renderparticle.cpp']:
        folder='common' if filename in ('jerror.cpp','jmalloc.cpp','cjcache.cpp') else ('1stclass' if filename in ['r3d3dtex.cpp','r3lightmap.cpp','r3d3d8.cpp','r3particle.cpp','entity.cpp','bsp.cpp','core.cpp','skybox.cpp','r3vertexbuffer.cpp','r3material.cpp','r3render.cpp','renderentity.cpp','r3vertexshader.cpp','renderparticle.cpp'] else ('extension' if filename in ['rtmovie.cpp','effectentitylist.cpp'] else '2ndclass'))
        source=base/'source/R3Engine'/folder/filename;raw=source.read_bytes()
        if filename=='jerror.cpp':
            from prepare_client455_normal import section
            start,end=section(raw,b'void Warning(',b'void Warning(')
            raw=raw[:start]+(WS/'scripts/native/client455_warning.inc').read_bytes()+raw[end:]
        elif filename=='jmalloc.cpp':
            raw=port_resource_allocator(raw, WS/'scripts/native')
        elif filename=='cjcache.cpp':
            from client455_wave_cache_port import port_wave_cache
            raw=port_wave_cache(raw)
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
            raw=port_device_wrapper_results(raw)
        elif filename=='r3d3dapp.cpp':
            from client455_d3d9_edits import replace
            from prepare_client455_normal import section

            raw = port_device_replacement_release(port_scene_reset_scope(raw, section), section)
            raw = b'#include "client455_multisampling.h"\r\n#include "client455_render_diagnostics.h"\r\n' + raw
            first,last=section(raw,b'HRESULT CD3DApplication::EndLoop()',b'HRESULT CD3DApplication::EndLoop()')
            body=raw[first:last];at=body.index(b'{')+1
            raw=raw[:first]+body[:at]+b'\n    RF455CpuSection presentTiming(1);\n'+body[at:]+raw[last:]
            # 455's ordinary window has a caption and minimize button, with a fixed client size.
            raw = replace(raw, b'WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_THICKFRAME|',
                          b'WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|')
            menu = b'LoadMenu( hInstance, MAKEINTRESOURCE(IDR_MENU) )'
            raw = replace(raw, menu, b'menu')
            raw = replace(raw, b'AdjustWindowRect( &rc, m_dwWindowStyle, TRUE );',
                          b'const HMENU menu = ' + menu + b';\r\n'
                          b'        AdjustWindowRect( &rc, m_dwWindowStyle, menu != NULL );')
            raw = replace(raw, b'    // Create the device\n    hr = m_pD3D->CreateDevice(',
                          b'''    m_d3dpp.PresentationInterval = RF455_PresentationInterval();
    m_d3dpp.MultiSampleType = RF455_SelectMultisampling(*m_pD3D, m_dwAdapter,
                                                        pDeviceInfo->DeviceType, m_d3dpp);
    // Create the device
    hr = m_pD3D->CreateDevice(''')
            raw = replace(raw, b'&m_pd3dDevice );\n    if( SUCCEEDED(hr) )', b'''&m_pd3dDevice );
    if (FAILED(hr) && m_d3dpp.MultiSampleType != D3DMULTISAMPLE_NONE) {
        m_d3dpp.MultiSampleType = D3DMULTISAMPLE_NONE;
        hr = m_pD3D->CreateDevice(m_dwAdapter, pDeviceInfo->DeviceType,
                                 m_hWndFocus, pModeInfo->dwBehavior, &m_d3dpp, &m_pd3dDevice);
    }
    if( SUCCEEDED(hr) )''')
            raw = replace(raw, b'    if( FAILED( hr = m_pd3dDevice->Reset( &m_d3dpp ) ) )\n        return hr;', b'''    const auto& adapter = m_Adapters[m_dwAdapter];
    m_d3dpp.PresentationInterval = RF455_PresentationInterval();
    m_d3dpp.MultiSampleType = RF455_SelectMultisampling(*m_pD3D, m_dwAdapter,
        adapter.devices[adapter.dwCurrentDevice].DeviceType, m_d3dpp);
    hr = RF455_ResetPresentation(*m_pd3dDevice, m_d3dpp);
    if (FAILED(hr)) return hr;''')
        elif filename=='r3text.cpp':
            anchor=b'static CR3Font stCR3Font;'
            if raw.count(anchor)!=1:raise ValueError('Legacy active text boundary changed')
            header=(WS/'scripts/native/client455_font.h').as_posix()
            raw=(f'#include "{header}"\n'.encode()+raw[:raw.index(anchor)]+(WS/'scripts/native/client455_text_bridge.inc').read_bytes())
        elif filename=='2dsprite.cpp':
            from prepare_client455_normal import section
            raw=port_sprite_resources(raw, WS/'scripts/native', section)
        elif filename=='extdummy.cpp':
            from prepare_client455_normal import section
            raw=port_ext_dummy_resource(raw, WS/'scripts/native', section)
        elif filename=='r3d3dtex.cpp':
            from prepare_client455_normal import section
            raw=port_r3t_resources(raw, WS/'scripts/native', section)
            start,end=section(raw,b'void *GetDDSTexFromBuffer(',b'void *GetDDSTexFromBuffer(')
            raw=raw[:start]+(WS/'scripts/native/client455_sprite_texture.inc').read_bytes()+raw[end:]
        elif filename=='r3lightmap.cpp':
            from prepare_client455_normal import section
            start,end=section(raw,b'void LoadLightMap(',b'void LoadLightMap(')
            raw=raw[:start]+(WS/'scripts/native/client455_lightmap_owner.inc').read_bytes()+raw[end:]
        elif filename=='bsp.cpp':
            raw=copy_map_particle_template(raw)
            raw+=b'\n'+(WS/'scripts/native/client455_lobby_shadow_bsp.inc').read_bytes()
            entityOwnerAnchor=b'\t\t\tmEntity[i].RestoreTexMem();'
            if raw.count(entityOwnerAnchor)!=1:raise ValueError('Successful map entity light owner boundary')
            raw=raw.replace(entityOwnerAnchor,(WS/'scripts/native/client455_map_entity_owner.inc').read_bytes()+b'\n'+entityOwnerAnchor)
            from prepare_client455_normal import section
            raw=port_scene_bsp(raw, section)
            raw=port_scene_rpk_cache(raw, section)
            raw=port_bsp_map_shader_lights(raw, section)
            raw=b'#include "client455_bsp_light.h"\n'+raw
            start,end=section(raw,b'void CBsp::DrawDynamicLightSub(',b'void CBsp::DrawDynamicLightSub(');raw=raw[:start]+raw[end:]
            start,end=section(raw,b'void CBsp::DrawMagicLightSub(',b'void CBsp::DrawMagicLightSub(');raw=raw[:start]+(WS/'scripts/native/client455_bsp_light.inc').read_bytes()+raw[end:]
            start,end=section(raw,b'short CBsp::GetLeafNum(',b'short CBsp::GetLeafNum(');raw=raw[:start]+(WS/'scripts/native/client455_bsp_leaf.inc').read_bytes()+raw[end:]
            start,end=section(raw,b'void CBsp::ClearVariable()',b'void CBsp::ClearVariable()');body=raw[start:end];at=body.index(b'{')+1
            raw=raw[:start]+body[:at]+b'\nD3DXMatrixIdentity(&mWorldMatrix455);D3DXMatrixIdentity(&mInverseWorldMatrix455);'+body[at:]+raw[end:]
        elif filename=='level.cpp':
            from prepare_client455_normal import section
            raw=guard_level_material_load(raw, section)
            raw=b'#include "client455_sky_atmosphere.h"\n'+raw
            raw+=b'\n'+(WS/'scripts/native/client455_sky_atmosphere.inc').read_bytes()
            raw=b'#include "client455_sky_lighting.h"\n'+raw
            raw=b'#include "client455_weather_parameters.h"\n'+raw
            raw+=b'\n'+(WS/'scripts/native/client455_sky_lighting.inc').read_bytes()
            raw+=b'\n'+(WS/'scripts/native/client455_level_weather.inc').read_bytes()
            weatherAnchor=b'\tmBsp->LoadBsp(real_bsp_name);'
            if raw.count(weatherAnchor)!=1:raise ValueError('Successful ordinary map weather owner boundary')
            weatherAt=raw.index(weatherAnchor);resetAnchor=b'\tResetTexMemSize();'
            resetAt=raw.rfind(resetAnchor,0,weatherAt)
            if resetAt<0 or raw[resetAt+len(resetAnchor):weatherAt].strip():raise ValueError('Map weather/reset ordering changed')
            raw=raw[:resetAt]+b'    SetWeatherColor455(RF455_GetMaterialWeather());\n'+raw[resetAt:]
            raw=b'#include "client455_sky_day.h"\n'+raw
            raw+=b'\n'+(WS/'scripts/native/client455_sky_day.inc').read_bytes()
            clockAnchor=b'    RF455_AdvanceDayClock();'
            if raw.count(clockAnchor)!=1:raise ValueError('Ordinary sky day frame boundary')
            raw=raw.replace(clockAnchor,clockAnchor+b'\n    RF455_UpdateSkyLighting();')
            first,last=section(raw,b'void CLevel::DrawMapRender()',b'void CLevel::DrawMapRender()');body=raw[first:last]
            drawAnchor=b'\tmBsp->DrawBspRender();'
            if body.count(drawAnchor)!=1:raise ValueError('Ordinary map texture-factor boundary')
            raw=raw[:first]+body.replace(drawAnchor,b'    GetD3dDevice()->SetRenderState(D3DRS_TEXTUREFACTOR,RF455_GetSkyTintColor());\n'+drawAnchor)+raw[last:]
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
            raw=port_scene_level(raw, section)
            raw=port_level_map_shader_lights(raw)
        elif filename=='core.cpp':
            from client455_d3d9_edits import replace
            raw = replace(raw, b'\tstState.mViewYL=(LONG)stState.mScreenYsize;',
                          b'\tstState.mViewYL=(LONG)stState.mScreenYsize;\n'
                          b'    if (stState.mScreenXsize > 0 && stState.mScreenYsize > 0)\n'
                          b'        stState.mAsfectRatio = stState.mScreenXsize / stState.mScreenYsize;')
            raw=b'#include "client455_sky_lighting.h"\n'+raw
            anchor=b'memset(&stState,0,sizeof(_R3ENGINE_STATE));'
            if raw.count(anchor)!=1:raise ValueError('Core initialization boundary')
            raw=raw.replace(anchor,anchor+b'\n    RF455_ResetSkyFogEndpoints();\n\tstState.mOrthographic=FALSE;stState.mOrthographicScale=5.0f; //4558C3614/20')
        elif filename=='r3material.cpp':
            raw=material133.material(raw)
            from prepare_client455_normal import section
            raw=port_r3x_resource(raw, section)
            raw=b'#include "client455_sky_lighting.h"\n#include "client455_weather_format.h"\n'+raw
            first,last=section(raw,b'static _R3MATERIAL* LoadIndependenceMaterial(',b'static _R3MATERIAL* LoadIndependenceMaterial(');body=raw[first:last]
            tokenAnchor=b'\t\tstrupr(hole);'
            if body.count(tokenAnchor)!=1:raise ValueError('Actual uppercase material token dispatch boundary')
            #45590A5ED folds each newly read tag to uppercase before FOG/ENV.
            #The late weather callback folds the then-current token to lowercase.
            fogFirst=body.index(b'        if (!strcmp(hole,"*FOG_START"))')
            fogLast=body.index(b'        if (!strcmp(hole,"*NO_FOG_SKY"))',fogFirst)
            body=body[:fogFirst]+b'        RF455_ReadSkyFogToken(fp,hole);\n'+body[fogLast:]
            raw=raw[:first]+body+raw[last:]
            anchor=b'    state->mEnvironmentSceneFlags=ext_mat.mSceneFlags;'
            if raw.count(anchor)!=1:raise ValueError('R3X day/night endpoint boundary')
            raw=raw.replace(anchor,anchor+b'\n    RF455_LoadSkyFogEndpoints(ext_mat);')
            raw=material133.port_mst_resources(raw, section)
        elif filename=='skybox.cpp':
            from prepare_client455_normal import section
            raw=b'#include "client455_sky_day.h"\n#include "client455_sky_fade_math.h"\n#include "client455_sky_atmosphere.h"\n'+raw
            first,last=section(raw,b'void CSkyBox::DrawSkyBox(',b'void CSkyBox::DrawSkyBox(')
            raw=raw[:first]+(WS/'scripts/native/client455_sky_material.inc').read_bytes()+raw[last:]
        elif filename=='r3vertexbuffer.cpp':
            raw=port_buffer_create_failure(raw)
        elif filename=='r3d3d8.cpp':
            from prepare_client455_normal import section
            from client455_d3d9_edits import replace
            raw=port_buffer_device_lifetime(raw, section)
            raw = replace(raw, b'void SetViewPortArea(LONG sx,LONG sy,LONG xl,LONG yl)\n{',
                          b'void SetViewPortArea(LONG sx,LONG sy,LONG xl,LONG yl)\n{\n'
                          b'    if (xl <= 0 || yl <= 0) return;')
            raw = replace(raw, b'//\tstate->mAsfectRatio = (float)xl/(float)yl;',
                          b'    state->mAsfectRatio = float(xl) / float(yl);')
            raw=b'#include "client455_special_shaders.h"\n'+raw
            raw+=b'\n'+(WS/'scripts/native/client455_special_shaders.inc').read_bytes()
            first,last=section(raw,b'HRESULT D3D_R3RestoreDevice()',b'HRESULT D3D_R3RestoreDevice()');body=raw[first:last];anchor=b'\tInitFullScreenEffect();'
            if body.count(anchor)!=1:raise ValueError('Special shader restore boundary')
            raw=raw[:first]+body.replace(anchor,anchor+b'\n    RF455_ReleaseSpecialShaders();\n    RF455_LoadSpecialShaderBinary();')+raw[last:]
            first,last=section(raw,b'HRESULT D3D_R3InvalidateDevice()',b'HRESULT D3D_R3InvalidateDevice()');body=raw[first:last];at=body.index(b'{')+1
            raw=raw[:first]+body[:at]+b'\n    RF455_ReleaseSpecialShaders();'+body[at:]+raw[last:]
            raw=b'#include "client455_entity_lighting.h"\n#include "client455_lobby_post.h"\n#include "client455_lobby_material.h"\n#include "client455_lobby_sky.h"\n#include "client455_lobby_shadow.h"\n'+raw
            first,last=section(raw,b'HRESULT D3D_R3InvalidateDevice()',b'HRESULT D3D_R3InvalidateDevice()');body=raw[first:last];at=body.index(b'{')+1
            raw=raw[:first]+body[:at]+b'\n    RF455_ReleaseLobbyShadows();\n    RF455_ReleaseLobbySky();\n    RF455_ReleaseLobbyMaterial();\n    RF455_ReleaseLobbyPost();'+body[at:]+raw[last:]
            raw=raw.replace(b'pd3dDevice->GetDeviceCaps(&caps);',b'pd3dDevice->GetDeviceCaps(&caps);\n    RF455_SetLightingCaps(&caps);')
            raw=port_reflection_device_init(raw,section,replace)
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
            raw=b'#include "client455_scene_capture.h"\n'+raw
            first,last=section(raw,b'void ReleaseFullScreenEffect()',b'void ReleaseFullScreenEffect()')
            raw=raw[:first]+raw[last:]
            first,last=section(raw,b'void InitFullScreenEffect()',b'void InitFullScreenEffect()')
            raw=raw[:first]+(WS/'scripts/native/client455_scene_capture.inc').read_bytes()+raw[last:]
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
        elif filename=='effectentitylist.cpp':raw=copy_effect_particle_template(raw)
        elif filename=='entity.cpp':
            from prepare_client455_normal import section
            raw=guard_entity_material_load(lighting130.entity(entity_source(raw)), section)
            raw=port_entity_input(raw, section)
        elif filename=='renderentity.cpp':raw=lighting130.render_entity(raw)
        elif filename=='r3render.cpp':raw=port_managed_uv_lock(shaders135.render(lighting130.material(raw)))
        elif filename=='renderparticle.cpp':raw=shaders135.particle_render(raw)
        elif filename=='r3vertexshader.cpp':raw=lighting130.shader(raw)
        elif filename=='r3sound.cpp':
            from prepare_client455_normal import section
            raw=port_wave_resources(raw, section)
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
    cmakeText+='\ntarget_compile_definitions(R3Engine455Startup PRIVATE RF_CLIENT_455_CACHED_VERTEX_SHADER)\n'
    post_source=WS/'scripts/native/client455_lobby_post.cpp'
    sky_source=WS/'scripts/native/client455_lobby_sky.cpp'
    shadow_source=WS/'scripts/native/client455_lobby_shadow.cpp'
    diagnostics_source=WS/'scripts/native/client455_render_diagnostics.cpp'
    resource_bytes_source=WS/'scripts/native/client455_resource_bytes.cpp'
    for modern_source in [post_source,sky_source,shadow_source,diagnostics_source,resource_bytes_source]:
        cmakeText+='\ntarget_sources(R3Engine455Startup PRIVATE "'+modern_source.as_posix()+'")\n'
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
    info = json.loads((WS/'inventory/msvc-verification.json').read_text())
    tools = Path(info['installation_path'])/'Common7/IDE/CommonExtensions/Microsoft/CMake'
    cmake = tools/'CMake/bin/cmake.exe'
    ninja = tools/'Ninja/ninja.exe'
    oldLibrary=base/'build-vs2026/Release/R3Engine455.lib';oldHash=sha(oldLibrary)
    if args.ninja:
        build = root/'ninja-build'
        generator = 'Ninja'
        options = ['-DCMAKE_BUILD_TYPE=Release', f'-DCMAKE_MAKE_PROGRAM={ninja}',
                   '-DCMAKE_CXX_COMPILER=cl.exe', '-DCMAKE_SUPPRESS_REGENERATION=ON']
        library = build/'R3Engine455Startup.lib'
        object_directory = build/'CMakeFiles/R3Engine455Startup.dir'
        log_prefix = 'ninja-'
    else:
        build = root/'build'
        generator = 'Visual Studio 18 2026'
        options = ['-A', 'Win32', '-T', 'v145', '-DCMAKE_SYSTEM_VERSION=10.0.26100.0']
        library = build/'Release/R3Engine455Startup.lib'
        object_directory = build/'R3Engine455Startup.dir/Release'
        log_prefix = ''
    config=subprocess.run([str(cmake),'-S',str(root),'-B',str(build),'-G',generator,*options],capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW);(art/(log_prefix+'configure.txt')).write_bytes(config.stdout+config.stderr)
    if config.returncode:raise ValueError('Derived engine configure failed')
    command = [str(cmake), '--build', str(build), '--config', 'Release',
               '--target', 'R3Engine455Startup', '--parallel', '4']
    clean_first = args.clean_first
    if args.ninja:
        object_file = (object_directory / 'source/bsp.cpp.obj').relative_to(build).as_posix()
        header = 'client455_scene_input.h'
        ninja_dependencies, recover = prepare_ninja_dependencies(ninja, build, previous, object_file, header)
        clean_first = clean_first or recover
    if clean_first:
        command.append('--clean-first')
    result = subprocess.run(command, capture_output=True, timeout=300, creationflags=subprocess.CREATE_NO_WINDOW)
    log = art/(log_prefix+'build.txt')
    log.write_bytes(result.stdout+result.stderr)
    if result.returncode:raise ValueError('Derived engine build:'+str(log))
    if args.ninja and not ninja_has_header(ninja, build, object_file, header):
        raise ValueError(f'Ninja did not record {header} for {object_file}: {log}')
    objects=list(object_directory.rglob('*.obj'))
    if len(objects)!=72 or sha(oldLibrary)!=oldHash or any(sha(WS/row['file'])!=row['sha256'] for row in sources):raise ValueError('Engine source/object/baseline drift')
    report={'scope':'Derived source engine with455color32 call and strict Create exit policy;remaining wrapper/camera/console/whole startup semantics open','architecture':'x86','build_exit':0,'objects':67,'library':library.relative_to(WS).as_posix(),'library_sha256':sha(library),'base_cmake':{'file':template.relative_to(WS).as_posix(),'sha256':sha(template)},'base_sources':sources,'derived_sources':derived,'baseline_library':{'file':oldLibrary.relative_to(WS).as_posix(),'sha256':oldHash},'cmake':{'file':(root/'CMakeLists.txt').relative_to(WS).as_posix(),'sha256':sha(root/'CMakeLists.txt')},'log':{'file':log.relative_to(WS).as_posix(),'sha256':sha(log)},'script_sha256':sha(WS/'scripts/build_client455_engine_startup.py'),'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    report['text_bridge']={name:sha(WS/'scripts/native'/name) for name in ['client455_text_bridge.inc','client455_font.h']}
    report['generator'] = generator
    report['clean_first'] = clean_first
    if args.ninja:
        report['ninja_dependencies'] = ninja_dependencies
    report.update(objects=len(objects),expected_objects=72,lobby_post_source={'file':post_source.relative_to(WS).as_posix(),'sha256':sha(post_source)},lobby_sky_source={'file':sky_source.relative_to(WS).as_posix(),'sha256':sha(sky_source)},lobby_shadow_source={'file':shadow_source.relative_to(WS).as_posix(),'sha256':sha(shadow_source)},render_diagnostics_source={'file':diagnostics_source.relative_to(WS).as_posix(),'sha256':sha(diagnostics_source)})
    report['lobby_texture']={name:sha(WS/'scripts/native'/name) for name in
                             ['client455_lobby_texture.h','client455_lobby_material.inc']}
    report['sprite_texture']={name:sha(WS/'scripts/native'/name) for name in
                              ['client455_sprite_texture.inc','client455_sprite_load.inc']}
    report['r3t_resources']={name:sha(WS/'scripts/native'/name) for name in ['client455_r3t_load.inc','client455_dds_stream.inc','client455_dds_load.inc','client455_dds_d3dx.inc','client455_lightmap_stream.inc','client455_lightmap_owner.inc']}
    report['resource_allocator']={name:sha(WS/'scripts/native'/name) for name in
                                  ['client455_dmalloc.inc','client455_mst_texture_registry.inc']}
    report['scene_input_sha256']=sha(WS/'scripts/native/client455_scene_input.h')
    report['entity_input']={name:sha(WS/'scripts/native'/name) for name in ['client455_entity_input.h','client455_resource_bytes.cpp']}
    report['warning']={'client455_warning.inc':sha(WS/'scripts/native/client455_warning.inc')}
    report['quake']={name:sha(WS/'scripts/native'/name) for name in ['client455_quake.h','client455_quake.inc','client455_quake_density.inc','client455_level_view.inc']}
    report['bsp_light']={name:sha(WS/'scripts/native'/name) for name in ['client455_bsp_light.h','client455_bsp_fields.inc','client455_bsp_light.inc']}
    report['map_shader_lights']={name:sha(WS/'scripts/native'/name) for name in ['client455_map_shader_lights.h','client455_shader_lights.h']}
    report['bsp_leaf']={'client455_bsp_leaf.inc':sha(WS/'scripts/native/client455_bsp_leaf.inc')}
    report['scene_input']={name:sha(WS/'scripts/native'/name) for name in ['client455_scene_input.h','client455_bsp_positions.h']}
    report['buffer_binding_sha256']=sha(WS/'scripts/native/client455_buffer_binding.h')
    report['sky_projection']={'client455_sky_projection.inc':sha(WS/'scripts/native/client455_sky_projection.inc')}
    report['sky_fade']={name:sha(WS/'scripts/native'/name) for name in ['client455_sky_fade_math.h','client455_sky_fade.inc']}
    report['sky_material']={name:sha(WS/'scripts/native'/name) for name in ['client455_sky_day.h','client455_sky_day.inc','client455_map_sky.inc','client455_sky_material.inc']}
    report['sky_atmosphere']={name:sha(WS/'scripts/native'/name) for name in ['client455_sky_atmosphere.h','client455_sky_atmosphere.inc']}
    report['sky_lighting']={name:sha(WS/'scripts/native'/name) for name in ['client455_sky_lighting.h','client455_sky_lighting.inc','client455_sky_lighting_math.h']}
    report['weather_parameters']={name:sha(WS/'scripts/native'/name) for name in ['client455_weather_parameters.h','client455_weather_parameters.inc','client455_level_weather.inc','client455_weather.cpp']}
    report['level_header_overlay']={'file':levelHeader.relative_to(WS).as_posix(),'sha256':sha(levelHeader),'original':levelInput.relative_to(WS).as_posix(),'original_sha256':sha(levelInput)}
    report['vertex_header_overlay']={'file':vertexHeader.relative_to(WS).as_posix(),'sha256':sha(vertexHeader),'original':vertexInput.relative_to(WS).as_posix(),'original_sha256':sha(vertexInput)}
    report['lighting_consumers']={name:sha(WS/'scripts/native'/name) for name in ['client455_entity_lighting.h','client455_entity_lighting.inc','client455_entity_normals.h','client455_lit_grass.inc']}
    report['lighting_port_script']={'file':'scripts/client455_lighting_port.py','sha256':sha(WS/'scripts/client455_lighting_port.py')}
    report['compiled_vertex_shader'] = {
        name: sha(WS / 'scripts/native' / name) for name in (
            'client455_r3_shader_load.inc', 'client455_screen_transition.h', 'client455_screen_transition_draw.inc',
            'client455_filter_blit.h', 'client455_filter_blit_draw.inc')
    }
    report['light_direction']={name:sha(WS/'scripts/native'/name) for name in ['client455_light_direction.h','client455_light_direction.inc']}
    report['map_entity_owner']={'file':'scripts/native/client455_map_entity_owner.inc','sha256':sha(WS/'scripts/native/client455_map_entity_owner.inc')}
    report['material_header_overlay']={'file':materialKey,'sha256':sha(materialHeader),'original':materialInput.relative_to(WS).as_posix(),'original_sha256':sha(materialInput)}
    report['material_port_script']={'file':'scripts/client455_material_port.py','sha256':sha(WS/'scripts/client455_material_port.py')}
    report['binary_material_inputs']={name:sha(WS/'scripts/native'/name) for name in ['client455_r3m_stream.inc','client455_weather_format.h']}
    report['text_material_inputs']={name:sha(WS/'scripts/native'/name) for name in
                                    ['client455_resource_text.h','client455_resource_io.h','client455_resource_bytes.cpp']}
    report['mst_texture_registry']={path:sha(WS/path) for path in
                                    ['scripts/client455_mst_texture_port.py','scripts/native/client455_mst_texture_registry.inc']}
    report['special_shader_owner']={name:sha(WS/'scripts/native'/name) for name in ['client455_special_shaders.h','client455_special_shaders.inc','client455_special_shader_text.inc','client455_shader_key.h']}
    report['material_shader_draw']={name:sha(WS/'scripts/native'/name) for name in ['client455_material_shaders.h','client455_material_shaders.inc','client455_shader_lights.h','client455_shader_lights.inc']}
    report['material_shader_port_script']={'file':'scripts/client455_material_shader_port.py','sha256':sha(WS/'scripts/client455_material_shader_port.py')}
    report['core_header_overlay']={'file':coreHeader.relative_to(WS).as_posix(),'sha256':sha(coreHeader),'original':coreInput.relative_to(WS).as_posix(),'original_sha256':sha(coreInput)}
    report['sky_header_overlay']={'file':skyHeader.relative_to(WS).as_posix(),'sha256':sha(skyHeader),'original':skyInput.relative_to(WS).as_posix(),'original_sha256':sha(skyInput)}
    report['bsp_header_overlay']={'file':bspHeader.relative_to(WS).as_posix(),'sha256':sha(bspHeader),'original':bspInput.relative_to(WS).as_posix(),'original_sha256':sha(bspInput)}
    report['camera']={name:sha(WS/'scripts/native'/name) for name in ['client455_camera.h','client455_camera_load.inc','client455_camera_play.inc']}
    report['fullscreen_effect']={name:sha(WS/'scripts/native'/name) for name in ['client455_fullscreen_effect.h','client455_fullscreen_motion.inc']}
    report['scene_capture']={name:sha(WS/'scripts/native'/name) for name in ['client455_scene_capture.h','client455_scene_capture.inc','client455_render_texture_lifetime.inc']}
    report['multisampling']=sha(WS/'scripts/native/client455_multisampling.h')
    report['movie_state']={name:sha(WS/'scripts/native'/name) for name in ['client455_movie_state.h','client455_movie_state.inc','client455_clear_frame.inc']}
    report['rvp_runtime']={name:sha(WS/'scripts/native'/name) for name in ['client455_rvp_runtime.h','client455_rvp_engine.inc']}
    report['camera_header_overlay']={'file':ownedHeader.relative_to(WS).as_posix(),'sha256':sha(ownedHeader),'original':cameraHeader.relative_to(WS).as_posix(),'original_sha256':sha(cameraHeader)}
    report['sprite_header_overlay']={'file':spriteHeader.relative_to(WS).as_posix(),'sha256':sha(spriteHeader),'original':spriteInput.relative_to(WS).as_posix(),'original_sha256':sha(spriteInput)}
    report['particle_headers']=particleHeaders
    report['particle_header_overlay']={'file':ownedParticleHeader.relative_to(WS).as_posix(),'sha256':sha(ownedParticleHeader),'extra_consumer':'scripts/native/client455_weather.cpp'}
    report['particle_port']={'script':{'file':'scripts/client455_particle_port.py','sha256':sha(WS/'scripts/client455_particle_port.py')},
                             'inputs':{name:sha(WS/'scripts/native'/name) for name in
                                       ['client455_particle_fields.inc','client455_shader_lights.h','client455_shader_lights.inc']}}
    report['immediate_sound']={name:sha(WS/'scripts/native'/name) for name in ['client455_sound_im.h','client455_sound_im.inc']}
    report['wave_manifest']={name:sha(WS/'scripts/native'/name) for name in
        ['client455_resource_text.h','client455_wave_manifest.inc']}
    report['wave_cache_port']={'file':'scripts/client455_wave_cache_port.py','sha256':sha(WS/'scripts/client455_wave_cache_port.py')}
    report['ext_dummy_input']={name:sha(WS/'scripts/native'/name) for name in
                              ['client455_ext_dummy_load.inc','client455_resource_text.h']}
    (WS/'inventory/client455-startup-engine-build.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {len(objects)} engine objects; base source/library preserved; startup and lobby renderer built')
if __name__=='__main__':main()
