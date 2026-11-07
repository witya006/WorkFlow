"""Real tagged Miles audio, with a silent lab and actual radar WAV input."""
import json,shutil,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,sha
from client455_own_probe import build_full_object_probe
from client455_runtime_inputs import copy_tagged_sound_providers
from compare_client_binaries import WS,pe


def main():
    source=WS/'scripts/native/client455_tagged_audio_probe.cpp';exe=build_full_object_probe('tagged-audio',source)
    holder=WS/'work/m9'/sha(exe)[:8];index=1
    while(holder/f'tagged-audio-{index:03d}').exists():index+=1
    run=holder/f'tagged-audio-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=copy_tagged_sound_providers(run)
    for name in ['mss32.dll','Snd/WaveList.spt','Snd/Character/Newclear/Radar_00.wav']:
        original,dest=client/name,run/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(dict(**record(dest),original=str(original)))
    config=run/'R3Engine.ini';config.write_text('[Sound]\nSound=TRUE\nMusic=TRUE\n[Path]\nSoundPath=.\\Snd\\\n',encoding='ascii')
    fixture=run/'fixture.spt';fixture.write_text('[WaveList]\n'+''.join(f'{id} .\\Snd\\Character\\Newclear\\Radar_00.wav\n' for id in range(1000,1070)),encoding='ascii');inputs+=[record(config),record(fixture)]
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json'
    report=dict(scope='Actual MainApp tagged audio owner/Miles provider/listener/PCM/30sample channels/64LRU;muted lab,not audible-output capture or full nuclear/audio parity',source=record(source),script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],console=record(console),inputs=inputs,output=record(output) if output.exists() else None,natural_exit=result.returncode,native=json.loads(output.read_text()) if output.exists() else None,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-tagged-audio-native.json').write_text(json.dumps(report,indent=2)+'\n')
    report['reference_sha256']=sha(WS/'inventory/client455-tagged-audio-reference.json')
    report['runtime_inputs_sha256']=sha(WS/'scripts/client455_runtime_inputs.py')
    (WS/'inventory/client455-tagged-audio-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(exit=result.returncode,run=str(run),native=report['native'],stderr=result.stderr.decode(errors='replace')[-1200:])))
    require(not result.returncode and report['native'] and report['native']['status']=='PASS','Tagged audio native failure')


if __name__=='__main__':main()
