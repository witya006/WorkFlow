"""Pin Character record/manager/file contracts andproduce constructor byte golden."""
import hashlib,json,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from character_ctor_oracle import interpret
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    functions=[('character_ctor',0x91c510,0x1bc),('material_init',0x91c450,0x3b),('manager_ctor',0x5dfe60,0x6e),('cache_ctor',0x5dfed0,0x29),('cache_find',0x91c7b0,0x8c),('cache_put',0x91c840,0xaa),('key1',0x9321b0,0x39),('key2',0x9321f0,0x42),('lookup_name',0x920a20,0x59),('lookup_id',0x920a80,0x4b),('id_by_name',0x920ad0,0x62),('append_assign_id',0x922840,0x57),('vector_insert',0x921d00,0x1b5),('manager_dtor',0x922240,0x5f),('delete_name',0x921960,0xe7),('delete_id',0x921a50,0xb5),('manager_clear',0x921bc0,0x97),('create_character',0x931360,0x88),('refresh_textures',0x91f0a0,0xa4),('read_raw_msh',0x91f1b0,0x9b),('extension',0x9351a0,0x30),('rfs_blob',0x9383a0,0xe1),('rfs_blob_read',0x9367c0,0x18c),('dispatcher',0x9238a0,0x195)]
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];baseline=None;golden=None
    trace=WS/'inventory/client455-character-constructor-instructions.json'
    if trace.exists():
        instruction_evidence=json.loads(trace.read_text(encoding='utf-8'))
    else:
        captured=WS/'artifacts/character-manager455/record-ctor-insns.json'
        rows=json.loads(captured.read_text(encoding='utf-8'))['result'][0]['matches']
        pin=(WS/'work/client-reference/reference-backup/RF_Online.bin').read_bytes()
        if sha(pin)!=pins['secondary_reference']['sha256']:raise ValueError('Pinned constructor input changed')
        encoded=[]
        for i,row in enumerate(rows):
            va=int(row['addr'],16);end=int(rows[i+1]['addr'],16) if i+1<len(rows) else 0x91c6cc
            encoded.append({'rva':hex(va-0x400000),'bytes':read_va(pin,va,end-va).hex(),'disasm':row['disasm']})
        instruction_evidence={'architecture':'x86','image_base':'0x400000','rva':'0x51c510','size':444,'sha256':sha(read_va(pin,0x91c510,444)),'source':'IDA MCP recorded instruction list;no reference executable run','instructions':encoded}
        trace.write_text(json.dumps(instruction_evidence,indent=2)+'\n',encoding='utf-8')
    instructions=[row['disasm'] for row in instruction_evidence['instructions']]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Pinned455changed')
        expected=0x91c510
        for row in instruction_evidence['instructions']:
            va=int(row['rva'],16)+0x400000;encoded=bytes.fromhex(row['bytes'])
            if va!=expected or not encoded or read_va(raw,va,len(encoded))!=encoded:raise ValueError('Constructor instruction bytes/address mismatch')
            expected+=len(encoded)
        if expected!=0x91c6cc or sha(read_va(raw,0x91c510,444))!=instruction_evidence['sha256']:raise ValueError('Incomplete constructor instruction coverage')
        ranges=[{'name':name,'rva':hex(va-0x400000),'bytes':size,'sha256':sha(read_va(raw,va,size))} for name,va,size in functions]
        if baseline is not None and baseline!=ranges:raise ValueError('Character manager/IO bodies differ betweenpins')
        baseline=ranges;value=interpret(instructions,lambda va:struct.unpack('<I',read_va(raw,va,4))[0])
        if golden is not None and golden!=value:raise ValueError('Constructor golden differs betweenpins')
        golden=value;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':ranges})
    output=WS/'work/client-reference/character-manager/ctor.bin';output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(golden)
    report={'scope':'Selected record/manager/cache/rawMSH source contracts;full dispatcher/legacyBN/animation/normal renderer still open','references':references,'constructor_golden':output.relative_to(WS).as_posix(),'constructor_golden_sha256':sha(golden),'record_bytes':1188,'manager_bytes':4148,'ctor_disassembly_sha256':sha(trace.read_bytes()),'oracle_script_sha256':sha((WS/'scripts/character_ctor_oracle.py').read_bytes()),'confirmed':['Ctor zeros1188bytes,twoidentitymatrices,material RGB0.6/0.3,Alpha792=1,minus1at696,160at672/684,3000at716','Manager preservesopaque0/name128;vector/nextId=0,cache1000pointers0;cachebase148','Cache3probes(slot=20*((key1+p)%50)+(key2+p)%20),keys byteSum%113 XOR2 and7*sum%113 XOR2;replacefirst ifallfull;lookup validatesrecordID','Exact-name firstmatch;IDcache thenfirstvectorscan;ID0 valid andmissing-name IDalso0;nextIdDWORDwrap;deleteallmatches/clear/dtor retaincache,nextId','Refresh six borrowed texture pointers plussecondaryalias5283;noAddRef','MSHraw reader usesextensionhelper returningfilename+1 whennodot;RFS beforeloose;zero-size rawallocation accepted','Dispatcher9238A0 short-circuitsloadingbyte264 orloadedDWORD260;MESH08onlyexternal-parent branch;parent mustbeloaded;MESH08failure decrementsloading,other failures oftenleavestickybyte;full implementation deferred untillegacyreader/converter'],
    'limits':['Constructor golden interprets recorded instruction subset andpinned constants,not reference EXE execution;helper91C450 semantics separatelypinned','Old CHARACTEROBJECT and455 layouts incompatible;full methods/unknown tail semantics notsupplied byrecordstorage','Cache retention canleave danglingpointers afterdelete;do notfix byguessing;unsafe stale dereferences outsidevalidated domain','Own bounded/percent-name/length/short-read/nullallocation policies differ fromunchecked ref/OOM/exception/logger/failure domains','4148byte logical storage/privateallocator padding notfull originalC++classABI;normal manager/file dispatch/BN/animation/shaders remainopen'],
    'raw_analysis':'artifacts/character-manager455;ownedc3f13f8bclosed/save;no inputEXE run'}
    (WS/'inventory/client455-character-manager-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{len(functions)}pinnedmanager/record/IO bodies;1188byte constructor golden fromrecorded instructions')
if __name__=='__main__':main()
