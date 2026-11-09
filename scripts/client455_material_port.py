"""Seven54-byte runtime layers;preserve46-byte serialized R3M records."""
from prepare_client455_normal import section


def replace(raw,old,new):
    if raw.count(old)!=1:raise ValueError('Material migration boundary '+repr(old))
    return raw.replace(old,new)


def header(raw):
    raw=replace(raw,b'#define _MAX_MATERIALS\t\t1024',b'#define _MAX_MATERIALS\t\t2048')
    raw=replace(raw,b'#define _MAX_LAYER_NUM\t\t4',b'#define _MAX_LAYER_NUM\t\t7')
    raw=replace(raw,b'}_ONE_LAYER;',b'    float m_fSpecularFlickeringScale; //455 runtime+46,not serialized\n    float m_fSpecularFlickeringSpeed; //455 runtime+50,not serialized\n}_ONE_LAYER;')
    return raw+b'\n#include <cstddef>\nstatic_assert(sizeof(_ONE_LAYER)==54 && offsetof(_ONE_LAYER,m_fSpecularFlickeringScale)==46 && offsetof(_ONE_LAYER,m_fSpecularFlickeringSpeed)==50,"455 runtime layer");\nstatic_assert(sizeof(_R3MATERIAL)==526 && offsetof(_R3MATERIAL,m_Layer)==148,"455 runtime material");\n'


def material(raw):
    raw=replace(raw,b'fread(&mat[i].m_Layer[j],sizeof(_ONE_LAYER),1,fp);',b'fread(&mat[i].m_Layer[j],46,1,fp); //455 serialized prefix;runtime tail stays zero')
    start,end=section(raw,b'_R3MATERIAL* LoadIndependenceR3M(',b'_R3MATERIAL* LoadIndependenceR3M(');body=raw[start:end]
    version=body.index(b'if( version != _R3M_VERSION )');failure=body.index(b'return NULL;',version)
    body=body[:failure]+b'fclose(fp); //455 closes the rejected version\n\t\t'+body[failure:];raw=raw[:start]+body+raw[end:]
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
