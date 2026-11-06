"""Pin actual RVP runtime identities/clock semantics; retain unfinished providers."""
import hashlib
import json
from pathlib import Path
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    raw_path=WS/'artifacts/client455-progress/rvp-runtime079.json'
    extra_path=WS/'artifacts/client455-progress/rvp-runtime079-ranges.json'
    body=json.loads(raw_path.read_text());extra=json.loads(extra_path.read_text())
    prior_path=WS/'inventory/client455-rvp-reference.json';prior=json.loads(prior_path.read_text())
    references=[]
    for folder,old in zip(['current','reference-backup'],prior['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=old['sha256']:raise ValueError('Changed455 runtime pin')
        ranges=list(old['ranges'])
        for row in extra['result']:
            if row['error']:raise ValueError('Missing runtime function')
            addr,size=int(row['fn']['addr'],16),int(row['fn']['size'],16)
            ranges.append(dict(rva=hex(addr-0x400000),bytes=size,sha256=hashlib.sha256(read_va(raw,addr,size)).hexdigest()))
        if references and ranges!=references[0]['ranges']:raise ValueError('RVP runtime ranges differ')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges))
    assemblies=list(assembly_rows([body[key] for key in ['frameAsm','startAsm','clockAsm','releaseAsm']]))
    report=dict(scope='Ordinary RVP camera/timeline/empty-actor-list source path; full player/Tutorial still open',
        references=references,assemblies=assemblies,script_sha256=sha(Path(__file__)),
        raw_evidence=[dict(file=p.relative_to(WS).as_posix(),sha256=sha(p)) for p in [raw_path,extra_path]],
        prior_reference_sha256=sha(prior_path),
        corrected_identities={'0x4d5510':'Render, called by level8E7C40','0x4d8340':'Release, called by level8E7730'},
        facts=['8D4C10 reads play;8D4C20 writes pause;Start sets play before testing loaded movie',
            'FrameMove guards level/CAM/loaded;flag16 skips track/camera path;no-camera4 consumes camera-dependent events',
            'Pause/not-playing extracts first,sets float seconds,then marks play false and sets no-camera4/density0.25',
            '8D1D90 float setter stores tick=now-seconds-playStart/30;the double-start playback offset is preserved',
            'Release8D8340 releases camera/resources/owner/flags but doesnot zero loaded/play/pause scalar',
            'Camera events bind lowercased CAM names;missing names are warned and skipped;track order is retained',
            'Real engine Render empty-list branch has fog toggles and unconditional normal renderer UnSetState',
            'No-camera stock RVP resets projection/FSE during level.FrameMove;intro must share real execution order,not be protected by an inventedflag'],
        gaps=['Actual actor/Character/effect/ambient and event audio/sword-trace/screen/timer-rate providers are explicitly refused at Create and remain mandatory',
            'RVP parser independent-if argument-keyword fallthrough and full malformed/locale/numeric domains from078 remain unaccepted',
            'Full Create/release shared-effect caches/deferred particle lifecycle and Render8CE5D0 material/light cache resets are not restored',
            'Camera-only failed-load owner detachment is source safety behavior;target leaves stale owner and is not accepted in that failure domain',
            'Paused automatic-camera unset-matrix scratch is explicitly unaccepted;no substitute matrix is claimed equivalent',
            'Legacy inverted movie-request callers and full Tutorial/Avatar/QBI/follow/fourstage/auth/gameplay/lifecycle/numeric/IME/M6F/M7/M9 remain open'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-rvp-runtime-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:20 equal455ranges;531+23+14+114 full asm;Render/Release identities corrected;full player remains OPEN')


if __name__=='__main__':main()
