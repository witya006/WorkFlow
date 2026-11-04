"""Pin ANI/dispatcher bodies andfreeze selected companion animations,notallassets."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from ani455 import decode

FUNCTIONS=[('animation_ctor',0x932380,0x2b),('animation_dtor',0x932690,0x72),('read_raw_ani',0x93acd0,0x145),('find_max',0x93ae20,0xfb),('load_animation',0x932400,0x77),('attach_track',0x93c050,0x194),('attach_raw',0x93c1f0,0xf6),('dispatchA',0x9352a0,0x7e),('dispatchB',0x935320,0x7e),('suffix',0x9351a0,0x30),('load_character',0x9238a0,0x195),('validate_faces',0x91f150,0x5e),('mesh08_gate',0x91f250,0x4c),('match_animation',0x9316c0,0x64),('factory_reference',0x933280,0xd0),('unsafe_direct_free_wrapper_reference',0x931310,0x2f)]
def sha(b):return hashlib.sha256(b).hexdigest()
def synthetic():
    def track(name,enabled,maximum,counts):
        h=bytearray(140);h[:len(name)]=name;struct.pack_into('<HH',h,100,enabled,maximum)
        return h+b''.join(struct.pack('<H',count)+bytes((i+count*7)&255 for i in range(count*stride)) for count,stride in zip(counts,(20,16,16,8)))
    return [('channels',bytes([3,0xa5])+track(b'A',1,40,(2,1,0,2))+track(b'B',0,200,(1,0,1,0))+track(b'absent',1,65535,(0,0,0,0))),('duplicate',bytes([2,0])+track(b'A',1,4,(1,0,0,0))+track(b'A',1,8,(3,1,1,1))),('empty',bytes(2)),('onebyte',bytes(1)),('empty_high',bytes([0,255])+b'TRAIL')]

def main():
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));previous=None;refs=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Pinned455changed')
        f=[{'name':name,'rva':hex(va-0x400000),'bytes':size,'sha256':sha(read_va(raw,va,size))} for name,va,size in FUNCTIONS]
        if previous is not None and previous!=f:raise ValueError('Animation bodies differbetweenpins')
        previous=f
        if read_va(raw,0x935290,1)!=b'\xc3' or read_va(raw,0x91c260,1)!=b'\xc3':raise ValueError('Observed no-op helperchanged')
        if read_va(raw,0xb3ae7c,4)!=b'ANI\0':raise ValueError('ANI dispatchliteralchanged')
        refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':f})
    pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));client=Path(paths['client_455']);root=WS/'work/client-reference/character-animation455';root.mkdir(parents=True,exist_ok=True);files=[]
    for index,sample in enumerate(pairs['samples']):
        if index==0:continue # Shield hasno companion motion chosen inthisfixture set.
        original=Path(sample['skeleton_original']);folder=client/original.parent.parent/'Ani';candidates=sorted(folder.glob(original.stem+'_*.ANI'))
        if len(candidates)<2:raise ValueError('Needtwo actual companion animations:'+str(folder/original.stem))
        for source in candidates[:2]:
            target=root/f'sample_{len(files):03}.ani';raw=source.read_bytes();target.write_bytes(raw);files.append((target,raw,'real',source.relative_to(client).as_posix(),index))
    for label,raw in synthetic():
        target=root/(label+'.ani');target.write_bytes(raw);files.append((target,raw,'synthetic',None,None))
    golden=bytearray(b'AN45'+struct.pack('<II',1,len(files)));samples=[];total=0
    def string(b):golden.extend(struct.pack('<H',len(b)));golden.extend(b)
    for path,raw,kind,original,pair in files:
        value=decode(raw)
        if value.encode()!=raw:raise ValueError('ANI framing roundtrip mismatch')
        string(path.relative_to(WS).as_posix().encode('ascii'));golden+=struct.pack('<IIIII',len(raw),len(value.tracks),value.maximum,value.consumed,0xffffffff if pair is None else pair)
        for t in value.tracks:
            golden+=struct.pack('<I',t.offset)+t.header
            for count,offset,keys in zip(t.counts,t.key_offsets,t.keys):golden+=struct.pack('<II',count,offset)+keys
        samples.append({'copy':path.relative_to(WS).as_posix(),'sha256':sha(raw),'kind':kind,'original':original,'pair_index':pair,'bytes':len(raw),'tracks':len(value.tracks),'max_frame':value.maximum,'consumed':value.consumed,'trailing':len(value.trailing),'channel_keys':[sum(t.counts[i] for t in value.tracks) for i in range(4)],'inactive':sum(not t.enabled for t in value.tracks)});total+=len(value.tracks)
    target=root/'golden.bin';target.write_bytes(golden)
    report={'scope':'ANI rawIO/framing/record/lifetime/attachment andvalid character dispatch;full pose math/animationmanager/privateABI/normal consumers remainopen','references':refs,'samples':samples,'total_tracks':total,'golden':target.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'script_sha256':sha(Path(__file__).read_bytes()),'framing_script_sha256':sha((WS/'scripts/ani455.py').read_bytes()),'confirmed':['284byte ctorwrites only0/4/5/264/268/272/276/280;rawowner268,descriptorcookie272,extra280;dtorfree/null inthatorder,retainsflags/max/name/id','93ACD0 rawANI hasno formatparse;RFSaccountinguses_msize,looseaccountingfilesize,DWORDcumulative1189608 neverdecremented','Firstcount BYTE0 only,byte1ignored,tracksstart2;header140 +WORDcounts/20,16,16,8;maxheader102 includesdisabled/unmatchedtracks','AnimationData32 contains4DWORDcount/pointerpairs;viewsborrowkeys;current5095/previous5099 copies ownonlydescriptors','Exactfirstmatching meshname;activeheader100 updates5094/current/5103 andretainsoldcurrentasprevious;inactive freescurrent only;model676onlygrows','Loading4 ofANI and264ofmodel stays1 onmostfailures;retry short-circuits true evenifloaded0;externalparent prerequisite beforeflagwrite','Object MESH08route onlyexternalparent branch;legacyvalidationfailure clearsloading onlyinparentbranch andleaksraw there;unparentedMESH08 stillentersoldparser','Unsafe931310 wrapperfreeRaw afterattach leavesborrowedkeydangling;referenceonly,not normal successfulowner route'],
        'limits':['Strictbounded counts/format/type/allocator/pointer policies differfromunchecked AV/OOM/partialparse/exception/unwind domains','Own tagged union rejectspreexistingANI-as-ObjectData28 andMSH-as-ANI reinterpretation ofuninitialized memory;no successstub','Maxvalidator usesallocationextent asreference,butboundedbeforeeveryread;allocatorpadding/uninitialized invalidinputdomains open','Logicalsourcecontexts and284storage notfull C++/STL/animationmanager ABI;full pose evaluator/key semantics deferred','Selectedbasename companions arefixtures,notproof ofruntime assetselection;deprecateddirectfreewrapper notported as safeowner'],
        'raw_analysis':'artifacts/character-animation455;owned45964631closed/save;no referenceEXE run'}
    (WS/'inventory/client455-animation-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{len(FUNCTIONS)}pinnedbodies;{len(files)}ANI fixtures/{total}tracks/roundtrip')
if __name__=='__main__':main()
