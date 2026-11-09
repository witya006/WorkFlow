"""Pin ordinary effect scheduling, lifecycle, render passes and R3T warning."""
import hashlib
import json
import re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require, sha
from compare_client_binaries import WS, pe


def main():
    path=WS/'artifacts/client455-progress/effect-runtime106-reference.json'
    raw=json.loads(path.read_text());functions=[row['fn'] for row in raw['ranges']['result']]
    require(len(functions)==16 and all(functions) and all(row['cursor']['done'] for row in raw['functions']+raw['assembly']),'Full coverage')
    require(sum(row['instruction_count'] for row in raw['assembly'])==2546,'Instruction coverage')
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    master_path=WS/'inventory/client455-magic-reference.json';master=json.loads(master_path.read_text())
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin';data=binary.read_bytes()
        require(sha(binary)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned input')
        ranges=[dict(rva=hex(int(fn['addr'],16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(fn['addr'],16),int(fn['size'],16))).hexdigest()) for fn in functions]
        selected=[row for row in master['references'][len(references)]['ranges'] if row['rva']=='0x3d8970']
        require(len(selected)==1 and hashlib.sha256(read_va(data,0x7d8970,selected[0]['bytes'])).hexdigest()==selected[0]['sha256'],'Previously pinned master start')
        globals=[dict(rva=hex(addr-0x400000),bytes=size,sha256=hashlib.sha256(read_va(data,addr,size)).hexdigest()) for addr,size in [(0xbddcac,2),(0xb394c4,37)]]
        require(read_va(data,0xbddcac,2)==b'\x02\x00','Initial quality2')
        source=WS/'work/client455-port/source/R3Engine/1stclass/r3d3dtex.cpp';body=source.read_bytes().split(b'void R3ReleaseTextureMem(int id)',1)[1].split(b'static CTextureRender',1)[0]
        text=re.findall(rb'Warning\("(R3T[^"\r\n]+)",""\);',body)
        require(len(text)==1 and read_va(data,0xb394c4,37).split(b'\0',1)[0]==text[0],'Exact target warning')
        references.append(dict(sha256=sha(binary),architecture='x86',image_base='0x400000',ranges=ranges,additional_master_range=selected[0],globals=globals))
    require(references[0]['ranges']==references[1]['ranges'] and references[0]['globals']==references[1]['globals'],'Reference equivalence')
    report=dict(status='CONFIRMED_SELECTED',scope='Ordinary effect512/scheduling quality owner, disappear/eviction/lifecycle and opaque/alpha selection; actual cue rendering and cancellation require native evidence, full client remains open',script_sha256=sha(Path(__file__)),raw_evidence=record(path),references=references,functions=16,instructions=2546,master_start_prior_reference=record(master_path),legacy_texture_source=record(source),target_R3T_release_warning_confirmed=True,
                contracts=['CEffectList136x512; capacity eviction releases particle before compaction',
                           'Master capacity256 evicts with force1 before reducing count; all255 survivor records copied before inserting new master',
                           'Quality WORD initial2; apply(enable1,option0/3/other) maps0/1/2, other enable maps2; cached magic prune preserves target whitelist and zero-ID early return',
                           'Frame scheduling preserves duplicate forced cue emissions, independent whitelist branches, rawframes, state0/2/4 master cleanup and stale last-child special writes',
                           'SetDisappear time0 stops particle emission and setsNO_LOOP; negative releases/deletes/removes shell; nonparticle time<=0 removes immediately; NaN follows unordered comparisons',
                           'DeleteMagicList notifies every child with0 or-1 before compaction; finished/evicted particle callsReleaseParticle before delete',
                           'Opaque mask4C4B400 overrides ordinary flags; states3/5 skipped; alpha pass then unconditional entityfade pass; fog restored afterward',
                           'R3T warning RVA7394c4 and GPU-release branch exist in target; six selected cleanup warnings are preserved behavior'],
                gaps=['Screen-blur runtime provider explicitly refuses; advanced motion/axis/parabola/multi/curve/RNG/unsafe/FP domains remain open',
                      'Quality kernel is source-owned and directly exercised; 455 option-field/UI producer not wired, default2 used in ordinary process',
                      'Legacy RenderAll calls the restored passes consecutively; placement around other world passes and full dynamic-light compositing/device reset remain unaccepted',
                      'Nuclear pending/position/cancel/tagged sound/messageC1A owner remains unported; effect cancellation alone does not close that feature',
                      'Other cache/zero-input/OOM/shared curve pointers/concurrency/shutdown/private ABI and all previous client-acceptance gaps remain mandatory'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-effect-runtime-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('16functions/2546asm/16equalranges;targetR3Treleasewarning confirmed')


if __name__=='__main__':main()
