"""Pin RVP immediate-audio behavior, including the compiled inactive WAV branch."""
import hashlib,json
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    files=[WS/'artifacts/client455-progress'/n for n in ['audio082-initial.json','audio082-extra.json','audio082-assembly.json']]
    initial,extra,assembly=[json.loads(p.read_text()) for p in files];pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=pins[key]['sha256']:raise ValueError('Changed455 pin')
        ranges=[]
        for row in extra['ranges']['result']:
            if row['error']:raise ValueError('Missing measured function')
            address,size=int(row['fn']['addr'],16),int(row['fn']['size'],16)
            ranges.append(dict(rva=hex(address-0x400000),bytes=size,sha256=hashlib.sha256(read_va(raw,address,size)).hexdigest()))
        if references and ranges!=references[0]['ranges']:raise ValueError('Audio ranges differ between pins')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=ranges))
    full=[]
    for fn in assembly['functions']:
        lines=[line for page in fn['pages'] for line in page['asm']['lines']]
        if len(lines)!=fn['total'] or len({r['addr'] for r in lines})!=len(lines):raise ValueError('Incomplete/overlapping assembly')
        full.append(dict(rva=hex(int(fn['addr'],16)-0x400000),instructions=len(lines),pages=len(fn['pages'])))
    if initial['create0']['line_count']+extra['create500']['line_count']!=770 or not extra['create500']['cursor']['done']:raise ValueError('Incomplete Create pseudocode')
    report=dict(scope='RVP immediate-wave ownership,ambient/event route and timer_rate;not whole audio or client acceptance',references=references,assemblies=full,
        raw_evidence=[dict(file=p.relative_to(WS).as_posix(),sha256=sha(p)) for p in files],script_sha256=sha(Path(__file__)),facts=[
            '8BEEC0 owns20-byte records:flag0/handle4/memory8/loop12/typeWORD16/occupiedWORD18;initial128 capacity,grow32 at count>=capacity',
            'Load allocates table before existence test;occupied records are not cleared/reused by individual release;releaseall frees table',
            'Only uppercase MP3 extension enters8BDE00;compiled non-MP3 branch sets type0/occupied1 without loading handle or file bytes;stock RVP WAV registrations therefore cannot start via8BF070',
            'MP3 helper gates on music,reads with size,allocates/initializes actual Miles sample,uses named file and passes raw loadflag to actual loopcount;metadata is loadflag!=1',
            '8BF070 gates on init/sound/table/id/handle,multiplies global volume once and starts sample;its third caller pan argument is ignored',
            '8BDA50 volume update gates on init/table/id/handle only;passes raw volume with fixed pan0.5;no global-volume multiplication or sound-on guard',
            '8BD950 loop setter gates on sound and skips unchanged metadata;thus loadflag1 gives metadata0/actualMilesloop1 and requested0 does not change actualloop',
            '8BD9B0 stop works with sound disabled;type0 stop also ends/releases3D sample and its memory;releaseall is invoked by loaded RVP Release',
            'Ambient uses previous actor matrix before flag16 gate and camera update;positive starts once with loop0 then only volume updates;nonpositive clears latch and stops',
            'Wave tracks prefer camera dummy,otherwise search actors excluding last;execution uses current dummy matrix or saved actor matrix;Create Prepare executes twice',
            'Timer-rate command11 writes actual float time scale via8B3CB0;camera-dependent events are consumed/skipped when flag4 is active',
            'Correction081 address label:8D6900 is cache destructor,8D6870 constructor;Create8D69E0 allocates and increments refs at8D6C57'],gaps=[
            'No reference EXE runtime trace or application-output PCM capture;actual own Miles decoder/status/volume checks do not prove full audible-output equivalence',
            'Full Miles initialization/3D provider,ordinary PlayWave cache,music/streaming/device/audio lifecycle and failure/OOM/invalid-ID parity remain open',
            'RVP source load-model defers resource side effects until after parse;repeated properties/scanner fallthrough and malformed filename/extension domains unaccepted',
            'Attenuation/pan selected boundaries verified;full x87 FP modes/nonfinite/singular/numeric/locale domains remain open',
            'Magic/throw/collision/shadow/trace/screen and advancedFX/globalChef/material-lightreset,fullTutorial/Avatar/QBI/fourstage/Login/auth/gameplay/IME and all prior gaps remain'],input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-rvp-audio-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(equal_ranges=len(references[0]['ranges']),full_assembly_instructions=sum(r['instructions'] for r in full),full_Create_decompile_lines=770,M9='OPEN')))
if __name__=='__main__':main()
