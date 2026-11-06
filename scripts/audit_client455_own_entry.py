"""Find own startup checkpoints from decoded instructions and current link symbols.

No fixed WinMain offsets: edits may change prologue/branches/call placement.
Only the linked OWN executable is disassembled, never executed here.
"""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def symbol(mapping,name):
    matches=re.findall(r'^\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+('+re.escape(name)+r')\s+([0-9a-fA-F]{8})\b',mapping,re.M)
    if len(matches)!=1:raise ValueError('Expected one own symbol:'+name)
    return int(matches[0][1],16)

def main():
    link=json.loads((WS/'inventory/client455-normal-link.json').read_text());validate_normal_link(link)
    exe=WS/link['executable']['file'];raw=exe.read_bytes();base=pe(raw)['image_base'];mapping=(WS/link['map']['file']).read_text()
    info=json.loads((WS/'inventory/msvc-verification.json').read_text());dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    names={'main':'_WinMain@16','sound':'?InitR3SoundSystem@@YAHPAD@Z','d3d':'?InitR3D3D@R3D3dWrapper@@QAEJPAUHINSTANCE__@@K@Z','create':'?Create@CMainApp@@QAEHXZ','char_data':'?_CreateCharDataMgr@@YAHXZ'}
    addresses={key:symbol(mapping,name) for key,name in names.items()};art=WS/'artifacts/client455-startup';art.mkdir(parents=True,exist_ok=True);decoded={};files=[]
    for key in ['main','create']:
        begin=addresses[key];result=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{begin+0x500:x}',str(exe)],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:raise ValueError('Own disassembly failed:'+result.stderr.decode(errors='replace'))
        path=art/f'own-{key}-disassembly.txt';path.write_bytes(result.stdout);files.append({'file':path.relative_to(WS).as_posix(),'sha256':sha(path)})
        rows=[]
        for line in result.stdout.decode(errors='replace').splitlines():
            match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
            if match:
                at=int(match[1],16);data=bytes.fromhex(match[2]);mnemonic=match[3];operand=match[4]
                if data!=read_va(raw,at,len(data)):raise ValueError('Disassembly bytes differ from own PE')
                rows.append((at,data,mnemonic,operand))
        if not rows or rows[0][0]!=begin:raise ValueError('Own function entry was not decoded')
        decoded[key]=rows
    points={}
    for label,owner,target,after in [('after_sound','main','sound',True),('after_d3d','main','d3d',True),('before_char_data','create','char_data',False)]:
        calls=[row for row in decoded[owner] if row[2]=='call' and len(row[1])==5 and row[1][0]==0xe8 and row[0]+5+struct.unpack('<i',row[1][1:])[0]==addresses[target]]
        if len(calls)!=1:raise ValueError('Expected one decoded CALL:'+label)
        call=calls[0];at=call[0]+5 if after else call[0]
        row=next((row for row in decoded[owner] if row[0]==at),None)
        if row is None:raise ValueError('Checkpoint is not a decoded instruction boundary')
        points[label]={'rva':hex(at-base),'call_rva':hex(call[0]-base),'target_rva':hex(addresses[target]-base),'bytes':len(row[1]),'sha256':hashlib.sha256(row[1]).hexdigest()}
    if not addresses['main']<base+int(points['after_sound']['rva'],16)<base+int(points['after_d3d']['rva'],16):raise ValueError('Unexpected own startup order')
    report={'scope':'Decoded instruction checkpoints in the exact own linked PE;not reference behavior acceptance','executable':link['executable'],'normal_link_sha256':sha(WS/'inventory/client455-normal-link.json'),'script_sha256':sha(Path(__file__)),'tool':{'file':str(dumpbin),'sha256':sha(dumpbin)},'symbols':{k:{'name':names[k],'rva':hex(v-base)} for k,v in addresses.items()},'points':points,'disassembly':files}
    (WS/'inventory/client455-own-entry.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'main':report['symbols']['main']['rva'],'points':points}))

def validated_entry():
    report=json.loads((WS/'inventory/client455-own-entry.json').read_text())
    if report['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or report['script_sha256']!=sha(Path(__file__)):raise ValueError('Stale own decoded checkpoint audit')
    raw=(WS/report['executable']['file']).read_bytes();base=pe(raw)['image_base']
    if hashlib.sha256(raw).hexdigest()!=report['executable']['sha256']:raise ValueError('Changed own PE')
    for row in report['points'].values():
        if hashlib.sha256(read_va(raw,base+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed own decoded instruction')
        call=read_va(raw,base+int(row['call_rva'],16),5)
        if call[0]!=0xe8 or int(row['call_rva'],16)+5+struct.unpack('<i',call[1:])[0]!=int(row['target_rva'],16):raise ValueError('Changed own CALL target')
    return report

if __name__=='__main__':main()
