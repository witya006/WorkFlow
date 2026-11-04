"""Pin the full legacy converter and its geometry/IO contracts for source recovery."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from audit_character_init455 import legacy_extent

FUNCTIONS=[('vertex64',0x93b020,0x31),('uv64',0x93b5f0,0x17),('weights64',0x93aa10,0x2c0),
           ('convert36',0x93b130,0x1c4),('dedup_upload',0x93b310,0x2db),
           ('legacy_bones',0x93bc40,0x1f6),('strip_extension',0x93a9d0,0x33),
           ('legacy_converter',0x93cd60,0x1083),('file_importer',0x93c770,0x123)]
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];previous=None;wide=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed pinned455')
        functions=[{'name':name,'rva':hex(va-0x400000),'bytes':size,'sha256':sha(read_va(raw,va,size))} for name,va,size in FUNCTIONS]
        if previous is not None and previous!=functions:raise ValueError('Converter bodies differ between pins')
        previous=functions
        if read_va(raw,0xb3b1c0,5)!=b'.mtg\0':raise ValueError('MTG extension changed')
        words=[]
        for i in range(128):
            word=struct.unpack('<H',read_va(raw,0xb3b118+2*i,2))[0];words.append(word)
            if not word:break
        else:raise ValueError('Unterminated debug W-data')
        if wide is not None and wide!=words:raise ValueError('Wide debug data differs')
        wide=words;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':functions})
    if struct.pack('<'+'H'*len(wide),*wide)!="Error: Can't Find Parent!!\n\0".encode('utf-16le'):raise ValueError('Missing-bone literal changed')
    root=WS/'work/client-reference/character-legacy-runtime';root.mkdir(parents=True,exist_ok=True);debug=root/'missing-bone-utf16.bin';debug.write_bytes(struct.pack('<'+'H'*len(wide),*wide))
    source=json.loads((WS/'inventory/character-init-reference.json').read_text(encoding='utf-8'));samples=[]
    for item in source['samples']:
        path=WS/item['copy'];raw=path.read_bytes()
        if sha(raw)!=item['sha256']:raise ValueError('Pinned model changed')
        extent=legacy_extent(raw)
        if extent['accepted']:samples.append({'copy':item['copy'],'sha256':sha(raw),'original_relative':item['original_relative'],'records':extent['mesh_count'],'vertices':sum(p['vertices'] for p in extent['records']),'faces':sum(p['faces'] for p in extent['records']),'physiques':sum(p['physiques'] for p in extent['records'])})
    report={'scope':'Full source legacy converter/IO/geometry contracts;runtime/normal integration tracked separately','references':references,'real_legacy_meshes':samples,'missing_bone_wide':{'rva':'0x73b118','words':wide,'file':debug.relative_to(WS).as_posix(),'sha256':sha(debug.read_bytes())},'confirmed':['MTG derived from model.name4 by stripping final dot suffix,then .mtg,loose fopen only;84bytes perface,three x87copied floats per28byte corner tovertex52/56/60','Header counts5086/5090=3faces beforematrix;normal conversion initializesweights/indices butpreserves persistent scratchUV/tangent tail','93B130 converts64→36 withDWORDcopies exceptweight12 whichusesx87;bothunrolledandscalar remainder verified','64byte memcmp firstmatch dedup;mode4VB64/mode2VB36;mode2conversionloops expandedCount butuploads uniqueCount;indexbase fromabsolute%2300000/stride,WORDwrap,IBupload evenafterVBfailure','Mode2+physique+firstinfluenceCount>2 retainsCPUexpandedarray4506,skipsindexupload;othermodesindexed','Parents local thenexternal;last import compactflag24 gates4702=4574*parent4638;legacy424physique distinctfromMESH08resolver','Legacybone resolver writesidentitymatrices beforeinlinepointercopy,includingknown31+overlap;missingbones callOutputDebugStringW(addressB3B118)','FileimporterRFS→loose→parser→rawfree→unconditionalImportMeshorBoneData(...):NULL log,evenparse success'],
        'limits':['Full source logger/OutputDebugString owner wiring still needed;adapter receives exact literal text/API kind','Bounded index/count/name/nullallocation/MTGshortread errors differfromunchecked reference/AV/debugbreak/OOM/unwind','Scratch isowned persistent memory corresponding toreference globals;other fullrenderer users andthreading remainopen','Body hash/decompiler text alone doesnotproveequivalence;scoped instruction evidence captured inartifacts/character-converter455'],
        'raw_analysis':'artifacts/character-converter455;owned0d9553e1/08d81b2fclosed/save;no referenceEXE run'}
    (WS/'inventory/client455-legacy-runtime-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:9pinnedconverter/IO/geometry bodies;legacy realmeshes='+str(len(samples))+';W-debug words='+str(wide))
if __name__=='__main__':main()
