"""Pin the real Tutorial camera cuts; do not interpret record labels as camera IDs."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_camera import camera_layout
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    raw_path=WS/'artifacts/client455-progress/intro075.json';evidence=json.loads(raw_path.read_text());pins=json.loads((WS/'config/client-target.json').read_text());references=[];tables=[]
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=pins[key]['sha256'] or pe(raw)['architecture']!='x86':raise ValueError('Changed455pin')
        ranges=[]
        for row in evidence['allRanges']['result']:
            if row['error']:raise ValueError('Missing intro function')
            addr,size=int(row['fn']['addr'],16),int(row['fn']['size'],16);ranges.append({'rva':hex(addr-0x400000),'bytes':size,'sha256':hashlib.sha256(read_va(raw,addr,size)).hexdigest()})
        regions=[];current=[]
        for race,addr in [('bellato',0xbd18c8),('cora',0xbd1938),('accretia',0xbd19b0)]:
            camera=client/f'Map/{race}/{race}.cam';layout=camera_layout(camera.read_bytes());count=layout['camera_count'];data=read_va(raw,addr,count*12)
            regions.append({'rva':hex(addr-0x400000),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            segments=[{'label':label,'start':start,'end':end} for label,start,end in struct.iter_unpack('<III',data)]
            if any(row['start']>row['end'] or row['end']>layout['end'] or row['end']<70 for row in segments):raise ValueError('Unexpected real Tutorial interval')
            current.append({'race':race,'count':count,'segments':segments,'camera':{'file':str(camera),'sha256':sha(camera),'bytes':camera.stat().st_size,'end':layout['end']}})
        if tables and current!=tables:raise ValueError('455intro tables differ')
        tables=current
        if references and (ranges!=references[0]['ranges'] or regions!=references[0]['tables']):raise ValueError('455intro ranges differ')
        references.append({'sha256':sha(path),'architecture':'x86','image_base':'0x400000','ranges':ranges,'tables':regions})
    output=WS/'artifacts/client455-tutorial-intro/tables.h';output.parent.mkdir(parents=True,exist_ok=True)
    text='// Generated from both pinned455 binaries by audit_client455_tutorial_intro.py.\n'
    for table in tables:
        text+='static const RF455TutorialIntroSegment '+table['race']+'Segments[]={\n'+''.join('    {'+','.join(str(row[k])+'u' for k in ['label','start','end'])+'},\n' for row in table['segments'])+'};\n'
    output.write_text(text,encoding='ascii')
    assemblies=[]
    for key in ['cameraAssembly','loadAssembly','fadeInAssembly','fadeOutAssembly']:assemblies+=list(assembly_rows([evidence[key]]))
    report={'scope':'Actual455 Tutorial intro tables and camera/fade/input sequencing;whole stage remains open','references':references,'tables':tables,'raw_evidence':{'file':raw_path.relative_to(WS).as_posix(),'sha256':sha(raw_path)},'assemblies':assemblies,'generated':{'file':output.relative_to(WS).as_posix(),'sha256':sha(output)},'script_sha256':sha(Path(__file__)),
        'facts':['5594D0 chooses raceBYTE/2 and starts camera0 with table start/end and final-stop1','5590B0 chooses subsequent cameras by segment ordinal;record label is unused even when it differs','Fade threshold is signed32(end-70),compared with double(nowSeconds)*30;pending increments once','Next segment waits for IsFading==FALSE,not IsFadeOut;then fadein3s and SetPrePlayCamera(ordinal,start,end,1)','Global skip is consumed at end of intro branch,sets ordinalFFFF;finish occurs on following tick','Finish fadesout0 then fadesin5,unblocks input,shows screen/mouse,starts real board script,clears intro and engine flags before follow camera in same tick','Init resets pending/index but Load does not;reload is not an implicit counter reset'],
        'gaps':['Full CGP_Tutorial lifecycle/factory,Avatar/QBI/action/localfeedback providers remain open','Engine renderflag8CED70,float8CE9D0 and camera control8D4C30 have additional455 consumers not in legacy engine;host must supply them,not a no-op','Complete follow-camera/render numeric parity,full world/effects/IME/lifecycle/M6F/M9 unaccepted'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-tutorial-intro-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'camera_counts':[r['count'] for r in tables],'assemblies':len(assemblies),'generated':str(output)}))
if __name__=='__main__':main()
