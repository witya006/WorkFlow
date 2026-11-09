"""Exercise the real text fallback with supplied source programs and typed objects."""
import argparse,json,struct,shutil
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,load,sha
from probe_client455_nuclear_registry import main as scenario

def fixtures(run):
    inputs=[];ref=load('client455-special-shaders-inputs')
    for program in ref['programs']:
        source=WS/program['decoded']['file'];require(sha(source)==program['decoded']['sha256'],'Verified supplied plain shader source')
        target=run/'System/shader'/('text-'+Path(program['name']).stem+'.shr');shutil.copyfile(source,target);inputs.append(record(target))
    stages='[path] .\\ignored\\\n[fx_list] 1\nnot-loaded.fx\n[vs_list] 2\ntext-vFraction.shr vs_2_0\ntext-vPlazma.shr vs_2_0\n[ps_list] 2\ntext-pFraction.shr ps_2_0\ntext-pPlazma.shr ps_2_0\n'
    parameters=[('B0','b',[1]),('Integer','i',[-7]),('Scalar','f',[.125]),('Vector','v',[1,2,3,4]),('Matrix','m44',list(range(1,17)))]+[(f'F{i}','f',[2**(i-7)]) for i in range(5,10)]
    ignored=[('SkipN','n'),('SkipTexture','t'),('SkipTimer','timer'),('SkipUnknown','unknown')]
    text=stages+'[sh_list] 3\n0 0 {\n'+''.join(n+' '+t+'\n' for n,t in ignored)+''.join(n+' '+t+' '+' '.join(map(str,v))+'\n' for n,t,v in parameters)+'}\n1 1 { Sentinel f -.5 }\n-1 65537 { }\n[end]\n'
    expected=bytearray(3*1964)
    for name,kind in ignored:
        data=name.encode()+b'\0';expected[4:4+len(data)]=data
    for i,(name,kind,values) in enumerate(parameters):
        at=4+i*196;data=name.encode()+b'\0';expected[at:at+len(data)]=data;struct.pack_into('<I',expected,at+128,{'b':1,'i':2,'f':3,'v':4,'m44':5}[kind]);struct.pack_into('<'+('i' if kind in ['b','i'] else 'f')*len(values),expected,at+132,*values)
    struct.pack_into('<HH',expected,1964,1,1);expected[1968:1977]=b'Sentinel\0';struct.pack_into('<If',expected,1968+128,3,-.5);struct.pack_into('<I',expected,3928,65537)
    generated={'text-scenario.r3s':text.encode(),'expected-objects.bin':expected,'eof-newline.r3s':b'[sh_list] 1\n1 1 { Marker f .5 }\n','eof-tight.r3s':b'[sh_list] 1\n1 1 { Marker f .5 }','text-mixed.r3s':text.replace('[vs_list] 2','[vs_list] 3').replace('text-vFraction.shr vs_2_0\n','text-vFraction.shr vs_2_0\nmissing.shr vs_2_0\n').encode()}
    for name,data in generated.items():target=run/name;target.write_bytes(data);inputs.append(record(target))
    return inputs

def verify(run,r):
    native=r['native'];require(native['programs']==4 and native['objects']==3 and native['active_parameters']==11 and native['inactive_types']==4 and native['fallback_via_restore'] and native['name_bind_cases']==8,'Actual text fallback/typed records/named bindings')
    require((run/'objects.bin').read_bytes()==(run/'expected-objects.bin').read_bytes(),'Exact1964-byte adjacent objects and196-byte parameter layouts')
    require(native['newline_objects']==2 and native['tight_objects']==1,'Original feof trailing-whitespace reprocessing')
    require(native['missing_text_preserves_tables'] and native['mixed_failures_skipped'] and native['binary_restored'],'Selected loader failure/recovery semantics')
    require(native['handles_before']==native['handles_after'] and native['memory_before']==native['memory_after'],'Selected file handles and own table allocations balanced')
    return dict(programs=4,objects=3,active_parameters=11,inactive_parameter_types=4,parameter_bytes=196,object_bytes=1964,exact_adjacent_records=True,actual_sources_bytecode_equal=True,text_fallback_via_ordinary_restore=True,named_bind_cases=8,custom_path_reset_preserved=True,fx_list_count_only=True,inclusive_object_index=True,feof_newline_duplicate_object=True,missing_text_preserves_tables=True,mixed_compile_failure_skipped=True,binary_restored=True,handles_balanced=True,table_allocations_balanced=True,full_special_renderer=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--verify-existing',action='store_true');a=p.parse_args();r=load('client455-shader-text-native') if a.verify_existing else scenario('client455_shader_text_probe.cpp','shader-text','client455-shader-text-native',expected_frames=0,prepare_run=fixtures)
    require(not r['natural_exit'] and r['native']['status']=='PASS','Successful real fallback run');run=(WS/r['exe']['file']).parent
    r.update(status='PASS_SELECTED',scope='Real ordinary Init.r3o->Init.r3s fallback,actual four source programs,typed objects and selected failure quirks',driver_script=record(Path(__file__)),world_source=record(WS/'scripts/native/client455_world_probe.cpp'),outputs=[record(run/n) for n in ['objects.bin','eof-objects.bin']],verdict=verify(run,r))
    (WS/'inventory/client455-shader-text-native.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['verdict']))
if __name__=='__main__':main()
