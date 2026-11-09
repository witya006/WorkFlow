"""Exercise real ordinary text/binary material loaders with7-layer boundaries."""
import argparse,json,struct
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,require,sha
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as scenario


def verify(run,native):
    binary=(run/'binary-materials.bin').read_bytes();text=(run/'text-materials.bin').read_bytes();require(len(binary)==len(text)==1052,'Two adjacent526-byte records per loader');expected=bytearray(1052);base=native['native']['base']
    for index in range(2):
        offset=index*526;struct.pack_into('<I',expected,offset,2 if not index else 0);name=b'sentinel' if index else b'seven';expected[offset+4:offset+4+len(name)]=name
        struct.pack_into('<IifI',expected,offset+132,0x22 if index else 0x10,3+base if index else -1,2. if index else 1.5,0 if index else 7)
    for layer in range(7):struct.pack_into('<hiIII14h',expected,148+layer*54,layer+1,20+layer+base,layer,0x80402010+layer,0x10,*[layer*32+x for x in range(14)])
    require(binary==expected,'Exact binary serialized46->runtime54 mapping;extra floats zero and adjacent record preserved')
    expected=bytearray(1052)
    for index in range(2):
        offset=index*526;struct.pack_into('<I',expected,offset,2 if not index else 0);name=b'sentinel' if index else b'seven';expected[offset+4:offset+4+len(name)]=name
        struct.pack_into('<IifI',expected,offset+132,0 if index else 0x11007f05,-1,0.,0 if index else 7)
        for layer in range(7):
            at=offset+148+layer*54;struct.pack_into('<i',expected,at+2,-1);struct.pack_into('<I',expected,at+10,0xffffffff)
            if not index:struct.pack_into('<I',expected,at+14,0x800003);struct.pack_into('<H',expected,at+38,0xff);struct.pack_into('<ff',expected,at+46,(layer+1)*.125,1.5+layer*.25)
    require(text==expected,'Exact text init/defaults,7layer fields and fullDWORD shader/light flag packing')
    require(native['native']['bad_versions']==3 and native['native']['handles_before']==native['native']['handles_after'] and native['native']['warnings']==3,'Rejected version closes its file')
    return dict(binary_materials=2,text_materials=2,layers=7,serialized_stride=46,runtime_stride=54,material_stride=526,adjacent_records_preserved=True,specular_fields=True,packed_material_flags=True,rejected_versions=3,full_material_shader=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-existing',action='store_true');args=parser.parse_args();file=WS/'inventory/client455-material-layout-native.json'
    r=load('client455-material-layout-native') if args.verify_existing else scenario('client455_material_layout_probe.cpp','material-layout','client455-material-layout-native',None,expected_frames=0)
    require(not r['natural_exit'] and r['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Current own material loader run');run=(WS/r['exe']['file']).parent
    r.update(status='PASS_SELECTED',scope='Actual ordinary R3M/MST material loaders,7layers/runtime54/material526,serialized46 and rejected version cleanup;fullshader open',driver_script=record(Path(__file__)),included_source=record(WS/'scripts/native/client455_lighting_consumers_probe.cpp'),world_source=record(WS/'scripts/native/client455_world_probe.cpp'),material_source=record(WS/'scripts/native/client455_sky_material_probe.cpp'),
             generated_inputs=[record(run/n) for n in ['seven.r3m','bad-version.r3m','text/MainMaterial.mst','text/seven.mst','text/sentinel.mst']],outputs=[record(run/n) for n in ['binary-materials.bin','text-materials.bin']],verdict=verify(run,r))
    file.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))


if __name__=='__main__':main()
