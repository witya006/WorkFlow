"""Run actual magic parser/layout/cache on the real archived nuclear cue."""
import json,shutil,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,sha
from client455_own_probe import build_full_object_probe
from compare_client_binaries import WS,pe


def main():
    source=WS/'scripts/native/client455_magic_probe.cpp';exe=build_full_object_probe('magic',source);holder=WS/'work/m9'/sha(exe)[:8];index=1
    while(holder/f'magic-{index:03d}').exists():index+=1
    run=holder/f'magic-{index:03d}';run.mkdir(parents=True);target=run/exe.name;shutil.copyfile(exe,target);mapping=target.with_suffix('.map');shutil.copyfile(exe.with_suffix('.map'),mapping)
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[]
    for name in ['Effect/EffectEntity59.rpk','Effect/EffectEntityList.spt','Effect/MagicSptList.spt']:
        original,dest=client/name,run/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,dest);inputs.append(dict(**record(dest),original=str(original)))
    fixtures={'fields.spt':'[MagicTrack]\naxis_type 2 3\nctrl_0 rand(-2,2) 5 7\nctrl_1 8 9 10\nctrl_2 11 12 13\ntime 0 billboard screen_blur_time 2 screen_blur_density .25\nparabola acc rot angle -120 curve 2 target .4\nparabola angle 10 curve -3 target .8\nparabola angle 12 curve 5 target 1\nmulti num 3 angle 15 delay 2000\nend\ntime 777\n',
              'boundary.spt':'[MagicTrack]\n'+''.join(f'time {i}\n' for i in range(64))+'end\n',
              'overflow.spt':'[MagicTrack]\n'+''.join(f'time {i}\n' for i in range(65))+'end\n'}
    for name,text in fixtures.items():path=run/'Effect'/name;path.write_text(text,encoding='ascii');inputs.append(record(path))
    config=run/'R3Engine.ini';config.write_text('[Path]\nEffectPath=.\\Effect\\\n',encoding='ascii');inputs.append(record(config))
    result=subprocess.run([str(target)],cwd=run,capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
    console=run/'console.txt';console.write_bytes(result.stdout+result.stderr);output=run/'result.json'
    report=dict(scope='Actual client CProcessMagic64/parser/selector/control andordinarymagiccache using real archived nuclear cue;fullrender/nuclearowner remainopen',source=record(source),script_sha256=sha(Path(__file__)),builder_sha256=sha(WS/'scripts/client455_own_probe.py'),normal_link_sha256=sha(WS/'inventory/client455-normal-link.json'),exe=record(target),map=record(mapping),architecture=pe(target.read_bytes())['architecture'],console=record(console),inputs=inputs,output=record(output) if output.exists() else None,native=json.loads(output.read_text()) if output.exists() else None,natural_exit=result.returncode,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    report['reference_sha256']=sha(WS/'inventory/client455-magic-reference.json')
    (WS/'inventory/client455-magic-native.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(exit=result.returncode,run=str(run),native=report['native'],stderr=result.stderr.decode(errors='replace')[-1200:])))
    require(not result.returncode and report['native'] and report['native']['status']=='PASS','Magic native failure')


if __name__=='__main__':main()
