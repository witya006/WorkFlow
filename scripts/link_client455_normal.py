"""Attempt the REAL normal client link and record unresolved455contracts.

Never /FORCE unresolved symbols and never link the legacy Character archive.
This command does not launch its output, even if the link eventually succeeds.
"""
import ctypes,hashlib,json,re,subprocess
from pathlib import Path
from compare_client_binaries import WS,pe

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root=WS/'work/client455-port/normal';art=WS/'artifacts/client455-normal';build=json.loads((WS/'inventory/client455-normal-build.json').read_text());proof=json.loads((WS/'inventory/client455-normal-consumers.json').read_text());info=json.loads((WS/'inventory/msvc-verification.json').read_text())
    if build['build_exit'] or build['objects']!=182 or proof['normal_build_sha256']!=sha(WS/'inventory/client455-normal-build.json'):raise ValueError('Current normal consumers required')
    libraries=[WS/r['file'] for r in proof['libraries']]
    for name in ['client455-effect-log']:
        report=json.loads((WS/f'inventory/{name}.json').read_text());libraries.append(WS/report['library'])
    imported=json.loads((WS/'inventory/recovered-import-libraries.json').read_text())['libraries']
    for row in imported:
        if sha(WS/row['library'])!=row['library_sha256']:raise ValueError('Changed import library:'+row['dll'])
        libraries.append(WS/row['library'])
    objects=sorted((root/'build/RFClient455Consumers.dir/Release').glob('*.obj'));engine=WS/'work/client455-port/source/R3Engine';client=root/'source';exe=root/'build/RF_Online.bin'
    # These old autolink hints must not select reference libraries. All actual
    # dependencies are explicit here; missing symbols still fail normally.
    suppressed=['CharacterR.lib','CharacterMD.lib','R3EngineMT.lib','R3EngineDMT.lib','ziplibm.lib','ZipArchive_STL_M.lib','libci.lib','JpegLibMT.lib']
    system=['d3d9.lib','dinput8.lib','dxguid.lib','winmm.lib','ws2_32.lib','vfw32.lib','advapi32.lib','gdi32.lib','user32.lib','imm32.lib','comdlg32.lib','delayimp.lib','dsound.lib','wininet.lib','shell32.lib','ole32.lib','oleaut32.lib','uuid.lib','strmiids.lib']
    args=['/NOLOGO','/MACHINE:X86','/SUBSYSTEM:WINDOWS','/OPT:REF','/OUT:'+str(exe),'/MAP:'+str(exe.with_suffix('.map'))]
    args+=['/NODEFAULTLIB:'+name for name in suppressed]+['/LIBPATH:'+str(p) for p in [engine,WS/'work/client-build/recovered-imports',WS/'work/client455-port/source/RF_Client',WS/'work/client455-port/source/RF_Client/lib',WS/'work/client455-port/dependencies']]
    args+=['/DELAYLOAD:'+name for name in ['mss32.dll','ABuse.dll','Adv.dll','PDLL.dll']]
    args+=[str(p) for p in objects+libraries]+system
    response=root/'generated/normal-link.rsp';response.write_text('\n'.join('"'+arg+'"' for arg in args)+'\n',encoding='ascii');batch=root/'generated/link-normal.cmd';log=art/'normal-link.txt';dev=Path(info['installation_path'])/'Common7/Tools/VsDevCmd.bat'
    batch.write_text(f'@echo off\ncall "{dev}" -no_logo -arch=x86 -host_arch=x64 > env-link.txt 2>&1\nif errorlevel 1 exit /b 1\nlink @"{response}" > "{log}" 2>&1\nexit /b %errorlevel%\n',encoding='ascii')
    result=subprocess.run(['cmd.exe','/d','/c',str(batch)],cwd=response.parent,creationflags=subprocess.CREATE_NO_WINDOW)
    data=log.read_bytes();text=data.decode('cp866',errors='replace');unresolved=[];other=[]
    undecorate=ctypes.WinDLL('Dbghelp.dll').UnDecorateSymbolName;undecorate.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_uint32,ctypes.c_uint32];undecorate.restype=ctypes.c_uint32
    for line in text.splitlines():
        if 'error LNK' not in line:continue
        code=re.search(r'error (LNK\d+)',line)[1]
        if code in ['LNK2001','LNK2019']:
            match=re.search(r'\((\?[^\s()]+|_+[^\s()]+)\)',line)
            if not match:raise ValueError('Unparsed linker symbol:'+line)
            symbol=match[1];out=ctypes.create_string_buffer(8192);ok=undecorate(symbol.encode(),out,len(out),0)
            unresolved.append({'symbol':symbol,'declaration':out.value.decode('ascii') if ok else symbol,'object':line.split(' : ',1)[0],'code':code})
        elif code!='LNK1120':other.append({'code':code,'line':line})
    grouped={}
    for row in unresolved:
        group=grouped.setdefault(row['symbol'],{'symbol':row['symbol'],'declaration':row['declaration'],'objects':[]})
        if row['object'] not in group['objects']:group['objects'].append(row['object'])
    report={'scope':'Real normal455RF_Online link diagnostic,not runtime/acceptance','link_exit':result.returncode,'client_objects':len(objects),'unique_unresolved':len(grouped),'unresolved':list(grouped.values()),'other_errors':other,'log':log.relative_to(WS).as_posix(),'log_sha256':sha(log),'normal_build_sha256':sha(WS/'inventory/client455-normal-build.json'),'libraries':[{'file':p.relative_to(WS).as_posix(),'sha256':sha(p)} for p in libraries],'legacy_character_linked':False,'unresolved_forced':False,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M9':'OPEN'}
    if not result.returncode:
        raw=exe.read_bytes();image=pe(raw);mapping=exe.with_suffix('.map');maptext=mapping.read_text(errors='replace')
        if grouped or other or 'CharacterMR' in maptext:raise ValueError('Unexpected successful link evidence')
        report['executable']={'file':exe.relative_to(WS).as_posix(),'sha256':sha(exe),'bytes':len(raw),'architecture':image['architecture'],'image_base':hex(image['image_base']),'entry_rva':hex(image['entry_rva']),'sections':[row['name'] for row in image['sections']]}
        report['map']={'file':mapping.relative_to(WS).as_posix(),'sha256':sha(mapping)}
        report['link_response']={'file':response.relative_to(WS).as_posix(),'sha256':sha(response)}
    (WS/'inventory/client455-normal-link.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'link_exit':result.returncode,'unique_unresolved':len(grouped),'other_errors':other},ensure_ascii=False));print('\n'.join(r['declaration'] for r in list(grouped.values())[:40]))
    if result.returncode:raise SystemExit(result.returncode)
if __name__=='__main__':main()
