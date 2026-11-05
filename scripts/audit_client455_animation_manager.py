"""Pin the actual animation collection and its constructor/cache/owner contracts."""
import hashlib,json,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];previous=None
    ranges=[('ctor',0x5e1150,0x74),('cache_ctor',0x5e11d0,0x29),('vector_ctor',0x5e7ec0,0x30),('allocator_base',0x5e9380,0x24),('allocator_copy',0x5ea9d0,0x18),('vector_empty',0x5e9280,0x85),('init_counters',0x932480,0xf),('hash_row',0x9321b0,0x39),('hash_column',0x9321f0,0x42),('cache_find',0x932240,0x90),('cache_put',0x9322d0,0xaa),('id_by_name',0x9329b0,0xa4),('find_suffix',0x932a60,0xc6),('find_name',0x932b30,0xbc),('find_id',0x932bf0,0x4c),('delete_name',0x932d30,0xe9),('delete_id',0x932e20,0x67),('release_records_vector',0x932f30,0xb9),('vector_grow',0x933020,0x1b5),('push',0x933230,0x4d),('register',0x933280,0xd0),('get_or_register',0x931f80,0x30),('unity_get',0x5e12c0,0xe6),('synchronous_false_import',0x9352a0,0x80),('synchronous_true_import',0x935320,0x80)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455')
        bodies=[{'name':n,'rva':hex(at-0x400000),'bytes':count,'sha256':sha(read_va(raw,at,count))} for n,at,count in ranges]
        if previous and previous!=bodies:raise ValueError('Manager bodies differ')
        previous=bodies;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies,'worker_va_byte_occurrences':raw.count(struct.pack('<I',0x935450))})
    source=json.loads((WS/'inventory/client455-animation-reference.json').read_text(encoding='utf-8'))['samples'][0]
    if sha((WS/source['copy']).read_bytes())!=source['sha256'] or source['kind']!='real':raise ValueError('Changed ANI sample')
    report={'scope':'Source AnimationManager4028 collection/cache/record ownership;normal oldSDK consumer migration separate','references':references,'sample':source,'script_sha256':sha((WS/'scripts/audit_client455_animation_manager.py').read_bytes()),'confirmed':['Manager allocated0xFBC;self0/allocatorpadding4 preserved/vector8-12-16/counter20zero/nextId24one/cache28+4000zero','Register lowercases short plain name,duplicate returnsfalse,no file load,record284 ID264,nextId incrementsafter push,vector capacity grows1.5x','IDcache uses3probes andfirstslotreplacement,deleted records remaincached;no invalidation bydelete/release','Suffix compares fromlastbackslash INCLUDING separator;managerrelease destroysrecords thenfreesvector/zeros8-12-16 only','Both importer modes use synchronous dispatch;worker935450 noxref incheckedIDA/currentimage immediateVA occurrence recorded,not claimed unreachable proof'],'remaining':['Normal CUnityAniMgr/ChAnimation types stilllegacy;no rawcast allowed','UI-specific CUnityGetAni failure policy/localization/async external entry lifetime notrestored','Owned guards forlong-percent/null names/missingbackslash/OOM differfromundefined reference domains','Original C++ allocator/exception/privateSTL ABI notcertified'],'raw_analysis':'artifacts/character-animation455/manager-*.json;ownedab74ea29/4c43ad92 closed/save'}
    (WS/'inventory/client455-animation-manager-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:25manager ranges bothpins;one real ANI sample frozen')
if __name__=='__main__':main()
