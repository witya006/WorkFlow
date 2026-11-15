"""Own byte-preserving header/source overlays for the455 particle dependency."""
import hashlib
import re
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
            body=replace_once(body,b'\tCParticle();',b'\tCParticle();\n\tbool CopyTemplate455(const CParticle& source); // Empty destination; owned curve copy.')
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
    raw=(b'#include "client455_shader_lights.h"\n#include "client455_resource_io.h"\n'
         b'#include "client455_resource_text.h"\n#include <memory>\n'+raw)
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
    token=b'BOOL GetRandOrNum(';start,end=section(raw,token,token)
    helper=b'''BOOL GetRandOrNum(FILE* fp,float* from,float* at) {
    bool valid=true;
    const BOOL random=RF455_GetRandOrNum(fp,from,at,valid);
    if(!valid)Warning("Invalid455 particle random argument", "");
    return random;
}
'''
    raw=raw[:start]+(WS/'scripts/native/client455_particle_fields.inc').read_bytes()+b'\n'+helper+raw[end:]
    token=b'BOOL CParticle::LoadParticleSPT(';start,end=section(raw,token,token);body=raw[start:end]
    first=body.index(b'\tFILE *fp;')
    last=body.index(b'\tchar hole[256];',first)
    opening=body[first:last]
    warnings=re.findall(rb'Warning\(name,[^\r\n]+?\);',opening)
    if len(warnings)!=1 or b'RF455_OpenResource(name,"rt")' not in opening:
        raise ValueError('Particle resource open boundary changed')
    body=body[:first]+b'''    float temp_f;
    RF455ResourceText input;
    std::uint64_t archiveBytes = 0;
    auto* stream = RF455_OpenResourceTextStream455(name, archiveBytes);
    if (!input.openStream(stream, archiveBytes)) {
        '''+warnings[0]+b'''
        return FALSE;
    }
'''+body[last:]
    # Preserve EOF as an ordinary terminator; oversized tokens and read errors fail.
    scan=b'if( fscanf(fp,"%s",hole)==EOF)\t\n\t\t\tbreak;'
    if body.count(scan)!=2:raise ValueError('Particle outer token boundaries changed')
    body=body.replace(scan,b'const int tokenResult455=particleRawToken455(input,hole);\n        if(tokenResult455==EOF)break;\n        if(tokenResult455!=1)return failInput455();')
    end_check=(b'#if defined(RF_CLIENT_455_RESOURCE_IO)\n'
               b'        if (RF455_ParticleScriptEnd(hole)) break;\n#endif')
    if body.count(end_check)!=2:raise ValueError('Particle end-token boundaries changed')
    body=body.replace(end_check,b'        if (RF455_ParticleScriptEnd(hole)) break;')
    body=body.replace(b'fscanf(fp,"%s",hole);',b'if(!particleToken455(input,hole))return failInput455();')
    body=replace_once(body,b'strcpy(mEntityName,hole);',b'if(strlen(hole)>=sizeof(mEntityName))return failInput455();\n            strcpy(mEntityName,hole);')
    track=b'mTimeTrack[mTrackCnt] = (float)atof(hole);'
    body=replace_once(body,track,b'if(mTrackCnt>=_PATICLE_MAX_TRACK)return failInput455();\n            '+track)
    body=re.sub(rb'GetRandOrNum\(fp,([^\n;]*?)\)',rb'RF455_GetRandOrNum(input,\1,particleInputOk455)',body)
    body=replace_once(body,b'!strcmp(hole,"sphere")',b'!strcmp(hole,"sphere_xz")')
    body=replace_once(body,b'!strcmp(hole,"sphere_edge")',b'!strcmp(hole,"sphere_xy")')
    body=replace_once(body,b'\t\tif( !strcmp(hole,"z_front"))',b'\t\tif(!strcmp(hole,"entity_ani"))mFlag|=_PARTICLE_ATTR_ENTITY_ANI;\r\n\t\tif( !strcmp(hole,"z_front"))')
    at=body.rindex(b'\t}\n\tfclose(fp);')
    advanced=b'''        if(!particleInputOk455)return failInput455();
        if(!RF455_ReadParticleFields(*this,input,hole)) {
            ReleaseEntity();ReleaseParticle();
            Warning(name,"<-Invalid455 advanced particle fields");return FALSE;
        }
        if(!strcmp(hole,"[light]")) {
            std::unique_ptr<RF455ShaderLight> nextLight455(RF455_ReadShaderLight(input));
            if(!nextLight455) {
                ReleaseEntity();ReleaseParticle();
                Warning(name,"<-Invalid455 particle light");return FALSE;
            }
            light455.swap(nextLight455); // Last valid block wins; release previous block.
            mFlag|=0x100000u;
        }
'''.replace(b'\n',b'\r\n')
    body=body[:at]+advanced+body[at:]
    at=body.index(b'{')+1;body=body[:at]+b'\n    std::unique_ptr<RF455ShaderLight> light455;\n    bool particleInputOk455=true;'+body[at:]
    body=replace_once(body,b'\tchar hole[256];',b'''    const auto failInput455=[&]() -> BOOL {
        ReleaseEntity();ReleaseParticle();
        Warning(name,"<-Invalid455 particle input");return FALSE;
    };
\tchar hole[256];''')
    end_anchor=b'\tfclose(fp);\n\n\treturn TRUE;'
    body=replace_once(body,end_anchor,b'''    if(light455) {
        mLightID=RF455_AppendShaderLight(light455.get());
        if(mLightID>=0)light455.release();
        // Full registry preserves legacy successful parse and ID -1/flag.
    }
\treturn TRUE;''')
    body,closes=re.subn(rb'(?m)^[ \t]*fclose\(fp\);\n',b'',body)
    if closes!=2:raise ValueError('Particle resource close boundaries changed')
    raw=raw[:start]+body+raw[end:]
    return raw+b'\n'+(WS/'scripts/native/client455_shader_lights.inc').read_bytes()

def entity_source(raw):
    from prepare_client455_normal import section
    token=b'CEntity::CEntity()';start,end=section(raw,token,token);body=raw[start:end]
    body=body[:-1]+b'\r\n\tmObject=NULL; //455+152\r\n}';raw=raw[:start]+body+raw[end:]
    return replace_once(raw,b'\tmMatGroupNum=(int)(mHeader.MatGroup.size/sizeof(_READ_ENTITY_M_GROUP));',b'\tmVertexCount=static_vertexnum; //4558E0FDE\r\n\tmMatGroupNum=(int)(mHeader.MatGroup.size/sizeof(_READ_ENTITY_M_GROUP));')
