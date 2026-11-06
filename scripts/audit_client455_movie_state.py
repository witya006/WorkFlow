"""Pin455 positive movie flags,letterbox/logo,current/default FOV and clear path."""
import hashlib,json
from pathlib import Path
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    evidence=WS/'artifacts/client455-progress/movie-state077.json';body=json.loads(evidence.read_text());target=json.loads((WS/'config/client-target.json').read_text());pins=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=target[key]['sha256'] or pe(raw)['architecture']!='x86':raise ValueError('Changed455pin')
        ranges=[]
        for row in body['ranges']['result']:
            if row['error']:raise ValueError('Missing movie-state function')
            addr,size=int(row['fn']['addr'],16),int(row['fn']['size'],16);ranges.append({'rva':hex(addr-0x400000),'bytes':size,'sha256':hashlib.sha256(read_va(raw,addr,size)).hexdigest()})
        if pins and ranges!=pins[0]['ranges']:raise ValueError('455movie-state ranges differ')
        pins.append({'sha256':sha(path),'architecture':'x86','image_base':'0x400000','ranges':ranges})
    assemblies=[]
    for key in ['stateAsm','fadeAsm','clearAsm','resetAsm']:assemblies+=list(assembly_rows([body[key]]))
    report={'scope':'Real455 positive RTMovie display flags/defaultFOV and intro binding;fullRVPplayer/stage stillopen','references':pins,'raw_evidence':{'file':evidence.relative_to(WS).as_posix(),'sha256':sha(evidence)},'assemblies':assemblies,'script_sha256':sha(Path(__file__)),
        'facts':['8D4C30 is RTMovie state,not generic camera-control state:positivewide1/logo2/no-camera4','Setter stores complete request11641C4,updates only internal low3bits11641B4,preserves previous upperbits;getter returns INTERNAL flags','8D4CB0/CC0 raw add/remove flags without synchronizing wide/logo booleans or resetting projection','wide flag writes1157CCC andisconsumed by DrawFadeScreen8B4B10 before fade-zero early return;logo flag1157CD0 feeds DrawLogo8CD960','Letterbox imageheight=int(double(float0.55)*screenwidth);integerborder=(screenheight-imageheight)/2,rectangles before fade andlogo','8CDB20 clear hasno legacywide viewport mutation;ordinary/mainFSEtarget paths covered,extra455targets remainopen','8C3400 andMainApp7D18B0 initialize/reset separatedefault/currentFOV0.6;8C43D0 readsdefault1157C90,not animatedcurrent1157C94','R3Engine legacy RTMovie player is compiled out in this configuration;actualstate/display APIs restoredoutside featureguard,not declared a working RVPplayer','Legacy0.7 RTMovieSetState/GetState inverted-request API remains explicitly separate;455intro usesnewpositive API'],
        'gaps':['Actual RVP player/track/actor/audio/RTMovieFrameMove consumer reconstruction remains mandatory;shared state doesnot restorethe player','455 percent-fov command7E3B10 writer identified butunported;fullprojection/numeric/failure/reset domains unaccepted','CGP_Tutorial owner/Avataractor/QBI/follow/fourstage/Login andallpriorCharacter/world/render/auth/IME/M6F/M7/M9gaps remain','Legacy0.7 movie-request callers not certified455semantics;explicit wrapper preserved untiltheir jointmigration'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-movie-state-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'ranges':len(ranges),'full_assemblies':len(assemblies)}))
if __name__=='__main__':main()
