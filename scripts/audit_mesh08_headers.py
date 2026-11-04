"""Audit new header/material domains using frozen offsets;prepare CPU-state golden.

Does not repeat the full framing/roundtrip census. Original model bytes are only
read and checked against that census;native expected states remain ignored assets.
"""
import collections,hashlib,json,math,ntpath,struct
from pathlib import Path
from compare_client_binaries import WS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def field(head,at):
    raw=head[at:at+100]
    if b'\0' not in raw:raise ValueError('Unterminated header fixture field')
    return raw.split(b'\0',1)[0]
def base_state():
    state=bytearray(5803)
    for at in [5131,5483,5487,5491]:struct.pack_into('<I',state,at,0x3f800000)
    for at in [5111,5123,5127,4494,4502,5767,5771,5775,5763]:struct.pack_into('<I',state,at,0xffffffff)
    return state
def header_state(head,part,modelFlag):
    result=base_state()
    def put(at,x):struct.pack_into('<I',result,at,x)
    put(5363,1);result[5339:5343]=struct.pack('<f',struct.unpack_from('<I',head,598)[0])
    result[5471:5483]=head[614:626];result[5459:5471]=head[602:614]
    put(5359,head[634]);put(5143,head[639]);result[5579:5595]=head[646:662]
    for destination,source in [(4766,328),(4574,200),(4510,200),(4702,264)]:result[destination:destination+64]=head[source:source+64]
    name=ntpath.basename(field(head,0));parentName=ntpath.basename(field(head,100))
    if any(x>=128 for x in name+parentName):raise ValueError('Non-ASCII golden names need locale validation')
    result[:len(name)]=name;result[256:256+len(parentName)]=parentName
    special=[b'Bip01 Spine1',b'Bip01 L Thigh',b'Bip01 R Thigh']
    if name in special:put(5575,special.index(name)+1)
    if name in [b'Bip01 Ponytail L1',b'Bip01 Ponytail L11',b'Bip01 L skirt',b'Bip01 R skirt',b'Bip01 B skirt']:put(5571,1);modelFlag=1
    put(5086,part['vertex_count']);put(5090,part['index_count'])
    # Runtime self pointer and two computed matrices are checked separately.
    return result,modelFlag
def main():
    summary=json.loads((WS/'inventory/character-mesh08-corpus.json').read_text(encoding='utf-8'))
    if sha(WS/summary['corpus'])!=summary['corpus_sha256']:raise ValueError('Framing corpus changed')
    corpus=json.loads((WS/summary['corpus']).read_text(encoding='utf-8'))
    root=Path(json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))['client_455'])
    counts=collections.Counter();examples=collections.defaultdict(list);headsByDigest={};selected={s['sha256'] for s in summary['samples']}
    def count(key,where):
        counts[key]+=1
        if len(examples[key])<4:examples[key].append(where)
    for record in corpus['records']:
        raw=(root/record['relative']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Reference model changed')
        heads=[]
        for part in record['parts']:
            head=raw[part['offset']:part['offset']+693]
            if len(head)!=693:raise ValueError('Frozen header extent changed')
            heads.append(head);counts['headers']+=1;where=f"{record['relative']}:{part['offset']}"
            values=[]
            for at in [0,100,398,498]:
                try:value=field(head,at)
                except ValueError:count('unterminated_strings',where);value=b''
                values.append(value)
                if any(x>=128 for x in value):count('non_ascii_strings',where)
                if b'%' in value:count('percent_strings',where)
            primary,secondary=values[2:]
            if not primary:counts['empty_primary']+=1
            elif b'\\' not in primary:count('nonempty_primary_without_backslash',where)
            if secondary.startswith(b'\\') and b'\\' not in secondary[1:]:count('secondary_leading_only_backslash',where)
            if primary and b'.dds' not in primary.rsplit(b'\\',1)[-1].lower():count('non_dds_primary_basename',where)
            for at in [200,264,328]:
                m=struct.unpack_from('<16f',head,at)
                if not all(map(math.isfinite,m)):count('nonfinite_matrix',where);continue
                if (m[3],m[7],m[11],m[15])!=(0,0,0,1):count('nonaffine_matrix',where)
                det=m[0]*(m[5]*m[10]-m[6]*m[9])-m[1]*(m[4]*m[10]-m[6]*m[8])+m[2]*(m[4]*m[9]-m[5]*m[8])
                if not det:count('zero_numeric_3x3_determinant',where)
            if not all(map(math.isfinite,struct.unpack_from('<6f',head,602))):count('nonfinite_metadata_floats',where)
        if record['sha256'] in selected:headsByDigest[record['sha256']]=(record,heads)
    folder=WS/'work/client-reference/character-models/mesh08-header';folder.mkdir(parents=True,exist_ok=True)
    golden=bytearray(b'M8HR'+struct.pack('<II',2,len(summary['samples'])))+base_state()
    for sample in summary['samples']:
        record,heads=headsByDigest[sample['sha256']];name=sample['copy'].encode('ascii');golden+=struct.pack('<H',len(name))+name+struct.pack('<I',len(heads));flag=0
        for head,part in zip(heads,record['parts']):
            state,flag=header_state(head,part,flag);golden+=struct.pack('<I',flag)+state
    output=folder/'golden.bin';output.write_bytes(golden)
    report={'scope':'New693-byte header/material domain audit on858frozen loose MESH08files;not a new framing census or complete runtime loader','files':len(corpus['records']),'counts':dict(counts),'examples':dict(examples),'golden':output.relative_to(WS).as_posix(),'golden_sha256':sha(output),'script_sha256':sha(Path(__file__)),'corpus_report_sha256':sha(WS/'inventory/character-mesh08-corpus.json'),'samples':summary['samples'],'masked_ranges':[[4638,64],[5022,64]],'self_pointer_offset':5455,'limits':['Matrix audit uses binary64 numeric3x3determinants andexact affine columns;not full singular/condition classification','Golden covers constructor/header scalar/copy fields;derived D3DX9 matrices validated by native algebraic invariants andexplicit synthetic outcomes','Materials backend/texture uploads/full skeleton/animation/sharedGPU/model dispatch remain open']}
    (WS/'inventory/character-mesh08-headers.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':report['files'],'counts':report['counts'],'golden_bytes':len(golden)}))
if __name__=='__main__':main()
