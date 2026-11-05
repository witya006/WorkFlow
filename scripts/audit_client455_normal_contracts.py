"""Pin the five normal model/animation contracts against both455 binaries."""
import hashlib,json
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());references=[];previous=None
    functions=[('animation_reset',0x931fb0,0x13c),('rematch_parent',0x931a80,0x37),
        ('rematch_kernel',0x93bb70,0xc1),('set_eye_matrix',0x931ac0,0x93),
        ('set_texture_path',0x608140,0x36),('import_bounds_wrapper',0x931810,0x50),
        ('import_bounds_reader',0x93bf90,0x62),('actor_reset_caller',0x7cd9f0,0x19c),
        ('equipment_rematch_reset_caller',0x451330,0x90),('eye_matrix_caller',0x51db70,0x64)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455reference')
        rows=[{'name':name,'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for name,at,size in functions]
        if previous is not None and previous!=rows:raise ValueError('Contract/caller bytes differ between455pins')
        references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':rows});previous=rows
    report={'scope':'Five normal Character455contracts and their callees/callers;not complete client equivalence',
        'references':references,'facts':[
        '931FB0 reads renderer33840. If current descriptor exists and enabled, free old previous, shallow-copy32bytes, save frame/max to684/688, reset elapsed692 and set680',
        '931FB0 always resets mesh5094/5103/5131/current5095;previous is retained unless replaced. Nonnull model ends frame160/max0',
        '931A80 nullguards both models then calls existing93BB70:only external-parent5495 meshes, first exact matching name',
        '931AC0 first exact mesh name;copy64matrix bytes to5503 then enable DWORD5499;ret72stack bytes',
        '608140 only source nullguard,strncpy255at model276,byte531 preserved',
        '931810->93BF90 loose fopen rb,skip256name,read second12then first12,ignore shortreads,return1for openedfiles'],
        'bounds':['Original OOM/unchecked-pointer failure behavior not reproduced;modern allocator throws bad_alloc',
        'Renderer33840 constructor sets0;normal producers enabling blend and initializing33844remain unproven',
        'Model blend elapsed advancement andcomplete actor lifecycle still open;reset alone doesnot establish timed blending'],
        'script_sha256':sha((WS/'scripts/audit_client455_normal_contracts.py').read_bytes())}
    (WS/'inventory/client455-normal-contracts-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Pinned five normal model contracts and ten body/caller ranges in both455references')
if __name__=='__main__':main()
