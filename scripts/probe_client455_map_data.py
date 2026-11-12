"""Exercise the ordinary map owner and real MiniMap geometry without a GPU run."""
import json,shutil,struct,subprocess
from pathlib import Path
from audit_client455_map_data import record
from audit_client455_language import decode, encode_with_envelope
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-map-data-reference');source=WS/'scripts/native/client455_map_data_probe.cpp';exe=build_full_object_probe('map-data',source)
    holder=WS/'work/m9'/sha(exe)[:8];n=1
    while(holder/f'map-data-{n:03d}').exists():n+=1
    run=holder/f'map-data-{n:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping);inputs=[]
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for row in [ref['main']]+[x['input'] for x in ref['locales']]:
        original=Path(row['file']);require(original.is_relative_to(client) and sha(original)==row['sha256'],'Pinned actual map data');dest=run/original.relative_to(client);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(dict(**record(dest),original=str(original)))
    for row in ref['decoded_fixtures']+[ref['canonical'],ref['geometry_oracle']]:
        check(row);dest=run/Path(row['file']).name;shutil.copyfile(WS/row['file'],dest);inputs.append(record(dest))
    for relative, name in [('Map.edf', 'truncated-map.edf'), ('zh-tw/NDMap.edf', 'truncated-ndmap.edf')]:
        encoded = (run / 'DataTable' / relative).read_bytes()
        dest = run / name
        payload = decode(encoded)
        shortened = payload[:-1]
        envelope = encoded[:29] + struct.pack('<I', len(shortened)) + encoded[33:33+len(shortened)] + encoded[33+len(payload):]
        dest.write_bytes(encode_with_envelope(envelope, shortened))
        inputs.append(record(dest))
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Taiwan\n',encoding='ascii');inputs.append(record(config))
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW);console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);out=run/'result.json';actual=run/'canonical-actual.bin';expected=run/'canonical.bin'
    native=json.loads(out.read_text()) if out.exists() else None
    report=dict(status='PASS' if result.returncode==0 else 'FAIL',scope='Actual ordinary CLand Map/NDMap loader,110records/two appended sections;actual geometry provider with copied real BSP node fixtures;no GPU/full world load acceptance',script_sha256=sha(Path(__file__)),source=record(source),reference_sha256=sha(WS/'inventory/client455-map-data-reference.json'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],inputs=inputs,console=record(console),output=record(out) if out.exists() else None,canonical_actual=record(actual) if actual.exists() else None,canonical_equal=actual.exists() and actual.read_bytes()==expected.read_bytes(),native=native,natural_exit=result.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-map-locale-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(run=str(run),exit=result.returncode,native=native,stderr=result.stderr.decode(errors='replace')[-1800:])))
    require(not result.returncode and native and native['status']=='PASS' and report['canonical_equal'],'Map data native failure')


if __name__=='__main__':main()
