"""Pin downstream ANI evaluators and record selected real-key shape evidence."""
import collections,hashlib,json,math,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from ani455 import decode,STRIDES

FUNCTIONS=[('frame_move',0x923a40,0xcb2),('key_scale',0x91de80,0x103),('key_rotation',0x91df90,0x1c7),('key_translation',0x91e160,0x106),('secondary_motion',0x91e270,0x80e),('scale_axis',0x934fc0,0x44),('matrix_multiply',0x934d60,0x15),('profile_begin',0x933430,0x5f),('profile_end',0x933490,0x70)]
def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));refs=[];last=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455 pin')
        f=[{'name':name,'rva':hex(va-0x400000),'bytes':size,'sha256':sha(read_va(raw,va,size))} for name,va,size in FUNCTIONS]
        if last is not None and f!=last:raise ValueError('Pose bodies differ between pins')
        last=f
        if struct.unpack('<f',read_va(raw,0xb369b0,4))[0]!=4294967296.0:raise ValueError('Unsigned x87 conversion constant changed')
        refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':f})
    source=WS/'inventory/client455-animation-reference.json';ani=json.loads(source.read_text(encoding='utf-8'));shapes=[collections.Counter() for _ in range(4)];nonmonotone=[0]*4;nonfinite=[0]*4;one=[];active=0
    for record in ani['samples']:
        if record['kind']!='real':continue
        raw=(WS/record['copy']).read_bytes()
        if sha(raw)!=record['sha256']:raise ValueError('Changed real ANI')
        for track in decode(raw).tracks:
            if not track.enabled:continue
            active+=1
            for channel,(count,keys,stride) in enumerate(zip(track.counts,track.keys,STRIDES)):
                shapes[channel][str(count)]+=1
                times=[struct.unpack_from('<i',keys,i*stride+stride-4)[0] for i in range(count)]
                if any(a>b for a,b in zip(times,times[1:])):nonmonotone[channel]+=1
                if any(not math.isfinite(struct.unpack_from('<f',keys,i*stride+j)[0]) for i in range(count) for j in range(0,stride-4,4)):nonfinite[channel]+=1
                if count==1 and channel<3:
                    start=track.key_offsets[channel];one.append({'copy':record['copy'],'track_offset':track.offset,'channel':channel,'offset':start,'nominal_bytes':stride,'bytes_remaining_in_file':len(raw)-start,'two_keys_fit_file':start+2*stride<=len(raw)})
    report={'scope':'Research only: pinned FrameMove/three key evaluators/secondary motion and selected real key shapes; no pose implementation claim','references':refs,'ani_report_sha256':sha(source.read_bytes()),'active_tracks':active,'channel_order':['quaternion20','translation16','scale16','unused_by_three_evaluators8'],'active_channel_count_histograms':[dict(sorted(c.items(),key=lambda x:int(x[0]))) for c in shapes],'nonmonotone_signed_time_tracks':nonmonotone,'nonfinite_value_tracks':nonfinite,'one_key_channels':one,'confirmed':['Key timestamps use signed DWORD comparisons;delta subtraction wrapsDWORD,then signed numerator/unsigned denominator converted byx87 andratio storedfloat32','Scale key2 useslinear search;quaternion key0 andtranslation key1 usebinary search;before-first/after-last extrapolate withoutclamp','Count1 still readssecond key beyonddeclared channel;do notinvent count1constant behavior;allocation-contained behavior needsseparate evidence','QuaternionSlerp actualfourargument stdcall,D3DXMatrixRotationQuaternion actualtwoargument stdcall;cacheddecompiler haswrongprototype/stackalignment','QuaternionW isFCHS/x87 beforematrixconversion;scale appliesmesh5483vector,translation fallbackmesh4750','FrameMove readsframe672/previous684,doesnotadvancecurrentframe;blend692/global33844 andramp712/716 separate','FrameMove producespose4830 throughparentpose andtwo-phase skinmatrix646=mesh4574*bone4638*bone4830;parent/mesh traversalorder observable','Profilebegin/end933430/933490 aretimingmetrics,notmutexlocks;secondarymotion91E270 usesmodel1184/timeGetTime andspecificpony/skirt names'],'limits':['No source pose implementation yet;nextinspectcount1 actualreadspan andthree math kernels before full FrameMove','Raw decompiler labels pose-rotation.json/pose-position.json/pose-scale.json areinitialprovisionalfilenames;actualroles determinedfrominstructions are scale91DE80/rotation91DF90/translation91E160','No inputEXE execution oranimateddraw proof'],'raw_analysis':'artifacts/character-animation455/framemove-0.json,framemove-1.json,framemove-tail.json,key-*-insn.json,pose-*.json,scale-axis.json;owned66b26ca4closed/save','script_sha256':sha((WS/'scripts/audit_client455_pose.py').read_bytes())}
    (WS/'inventory/client455-pose-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'pinned_bodies':len(FUNCTIONS),'active_tracks':active,'one_key_channels':len(one),'count_histograms':report['active_channel_count_histograms'],'nonmonotone':nonmonotone,'nonfinite':nonfinite}))
if __name__=='__main__':main()
