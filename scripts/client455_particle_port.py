"""Own byte-preserving header/source overlays for the455 particle dependency."""
import hashlib
from compare_client_binaries import WS

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def replace_once(raw,old,new):
    if raw.count(old)!=1:raise ValueError('Particle source boundary changed: '+repr(old))
    return raw.replace(old,new)
def headers(base,root,previous):
    old={r['file']:r['sha256'] for r in previous.get('particle_headers',[])};records=[]
    for name in ['entity','r3particle']:
        source=base/'source/R3Engine/1stclass'/(name+'.h');raw=source.read_bytes()
        if name=='entity':
            raw=replace_once(raw,b'\tvoid *mIndependencyTex;',b'\tDWORD mVertexCount; //455+168, expanded vertex count\r\n\tvoid *mIndependencyTex;')
            raw+=b'\r\n#include <cstddef>\r\nstatic_assert(sizeof(CEntity)==212 && offsetof(CEntity,mVertexCount)==168 && offsetof(CEntity,mFrame)==208,"455 entity fields");\r\n'
        else:
            at=raw.index(b'class CParticle{');prefix,body=raw[:at],raw[at:]
            body=replace_once(body,b'\tfloat mLiveTime;',b'\tfloat mElapsedTime; //455+140\r\n\tfloat mLiveTime;')
            extra=b'''\tBYTE mTraceLength,mCurvePad[3]; //455+336
\tVector3f* mCurvePoints;
\tfloat mCurveSpeed,mCurveRadius;
\tBYTE mCurveKnotNum,mCurveRepeatNum,mCurvePad2[2];
\tfloat mCurveRotation,mCurveMatrix[4][4];
\tfloat mAzirangPos[4];
\tDWORD mAzirangWidth,mAzirangHeight;
\tfloat mAzirangAmplitude,mAzirangVariance,mAzirangTime;
\tfloat mDistort,mDistortOffset[2];
'''.replace(b'\n',b'\r\n')
            body=replace_once(body,b'\tWORD mSpecialID;',extra+b'\tWORD mSpecialID;')
            body=replace_once(body,b'private:\n\tBOOL mState;',b'public:\n\tBYTE mUseCombineScale,mCombinePad[3];\nprivate:\n\tBOOL mState;')
            line=next(line for line in body.splitlines(keepends=True) if b'float mNextCreatorTime;' in line)
            body=replace_once(body,line,line+b'public:\r\n\tint mLightID; //455+1292\r\nprivate:\r\n')
            raw=prefix+body+b'\r\n#include <cstddef>\r\nstatic_assert(sizeof(CParticle)==1296 && offsetof(CParticle,mElapsedTime)==140 && offsetof(CParticle,mLiveTime)==144 && offsetof(CParticle,mCurvePoints)==340 && offsetof(CParticle,mSpecialID)==472 && offsetof(CParticle,mFlag)==1224 && offsetof(CParticle,mCreatePos)==1256 && offsetof(CParticle,mUseCombineScale)==1268 && offsetof(CParticle,mLightID)==1292,"455 particle fields");\r\n'
        target=root/'include'/(name+'455.h');target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=raw and sha(target)!=old.get(target.relative_to(WS).as_posix()):raise ValueError('Preserving changed owned particle declaration')
        if not target.exists() or target.read_bytes()!=raw:target.write_bytes(raw)
        records.append(dict(file=target.relative_to(WS).as_posix(),sha256=sha(target),original=source.relative_to(WS).as_posix(),original_sha256=sha(source)))
    return records

def particle_source(raw):
    raw=b'#include "client455_shader_lights.h"\n'+raw
    from prepare_client455_normal import section
    for token,new in [
        (b'CParticle::~CParticle()',b'CParticle::~CParticle(){if(mCurvePoints)Dfree(mCurvePoints);if(mElement)Dfree(mElement);mElement=NULL;mCurvePoints=NULL;}'),
        (b'void CParticle::ReleaseParticle()',b'void CParticle::ReleaseParticle(){if(mCurvePoints)Dfree(mCurvePoints);mCurvePoints=NULL;if(mElement)Dfree(mElement);mNum=0;mElement=NULL;}'),
        (b'void CParticle::ReleaseEntity()',b'void CParticle::ReleaseEntity(){if(mEntity){mEntity->ReleaseEntity();delete mEntity;mEntity=NULL;}}')]:
        start,end=section(raw,token,token);raw=raw[:start]+new+raw[end:]
    token=b'CParticle::CParticle()';start,end=section(raw,token,token);body=raw[start:end];at=body.index(b'{')+1
    #The original body already zeroes sizeof(CParticle). Add the final455ID write.
    body=body[:-1]+b'\r\n\tmLightID=-1;\r\n}';raw=raw[:start]+body+raw[end:]
    token=b'LONG CParticle::Loop()';start,end=section(raw,token,token);body=raw[start:end];at=body.index(b'{')+1
    body=body[:at]+b'\r\n\tmElapsedTime=float(double(mElapsedTime)+R3GetLoopTime());'+body[at:];raw=raw[:start]+body+raw[end:]
    token=b'BOOL CParticle::LoadParticleSPT(';start,end=section(raw,token,token);body=raw[start:end]
    body=replace_once(body,b'!strcmp(hole,"sphere")',b'!strcmp(hole,"sphere_xz")')
    body=replace_once(body,b'!strcmp(hole,"sphere_edge")',b'!strcmp(hole,"sphere_xy")')
    body=replace_once(body,b'\t\tif( !strcmp(hole,"z_front"))',b'\t\tif(!strcmp(hole,"entity_ani"))mFlag|=_PARTICLE_ATTR_ENTITY_ANI;\r\n\t\tif( !strcmp(hole,"z_front"))')
    at=body.rindex(b'\t}\n\tfclose(fp);')
    reject=b'''        //Required455 advanced providers remain explicit,not silently ignored.
        if(!strcmp(hole,"tracelength")||!strcmp(hole,"control_node")||
           !strcmp(hole,"distort")||!strcmp(hole,"distort_offset")||
           !strcmp(hole,"azirang_pos")||!strcmp(hole,"azirang_width")||
           !strcmp(hole,"azirang_height")||!strcmp(hole,"azirang_amplitude")||
           !strcmp(hole,"azirang_time")||!strcmp(hole,"azirang_variance")||
           !strcmp(hole,"use_combine_scale")) {
            fclose(fp);ReleaseEntity();ReleaseParticle();
            Warning(name,"<-455 advanced particle provider remains open");return FALSE;
        }
'''.replace(b'\n',b'\r\n')
    body=body[:at]+reject+b'        if(!strcmp(hole,"[light]")){light455=RF455_ReadShaderLight(fp);mFlag|=0x100000u;}\n'+body[at:]
    at=body.index(b'{')+1;body=body[:at]+b'\n    RF455ShaderLight* light455=nullptr;'+body[at:]
    end_anchor=b'\tfclose(fp);\n\n\treturn TRUE;'
    body=replace_once(body,end_anchor,b'    if(light455)mLightID=RF455_AppendShaderLight(light455);\n'+end_anchor)
    raw=raw[:start]+body+raw[end:]
    return raw+b'\n'+(WS/'scripts/native/client455_shader_lights.inc').read_bytes()

def entity_source(raw):
    from prepare_client455_normal import section
    token=b'CEntity::CEntity()';start,end=section(raw,token,token);body=raw[start:end]
    body=body[:-1]+b'\r\n\tmObject=NULL; //455+152\r\n}';raw=raw[:start]+body+raw[end:]
    return replace_once(raw,b'\tmMatGroupNum=(int)(mHeader.MatGroup.size/sizeof(_READ_ENTITY_M_GROUP));',b'\tmVertexCount=static_vertexnum; //4558E0FDE\r\n\tmMatGroupNum=(int)(mHeader.MatGroup.size/sizeof(_READ_ENTITY_M_GROUP));')
