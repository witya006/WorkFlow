"""Pin confirmed cumulative Character counters without guessing an eighth field."""
import hashlib,json
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from audit_client455_effect_tables import loaded

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];last=None
    functions=[('texture_producer',0x934a20,0x33d),('vertex36_producer',0x93de00,0x78),('vertex64_producer',0x93df80,0x78),('index_producer',0x93e100,0x75),('mesh_ctor',0x9214e0,0x1c2),('ani_import',0x93acd0,0x145),('debug_counter_consumer',0x7f26f1,0xa7),('unassociated_zero32_ctor',0x9312e0,0x1c)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for name,at,size in functions]
        if last is not None and bodies!=last:raise ValueError('Counter bodies differ')
        last=bodies;initial=loaded(raw,0x11895f8,28)
        if any(initial):raise ValueError('Counter initial image changed')
        refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies,'confirmed_initial_counters':{'rva':'0xd895f8','bytes':28,'sha256':sha(initial),'all_zero':True}})
    sample=WS/'work/client-reference/character-animation455/sample_001.ani'
    fields=[('m_TextureSize',0x11895f8),('m_TextureNum',0x11895fc),('m_VertexSize',0x1189600),('m_VetexNum',0x1189604),('m_AniSize',0x1189608),('m_ObjectNum',0x118960c),('m_ObjectSize',0x1189610)]
    report={'scope':'Seven confirmed cumulative DWORD counters and normal process ownership/read facade;not live heap/private global ABI or full game acceptance','references':refs,'fields':[{'source_field':name,'rva':hex(at-0x400000)} for name,at in fields],'ani_fixture':sample.relative_to(WS).as_posix(),'ani_fixture_sha256':sha(sample.read_bytes()),'ani_bytes':sample.stat().st_size,'raw_analysis':'artifacts/normal-accounting455;ownedIDA6b33fc0a','facts':['Texture bytes +=4*width*height andcount++ on successful addition;deletion doesnot subtract','Shared buffer creation adds2300000vertex or1000000index andcount++;release doesnot subtract','Mesh constructor adds5803bytes andcount++;rawANI RFS adds_msize,loose addsfilelength','Only confirmed seven fields exposed as own source snapshot,not an overlay;unassociated32-byte zero ctor has no found xrefs'],'gaps':['Eighth field/private32byte association unproven;do not infer semantics from unused constructor','Original async data races/diagnostic float formatting/allocator extent failures not accepted','Full normal WinMain/device-reset/gameplay/UI/network acceptance remains open'],'script_sha256':sha((WS/'scripts/audit_client455_normal_accounting.py').read_bytes())}
    (WS/'inventory/client455-normal-accounting-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:7counter fields/producers/consumer pinned both455bins;no guessed eighthfield')
if __name__=='__main__':main()
