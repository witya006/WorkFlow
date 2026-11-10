"""Verify actual equipment wrappers, GPU contribution and retained queue poses."""
import argparse,ctypes,json,shutil,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS
from client455_own_probe import build_full_object_probe
from client455_asset_staging import stage_asset,staging_stats
from client455_runtime_inputs import copy_character_shaders,copy_grade_overlay_inputs
from audit_client455_equipment import record,sha
from audit_client455_language import decode
from audit_client455_item_payloads import item_tables

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report-label',choices=['equipment-draw','equipment-frame-render'],default='equipment-draw');args=parser.parse_args()
    source=WS/'scripts/native/client455_equipment_draw_probe.cpp'
    exe=build_full_object_probe('equipment-draw',source)
    parent=WS/'work/m9'/sha(exe)[:8];index=1
    while(parent/f'equipment-draw-{index:03d}').exists():index+=1
    run=parent/f'equipment-draw-{index:03d}';run.mkdir(parents=True)
    target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for name in ['mss32.dll','System/010.TTF','System/console.jpg','System/shader/Grass1.vsh','System/shader/grass1.vso','DataTable/ko-kr/NDLanguage.edf']:
        stage_asset(client/name,run/name);inputs.append(dict(**record(run/name),original=str(client/name)))
    ref=json.loads((WS/'inventory/client455-equipment-reference.json').read_text())
    for row in ref['inputs']:
        dest=run/row['relative'];stage_asset(Path(row['original']),dest,expected=row['sha256']);inputs.append(dict(**record(dest),original=row['original']))
    fixture=WS/ref['expected']['file'];assert sha(fixture)==ref['expected']['sha256'];shutil.copyfile(fixture,run/'expected.bin');inputs.append(record(run/'expected.bin'))
    #Independent raw EDF fields plus the audited DWORD call operands;no call to
    #the reconstructed C++ key helper when constructing the expected values.
    tables,_,_=item_tables(decode((client/'DataTable/Item.edf').read_bytes()));cases=[]
    for table in [27,37,38,39,40,41,42,43]:
        row=tables[table];assert row['count'] and row['stride']>152
        data=row['data'];index=struct.unpack_from('<I',data)[0];kind=data[88];part=data[152] if 37<=kind<=43 else 255
        cases.append([table,0,kind,index,part,(kind-37)*100+index if part!=255 else index])
    assert any(c[-1]>255 for c in cases)
    metadata=run/'render-metadata.bin';metadata.write_bytes(struct.pack('<I',len(cases))+b''.join(struct.pack('<6I',*c) for c in cases));inputs.append(record(metadata))
    inputs+=copy_character_shaders(run)+copy_grade_overlay_inputs(run)
    (run/'R3Engine.ini').write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n',encoding='ascii')
    startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    try:result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW,startupinfo=startup)
    finally:
        remove=ctypes.WinDLL('gdi32.dll').RemoveFontResourceW;remove.argtypes=[ctypes.c_wchar_p];remove.restype=ctypes.c_int;remove(str(run/'System/010.TTF'))
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    frames=[record(p) for p in sorted(run.glob('equipment-*.png'))]
    report=dict(scope='Actual typed equipment Render/default+matrix/fade/alpha/grade and retained queue pose ownership;ordinary full player and nonzero effects remain open',
        source=record(source),source_includes=[record(WS/'scripts/native'/name) for name in ['client455_grade_overlay_probe.cpp','client455_equipment_probe.cpp']],
        script=record(Path(__file__)),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),inputs=inputs,
        console=record(console),output=record(output) if output.exists() else None,native=native,natural_exit=result.returncode,frames=frames,
        shared_asset_staging=staging_stats(),input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    if args.report_label=='equipment-frame-render':
        baseline=WS/'inventory/client455-equipment-draw-native.json'
        before=json.loads(baseline.read_text());prior={Path(p['file']).name:p for p in before['frames']}
        assert len(prior)==len(frames)==6
        for row in frames:
            old=prior[Path(row['file']).name];assert sha(WS/old['file'])==old['sha256']==row['sha256'],'Equipment image changed: '+row['file']
        report['render_regression']=dict(baseline=record(baseline),equal_frames=6,comparison='SHA256 of complete PNG bytes on same controlled GPU fixture')
    text=json.dumps(report,indent=2)+'\n';(run/'probe-report.json').write_text(text);(WS/f'inventory/client455-{args.report_label}-native.json').write_text(text)
    print(json.dumps(dict(exit=result.returncode,native=native,staging=report['shared_asset_staging'],console_tail=console.read_text(errors='replace')[-1200:],run=run.relative_to(WS).as_posix())))
    if result.returncode or not native or native['status']!='PASS':raise ValueError('Equipment render failed;inspect '+str(run))
    assert all(sha(WS/row['file'])==row['sha256'] for row in inputs)

if __name__=='__main__':main()
