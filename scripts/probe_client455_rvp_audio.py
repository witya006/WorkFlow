"""Exercise the actual Miles API and ordinary RVP audio path on owned copies."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    source=WS/'scripts/native/client455_rvp_audio_probe.cpp';exe=build_full_object_probe('rvp-audio',source)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);old=json.loads((WS/'inventory/client455-rvp-actor-native.json').read_text())
    holder=WS/'work/m9'/sha(exe)[:8];holder.mkdir(parents=True,exist_ok=True);index=1
    while(holder/f'rvp-audio-{index:03d}').exists():index+=1
    run=holder/f'rvp-audio-{index:03d}';run.mkdir();target=run/exe.name;shutil.copyfile(exe,target);shutil.copyfile(exe.with_suffix('.map'),target.with_suffix('.map'));records=[]
    def stage(original,relative,digest=None):
        if digest and sha(original)!=digest:raise ValueError('Changed input '+str(original))
        path=run/relative;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,path);records.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path),original=str(original)))
    for row in old['inputs']:
        if Path(row['file']).name=='R3Engine.ini':continue
        original=WS/row['file'];relative=original.relative_to((WS/old['exe']['file']).parent);stage(original,relative,row['sha256'])
    for name in ['mss32.dll','mssmp3.asi','Snd/WaveList.spt']:stage(client/name,name)
    candidates=[p for p in (client/'Snd').rglob('*') if p.is_file() and p.suffix.lower()=='.mp3' and p.stat().st_size>60000]
    if not candidates:raise ValueError('Actual MP3 fixture missing')
    mp3=min(candidates,key=lambda p:(p.stat().st_size,str(p)));stage(mp3,'loop.mp3')
    inputs=json.loads((WS/'inventory/client455-rvp-audio-inputs.json').read_text());wav=next(a for a in inputs['assets'] if a['exists'] and a['extension']=='.wav');stage(Path(wav['file']),'stock.wav',wav['sha256'])
    config=run/'R3Engine.ini';config.write_text('[Setup]\nLanguage=Korea\n[RenderState]\nScreenXSize=640\nScreenYSize=480\nbFullScreen=FALSE\nTextureDetail=3\n[Sound]\nSound=TRUE\nMusic=TRUE\n',encoding='ascii')
    raw='[Object]\n'+''.join('*'+name+' .\\animated.msh\ntexpath .\\tex\nbone .\\animated.bn\nani .\\animated.ani\n'+('wav loop.mp3 wav_dist 200\n' if name=='first' else '') for name in ['first','second'])
    raw+='[PrepareTrack]\n*first *Dummy01\n*second *Dummy01\nno_camera\nwav *Dummy01 loop.mp3 200\n[Track]\n*frame 1\nwav *first stock.wav 200\n*frame 2\ntimer_rate .5\n'
    fixture=run/'audio.rvp';fixture.write_text(raw,encoding='ascii');stage(client/'Map/neutralAS1/neutralAS1.cam','audio.cam')
    for path in [config,fixture]:records.append(dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)))
    console=run/'console.txt'
    with console.open('wb') as stream:result=subprocess.run([str(target)],cwd=run,stdout=stream,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path)) if path.exists() else None
    output=run/'result.json';native=json.loads(output.read_text()) if output.exists() else None
    report=dict(scope='Actual Miles sample decoder/status/volume/loop/table lifecycle and ordinary RVP ambient/event/timer route;not audible-output capture or fullsound/game parity',source=record(source),script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),engine_report_sha256=sha(WS/'inventory/client455-startup-engine-build.json'),exe=record(target),map=record(target.with_suffix('.map')),console=record(console),output=record(output),inputs=records,native=native,natural_exit=result.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    path=WS/'inventory/client455-rvp-audio-native.json';path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(run=run.relative_to(WS).as_posix(),exit=result.returncode,native=native,console=console.read_text(errors='replace')[-1800:])))
    if result.returncode:raise SystemExit(result.returncode)
    if any(sha(WS/r['file'])!=r['sha256'] or ('original' in r and sha(Path(r['original']))!=r['sha256']) for r in records):raise ValueError('Mutated input')
    report['inputs_unchanged']=True;path.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
