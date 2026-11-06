"""Pin455camera loader/playback and independently walk real1.2/1.3files."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()
def camera_layout(raw):
    at=0;parts=[]
    def take(n):
        nonlocal at
        if n<0 or at+n>len(raw):raise ValueError('Truncated camera')
        part=raw[at:at+n];at+=n;parts.append(part);return part
    def word():return struct.unpack('<I',take(4))[0]
    def node():
        take(64+12+16);pos,rot=word(),word();take(pos*16);take(rot*20);return {'position_keys':pos,'rotation_keys':rot}
    version=struct.unpack('<f',take(4))[0];count=word();rows=[];dummies=[];start=end=0
    if version<1.2:raise ValueError('Unsupported camera version')
    if count:
        start,end=word(),word()
        for _ in range(count):
            name=take(64).split(b'\0',1)[0].decode('ascii');fov,distance=struct.unpack('<ff',take(8));num=word();fovs=word() if version>=struct.unpack('<f',struct.pack('<f',1.3))[0] else 0;take(fovs*20)
            rows.append({'name':name,'fov':fov,'distance':distance,'fov_keys':fovs,'hierarchy':[node() for _ in range(num)]})
        for _ in range(word()):
            name=take(64).split(b'\0',1)[0].decode('ascii');parent=take(64).split(b'\0',1)[0].decode('ascii');dummies.append({'name':name,'parent':parent,**node()})
    trailer=take(len(raw)-at)
    if b''.join(parts)!=raw:raise ValueError('Camera wire roundtrip mismatch')
    return {'version':version,'camera_count':count,'start':start,'end':end,'cameras':rows,'dummies':dummies,'trailer_bytes':len(trailer),'roundtrip_equal':True}
def main():
    evidence=WS/'artifacts/client455-camera/reference.json';raw_evidence=json.loads(evidence.read_text());pins=json.loads((WS/'config/client-target.json').read_text());references=[];previous=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        ranges=[{'rva':hex(int(row['fn']['addr'],16)-0x400000),'bytes':int(row['fn']['size'],16),'sha256':sha(read_va(raw,int(row['fn']['addr'],16),int(row['fn']['size'],16)))} for row in raw_evidence['ranges']['result']]
        if previous is not None and previous!=ranges:raise ValueError('455camera ranges differ')
        previous=ranges;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':ranges})
    root=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for name in ['bellato','cora','accretia','lobby']:
        path=root/f'Map/{name}/{name}.cam';data=path.read_bytes();inputs.append({'file':str(path),'relative':f'Map/{name}/{name}.cam','sha256':sha(data),'bytes':len(data),'layout':camera_layout(data)})
    report={'scope':'455camera1.2/1.3wire loading and playback state;not fullTutorial/world/camera matrix parity','references':references,'raw_evidence':{'file':evidence.relative_to(WS).as_posix(),'sha256':sha(evidence.read_bytes())},'script_sha256':sha(Path(__file__).read_bytes()),'inputs':inputs,
        'facts':['Camera owner56bytes;target privatecamera records88=Name64/hierarchyCount/fov/distance/FovCount/FovPtr/NodePtr','Version>=1.2;FOV count/20bytekeys presentwhen version>=float1.3;node349serializedmatrix64/pos12/quat16/counts/tracks16and20','Dummy header name64/parent64 followedbysame node payload;zeroCamera file doesnotreadotherheaders;trailerignoredbytarget','Initial matrix FOV is storedFov*float0.788;separateFOV updater interpolates keyvalue0 at nowSeconds*30;beforefirst/notbracketed selects lastkey','Play:forward terminal>=end/30;flag0 resets time but uses float(startFrame) seconds;reverse terminal<=0 ratherthan end/30;allterminal cases returnfalse','Paused play doesnotreadclock unless flag0 terminal resets it;clockmaybereadtwice onordinary loop restart','Tutorial scene/race usesbellato/cora/accretia BSPandCAM;normalLogin useslobbyCAM'],
        'gaps':['FullTutorial/4stage/Avatar/world/UI/camera-cut sequencing remainopen','Source camera private80bytelegacy record retainedasownedtype;additional FOVdocument registry stores455metadata without mixedheaders/raw original overlays','Separate FOV API is source andtested;actualR3Move8D5FF0 updater callsite stillrequiresport','Legacyengine matrix interpolation/matrix numericdomains anddummy hierarchy unsafe cycles notfullycertified','Malformedload nowatomic/preservesold owner;target mayreleasefirst/overread/partiallymutate;OOM/concurrency/CRTerror domains notcertified','Target destructor empty;explicitRelease required;smallregistrycontainer deliberatelysurvivesCRT teardown;documents erasedonRelease','Whole455runtime/authentication/M6F/M9 remainopen'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    report['gaps'][2]='Separate FOV API is source andtested;actualengine camera consumer8D5FF0 updater callsite stillrequiresport'
    report['actual_selected_files_version']='1.2;1.3 is verified on a syntheticfixture;do notclaim real1.3coverage'
    report['playback_asm']={'file':'artifacts/client455-camera/playback-branches.json','sha256':sha((WS/'artifacts/client455-camera/playback-branches.json').read_bytes())}
    (WS/'inventory/client455-camera-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps([{'relative':r['relative'],'version':r['layout']['version'],'cameras':r['layout']['camera_count'],'fov_keys':sum(c['fov_keys'] for c in r['layout']['cameras']),'bytes':r['bytes']} for r in inputs]))
if __name__=='__main__':main()
