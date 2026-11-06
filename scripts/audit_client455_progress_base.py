"""Pin the455 stage base and preserve Tutorial dependencies for the next port."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    evidence=WS/'artifacts/client455-progress-base/reference.json';data=json.loads(evidence.read_text());pins=json.loads((WS/'config/client-target.json').read_text());references=[];previous=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        ranges=[{'rva':hex(int(row['fn']['addr'],16)-0x400000),'bytes':int(row['fn']['size'],16),'sha256':sha(read_va(raw,int(row['fn']['addr'],16),int(row['fn']['size'],16)))} for row in data['ranges']['result']]
        if previous is not None and previous!=ranges:raise ValueError('455 stagebase ranges differ')
        previous=ranges;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':ranges})
    report={'scope':'Stage base Init/Create/Destroy/loop/next/exit and existing particle reset consumer;Tutorial methods pinnedbutnotimplemented','references':references,'raw_evidence':{'file':evidence.relative_to(WS).as_posix(),'sha256':sha(evidence.read_bytes())},'script_sha256':sha(Path(__file__).read_bytes()),
        'facts':['Init clears BOOL fields4/8/12/16 and retains DWORDnext20','BaseCreate/BaseDestroy return1 without LoadData/UnloadData','Nextsetter13F6B0 writesDWORD20;getter3D1470 readsit;exitsetter13F6D0 writesBOOL4','BaseMainLoop138FF0:Input,ifexitreturn1,FrameMove,Render,particlecountreset,return0;no active-window predicate','Exit requested by FrameMove is observed on next loop,not before currentRender/reset;virtualreturn values ignored','Title constructor sets next1 afterInit','Target particle manager resets count7832 in every vector record7836;own current manager retains legacyfixed1024 capacity','Tutorial Create/FrameMove/LoadData/UnloadData include world/UI/input/Avatar/camera dependencies;they are not reducedtoMainGame aliases'],
        'gaps':['Fullfourstage factory/explicitnext transition and Avatar runtime provider;legacyfactory remains3/modulo until Tutorial is ready','FullTitle/Login/Tutorial/MainGame lifecycle/UI/actors/world/gameplay/IME/shutdown','Target dynamic particle owner/storage differsfrom existingfixed1024;only common per-typecount reset semantics verified','Ownedsource keeps MainLoop(BOOL) API;originaltarget has no such argument;source is not a raw originalABI overlay','Owned next initialFFFFFFFF differsfrom target uninitializedconstructor domain;Init retention/set/get defined domains match','Current Title input/create/lifecycle remainlegacyexcept confirmednext1;not455Title acceptance','M6F/M7/M9 and realauthentication remainopen'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-progress-base-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:18stagebase/Tutorial ranges pinned;ordinary base semantics identified;fullfourstage OPEN')
if __name__=='__main__':main()
