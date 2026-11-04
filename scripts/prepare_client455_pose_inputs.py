"""Freeze selected existing ANI key expectations and connected model paths."""
import hashlib,json,struct
from compare_client_binaries import WS
from ani455 import decode,STRIDES

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def signed(v):return (v+2**31)%2**32-2**31
def main():
    source=WS/'inventory/client455-animation-reference.json';ani=json.loads(source.read_text(encoding='utf-8'));pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));cases=[]
    # Pick first track of each animated channel in each file. Framing coverage
    # belongs to the completed ANI tests; this checks new selection/math paths.
    for record in ani['samples']:
        if record['kind']!='real':continue
        path=WS/record['copy']
        if sha(path)!=record['sha256']:raise ValueError('Changed ANI')
        value=decode(path.read_bytes())
        for channel in range(3):
            track=next((t for t in value.tracks if t.enabled and t.counts[channel]>=2),None)
            if track is None:continue
            keys=track.keys[channel];stride=STRIDES[channel];times=[struct.unpack_from('<i',keys,i*stride+stride-4)[0] for i in range(track.counts[channel])]
            for frame in [times[0]-80,(times[0]+times[-1])//2,times[-1]+80]:
                # Independent interval definition for the monotone real fixtures.
                left=max(0,min(len(times)-2,next((i-1 for i,t in enumerate(times) if t>frame),len(times)-2)))
                delta=(times[left+1]-times[left])%2**32;ratio=f32(signed(frame-times[left])/delta) if delta else 0.0
                vectors=[]
                if channel:
                    a=struct.unpack_from('<3f',keys,left*stride);b=struct.unpack_from('<3f',keys,(left+1)*stride)
                    vectors=[f32(x-(x-y)*ratio) for x,y in zip(a,b)]
                cases.append((record['copy'],track.offset,channel,frame,left,ratio,vectors))
    result=bytearray(b'PS45'+struct.pack('<II',1,len(cases)))
    def text(s):
        raw=s.encode('ascii');result.extend(struct.pack('<H',len(raw)));result.extend(raw)
    for path,track,channel,frame,left,ratio,vectors in cases:
        text(path);result+=struct.pack('<IIiIf',track,channel,frame,left,ratio)+struct.pack('<3f',*(vectors or [0,0,0]))
    result+=struct.pack('<I',11)
    for index in range(1,12):
        text(f'work/client-reference/character-legacy-runtime/real_{index:02}.bn');text(pairs['samples'][index]['mesh'])
        samples=[r for r in ani['samples'] if r['pair_index']==index]
        if len(samples)!=2:raise ValueError('Two ANI per pair required')
        for r in samples:text(r['copy'])
    root=WS/'work/client-reference/character-pose455';root.mkdir(parents=True,exist_ok=True);golden=root/'pose.bin';golden.write_bytes(result)
    report={'scope':'Selected key selection/component float32 expectations and11 existing connectedpairs;not all pose reference runtime','golden':golden.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'key_cases':len(cases),'real_pairs':11,'ani_report_sha256':sha(source),'pair_report_sha256':sha(WS/'inventory/character-mesh08-bone-pairs.json'),'pose_reference_sha256':sha(WS/'inventory/client455-pose-reference.json'),'script_sha256':sha(WS/'scripts/prepare_client455_pose_inputs.py'),'limits':['Finite monotone selected real key fixtures,nearest rounding/53bit intermediate expectation;other masked FP modes checked on exact analytic native cases','Quaternion expected call inputs/ratio checked;actual matrix math uses pinned D3DX provider','Connected pose parent/skin identities are structural checks,not independent full binary execution comparison']}
    (WS/'inventory/client455-pose-inputs.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'key_cases':len(cases),'real_pairs':11}))
if __name__=='__main__':main()
