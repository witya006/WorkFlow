"""Own hidden-window D3D8 lab: real engine/asset loading, no normal game startup."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import struct
from pathlib import Path
from compare_client_binaries import WS,pe
from probe_client_helpers import import_names


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cli=argparse.ArgumentParser();cli.add_argument('--entity',action='store_true');cli.add_argument('--particle',action='store_true');cli.add_argument('--level',choices=['lobby','Platform01'],action='append',default=[])
    cli.add_argument('--output',default='inventory/client455-graphics-runtime.json');args=cli.parse_args()
    report_path=WS/args.output
    if report_path.resolve().parent!=(WS/'inventory').resolve() or report_path.suffix!='.json':raise ValueError('Graphics report must be a JSON directly under inventory/')
    build=json.loads((WS/'inventory/client-helper-lab-build.json').read_text(encoding='utf-8'))
    if build['build_exit'] or build['build_settings'].get('RF_CLIENT_455_RESOURCE_IO')!='ON':raise ValueError('Successful graphics-enabled lab build required')
    for group in ['graphics_input_sha256','lab_input_sha256','resource_input_sha256','weather_input_sha256']:
        for name,digest in build[group].items():
            if sha(WS/name)!=digest:raise ValueError('Stale graphics build input')
    original=WS/'work/client-build/build-helper-lab/Release/RF_Online.bin';digest=sha(original)
    pe(original.read_bytes())
    if set(import_names(original.read_bytes(),13))!={'mss32.dll','abuse.dll','adv.dll','pdll.dll'}:raise ValueError('Game DLLs must stay delayed')
    if json.loads((WS/'inventory/client455-x87-link.json').read_text(encoding='utf-8'))['lab']['sha256']!=digest:raise ValueError('Linked math proof stale')
    root=WS/'work/client-graphics-lab'/digest[:16];root.mkdir(parents=True,exist_ok=True)
    exe=root/'RF_Online.bin'
    if exe.exists() and sha(exe)!=digest:raise ValueError('Preserving unexpected graphics snapshot')
    if not exe.exists():shutil.copyfile(original,exe)
    if any(root.rglob('*.dll')) or any(original.parent.glob('*.dll')):raise ValueError('Unexpected local DLL')
    resources=json.loads((WS/'inventory/client455-map-resources.json').read_text(encoding='utf-8'))
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));reference=Path(paths['client_455'])
    wanted={p['archive'] for asset in resources['selected_assets'] for p in asset['providers'] if 'archive' in p}
    archive_inputs=[]
    cases=[('device',None)]
    if args.entity:
        for asset in resources['selected_assets']:
            if asset['path'].endswith('.r3e'):cases.append((f'entity-{len(cases):02}',asset['path']))
    if args.particle:
        for asset in resources['selected_assets']:
            if asset['path'].endswith('.spt'):cases.append((f'particle-{len(cases):02}',asset['path']))
    for level in args.level:cases.append(('level-'+level,'Map/'+level+'/'+level+'.bsp'))
    all_results=[]
    for case,input in cases:
        folder=root/case;folder.mkdir(parents=True,exist_ok=True)
        if any(folder.glob('result-*.json')):
            attempt=len(list(folder.glob('result-*.json')))+1
        else:attempt=1
        output=folder/f'result-{attempt:03}.json'
        for name in ['frame.bmp','particle.json','level.json','fpu.json','map-time.json']:
            transient=folder/name
            if transient.exists():
                if not transient.resolve().is_relative_to(root.resolve()):raise ValueError('Transient artifact outside own lab')
                transient.unlink()
        (folder/'R3Engine.ini').write_text('[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=FALSE\nMusic=FALSE\n',encoding='ascii')
        inputs=[]
        if input:
            used=sorted(row['path'] for row in resources['archives']) if case.startswith('level') else sorted(wanted)
            for rel in used:
                record=next(row for row in resources['archives'] if row['path']==rel)
                source=reference/rel
                if sha(source)!=record['sha256']:raise ValueError('Pinned graphics archive changed')
                dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True)
                if dest.exists() and sha(dest)!=record['sha256']:raise ValueError('Staged graphics archive changed')
                if not dest.exists():shutil.copyfile(source,dest)
                inputs.append({'path':rel,'sha256':record['sha256']})
            if case.startswith('level'):
                source_folder=reference/'Map'/case.removeprefix('level-')
                for source in sorted(source_folder.rglob('*')):
                    if not source.is_file() or source.suffix.lower() in ('.exe','.dll'):continue
                    rel=source.relative_to(reference);dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True)
                    fingerprint=sha(source)
                    if dest.exists() and sha(dest)!=fingerprint:raise ValueError('Preserving changed staged level input')
                    if not dest.exists():shutil.copyfile(source,dest)
                    inputs.append({'path':rel.as_posix(),'sha256':fingerprint})
        env=os.environ.copy();env['RF_LAB_HELPER_OUTPUT']=str(output)
        if input:env['RF_LAB_HELPER_INPUT']='.\\'+input.replace('/','\\')
        mode='--rf-graphics-level' if case.startswith('level') else '--rf-graphics-particle' if case.startswith('particle') else '--rf-graphics-entity' if input else '--rf-graphics-device'
        process=subprocess.run([str(exe),mode],cwd=folder,env=env,capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
        result=json.loads(output.read_text(encoding='utf-8')) if output.exists() else {'stage':'missing-native-report'}
        result.update({'case':case,'input':input,'exit_code':process.returncode,'output':output.relative_to(WS).as_posix(),'archives':inputs})
        if (folder/'particle.json').exists():result['particle']=json.loads((folder/'particle.json').read_text())
        if (folder/'level.json').exists():result['level']=json.loads((folder/'level.json').read_text())
        if (folder/'fpu.json').exists():result['fpu_stages']=json.loads((folder/'fpu.json').read_text())
        if (folder/'map-time.json').exists():result['map_time']=json.loads((folder/'map-time.json').read_text())
        frame=folder/'frame.bmp'
        if frame.exists():
            image=frame.read_bytes()
            if image[:2]!=b'BM' or struct.unpack_from('<ii',image,18)!=(640,-480) or len(image)!=54+640*480*3:raise ValueError('Malformed GPU frame')
            pixels=image[54:]
            changed=sum(pixels[i:i+3]!=b'\x30\x20\x10' for i in range(0,len(pixels),3))
            if changed!=result['changed_pixels']:raise ValueError('Independent BMP pixel count differs from GPU report')
            snapshot=folder/f'frame-{attempt:03}.bmp';shutil.copyfile(frame,snapshot)
            result['frame']=snapshot.relative_to(WS).as_posix();result['frame_sha256']=sha(snapshot)
        all_results.append(result)
        if process.returncode:break
    report={'exe':exe.relative_to(WS).as_posix(),'exe_sha256':digest,'architecture':'x86','cases':all_results,
            'graphics_source_sha256':build['graphics_input_sha256'],
            'scope':'Own hidden-window real D3D8 HAL device/engine, selected RPK assets and optional actual CLevel::LoadLevel. Normal game WinMain, reference EXE, D3D9 comparison, sound/network not executed; no game DLL provider present.'}
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cases':len(all_results),'stage':all_results[-1]['stage'],'exit':all_results[-1]['exit_code'],'result':args.output}))
    if any(row['exit_code'] or row.get('failures') or row.get('errors') for row in all_results):raise ValueError('Graphics probe did not complete; inspect recorded stage/evidence')


if __name__=='__main__':main()
