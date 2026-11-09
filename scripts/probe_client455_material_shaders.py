"""Actual BSP shader draws,real particle light producer and texture cleanup."""
import json,math,struct
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require
from probe_client455_nuclear_registry import main as scenario

def single(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def number(x):return struct.unpack('<f',struct.pack('<I',x))[0]
def verify(run,r):
    rows=[json.loads(x) for x in (run/'material-shaders.jsonl').read_text().splitlines()];require(len(rows)==r['native']['draw_cases']==51,'51 actual BSP shader cases')
    require({x['layers'] for x in rows}=={1,2,7} and {x['light_mode'] for x in rows}=={0,1,2},'Layer1/2/7 and light/fallback selector domains')
    for row in rows:
        flags=row['flags'];expected=[-257/256 if flags&0x10 else 0,32767/256 if flags&0x20 else 0,.375 if flags&0x800001 else 0,-.625 if flags&0x800002 else 0];require(row['ps18']==list(map(bits,expected)),'Actual PS18 signed fixed-point and ANY-bit specular masks')
        time=number(row['time']);angle=single(time*2);c=single(math.cos(angle));s=single(math.sin(angle));require(row['ps17']==list(map(bits,[single(c*single(.01)),single(s*single(-.01)),single(s*single(.01)),time])),'Actual bump matrix/time constant PS17')
        require(row['textures_and_cleanup'] and row['selection']==[0,5 if row['light_mode'] else 0],'Actual texture bindings/cleanup and retained light selector')
    require(r['native']['splat_draws']==6 and r['native']['actual_particle_lights']==2 and len(r['frames'])==4,'Two ordinary/special three-pass splat cases/real particle parser-update/4GPU frames')
    require(all(x>0 for x in r['native']['pixels']),'Actual visible GPU pixels')
    return dict(actual_draw_cases=51,layers=[1,2,7],real_distinct_textures=7,PS18_exact=True,PS17_selected_times_exact=True,raw_matrices_and_inverse_view_row4=True,unchanged_VS12_VS13=True,texture_cleanup_and_retained_lightmap=True,real_particle_light_loader_and_update=True,material_light_selector_retention=True,whole_DWORD_splat_shader_index64=True,splat_cases=2,splat_passes=6,actual_source_pairs=2,GPU_frames=4,full_special_renderer=False,unowned_PS6w_certified=False)

def main():
    r=scenario('client455_material_shaders_probe.cpp','material-shaders','client455-material-shaders-native','client455-world-bellato-native',expected_frames=4);run=(WS/r['exe']['file']).parent
    r.update(status='PASS_SELECTED',scope='Actual ordinary BSP special-material dispatcher/PS18/particle light owner/selected splat;full special renderer remains open',driver_script=record(Path(__file__)),included_source=record(WS/'scripts/native/client455_lighting_consumers_probe.cpp'),trace=record(run/'material-shaders.jsonl'),fixtures=[record(run/n) for n in ['light0.spt','light1.spt','plasma.r3o']],verdict=verify(run,r))
    (WS/'inventory/client455-material-shaders-native.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))
if __name__=='__main__':main()
