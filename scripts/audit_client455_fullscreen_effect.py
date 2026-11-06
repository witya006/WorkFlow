"""Pin the ordinary455 fullscreen motion branch,including its final opaque pass."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    evidence=WS/'artifacts/client455-progress/fullscreen076.json';body=json.loads(evidence.read_text());target=json.loads((WS/'config/client-target.json').read_text());pins=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=target[key]['sha256'] or pe(raw)['architecture']!='x86':raise ValueError('Changed455pin')
        ranges=[]
        for row in body['ranges']['result']:
            if row['error']:raise ValueError('Missing fullscreen function')
            addr,size=int(row['fn']['addr'],16),int(row['fn']['size'],16);ranges.append({'rva':hex(addr-0x400000),'bytes':size,'sha256':hashlib.sha256(read_va(raw,addr,size)).hexdigest()})
        density=read_va(raw,0xbf7850,4);record={'rva':'0x7f7850','bytes':4,'sha256':hashlib.sha256(density).hexdigest(),'value':struct.unpack('<f',density)[0]}
        if record['value']!=0.25:raise ValueError('Unexpected default density')
        if pins and (ranges!=pins[0]['ranges'] or record!=pins[0]['default_density']):raise ValueError('Fullscreen455pins differ')
        pins.append({'sha256':sha(path),'architecture':'x86','image_base':'0x400000','ranges':ranges,'default_density':record})
    assemblies=[]
    for key in ['effectAsm','setterAsm','modeAsm','beginAsm']:assemblies+=list(assembly_rows([body[key]]))
    report={'scope':'Actual455 ordinary fullscreen motion branch/density/BeginScene result;not completepostprocessing or Tutorial owner','references':pins,'raw_evidence':{'file':evidence.relative_to(WS).as_posix(),'sha256':sha(evidence)},'assemblies':assemblies,'script_sha256':sha(Path(__file__)),
        'facts':['8CED70 stores fullDWORD mode and resets previous-mode cache only when mode0','8CE9D0 stores float unchanged;defaultBF7850=0.25;Tutorial uses0.15 andrestores0.25','8CD9F4 selects512 independently oflegacyvideo-memory level','8CDB80 returns actualtexture BeginScene success when effectrequested;unloaded target returns0','8CE9F0 Ends main, Begins blur;motion modechange draws main opaque andclears CURRENTblur target','Everymotion frame draws main with truncated density*255 alpha,clears CURRENTblur target,draws main opaque;this final pass must notbe replaced withtemporalaccumulation','Composite restores actualframebuffer/depth/viewport,temporarilyclearsrequestmode forBeginScene,restores fullDWORDmode and ZENABLEafterfullscreenquad','OrdinaryMainGame renderer alreadycalls FullScreenEffect;sourceprovider is naturallyretained,notforce-linked'],
        'gaps':['Water/bloom/extra455targets andcompleteInit/restore/reset/lifecycle/numericfailure domains remainunaccepted;legacyshadow allocation isnot claimed455-equivalent','Stagecamera control8D4C30/follow/QBI/Avataractor/fullCGP_Tutorial/fourstage stillopen','GPUchecks are owncode andstatic455contracts,not reference-runtime pixelparity;densitydraw verified onlyfinite0..1','AllpreviousILevel/Empty/INS/Character/render/gameplay/auth/IME/M6F/M7/M9 gaps remain'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-fullscreen-effect-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'ranges':len(ranges),'full_assemblies':len(assemblies),'default_density':record['value']}))
if __name__=='__main__':main()
