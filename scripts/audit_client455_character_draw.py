"""Pin the main Character draw, effects, deferred routes and shared constants."""
import hashlib,json,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];previous=None
    ranges=[('material_rgba',0x91c450,0x3a),('main_draw',0x92e5f0,0x1590),('bump_oscillator',0x92d330,0xa2),('effect_stage',0x92d3e0,0x2b1),('transparent_reset',0x92d270,0x5a),('transparent_depth',0x92d6c0,0x26),('transparent_insert',0x92d6f0,0x130),('transparent_packet',0x91f300,0xe6),('batch_capture',0x92d9d0,0x187),('batch_draw',0x930650,0x35e),('dynamic_draw',0x92db60,0x5d4),('transparent_draw',0x930a40,0x89b),('shadow_draw',0x930120,0x394)]
    constants=[('environment',0xbf8360,64),('pi',0xada958,8),('bump_rate',0xaab200,8),('bump_negative_rate',0xb37360,8),('color_denominator',0xb3add8,8)]
    for folder,label in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=target[label]['sha256']:raise ValueError('Changed client pin')
        bodies=[{'name':n,'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for n,at,size in ranges]
        values=[{'name':n,'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size)),'values':list(struct.unpack('<16f' if size==64 else '<d',read_va(raw,at,size)))} for n,at,size in constants]
        if previous is not None and previous!=(bodies,values):raise ValueError('Draw bodies/constants differ')
        previous=(bodies,values);references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies,'constants':values})
    expected=[.5,0,0,0,0,-.5,0,0,0,0,1,0,.5,.5,0,1]
    if values[0]['values']!=expected or values[-1]['values']!=[2147483264.0]:raise ValueError('Changed effect constants')
    record={'scope':'Source main/effects/transparency/batch/CPU/shadow routes;normal renderer/highlevel visibility remain open','references':references,'draw_fixture_report_sha256':sha((WS/'inventory/client455-draw-reference.json').read_bytes()),'script_sha256':sha((WS/'scripts/audit_client455_character_draw.py').read_bytes()),'raw_analysis':'artifacts/character-animation455/route-*.json and draw-main{,-tail}.json','instruction_pagination':'route-main-all-instructions.json has1582 actual instructions;each120-instruction page checked against actual length. Earlier draw-main-insn.json was silently clipped to10lines despite982count/cursor.done;do not use it as complete evidence.','confirmed':['Effect stage iscdecl(device,stage,type,color,scroll),five stackargs;decompiler registerargs and apparent matrix+3 overread are wrong','Indexed transparent branch selectsprogram11 again even whenentry effect2 initiallyselected6','Bump branch reuses main material scratch;first bump without prior basic material isundefined stack content inreference'],'gaps':['StaticCRT sine-cosine/failure-OOM/uninitialized-stack domains unproven','8C2A90 scene-frustum publication is explicit external dependency whenorthographic isenabled','Highlevel culling/wrappers/simpledraw/normaltypedrenderer andfullM9 acceptance remainopen']}
    (WS/'inventory/client455-character-draw-reference.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('PASS:13pinned draw bodies/5constants;MCP pagination verified')
if __name__=='__main__':main()
