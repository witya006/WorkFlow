"""Verify the actual linked455clock and its default GetTickCount provider."""
import argparse,hashlib,json,re,struct
from compare_client_binaries import WS,pe
from build_client455_clock import FUNCTIONS,sha
from build_client455_x87_math import read_va

def main():
    cli=argparse.ArgumentParser();cli.add_argument('--lab',action='store_true');args=cli.parse_args()
    mode='lab' if args.lab else 'normal';folder='build-helper-lab' if args.lab else 'build-character-diagnostic'
    build=WS/'work/client-build'/folder
    result=json.loads((WS/('inventory/client-helper-lab-build.json' if args.lab else 'inventory/client-character-diagnostic.json')).read_text(encoding='utf-8'))
    if result['build_exit'] or result['build_settings'].get('RF_CLIENT_455_CLOCK')!='ON':raise ValueError('Successful clock-enabled client required')
    proof=json.loads((WS/'inventory/client455-clock.json').read_text(encoding='utf-8'))
    for name,digest in proof['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Clock component source proof stale')
    data=(build/'Release/RF_Online.bin').read_bytes();mapping=(build/'RF_Online-Release.map').read_text(encoding='ascii',errors='replace')
    symbols={m[1]:int(m[2],16) for line in mapping.splitlines() if (m:=re.match(r'\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{8})\s',line))}
    reference=(WS/'work/client-reference/current/RF_Online.bin').read_bytes()
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'))
    if hashlib.sha256(reference).hexdigest()!=target['behavior_reference']['sha256']:raise ValueError('Clock reference changed')
    for name,ref_va,size in [('_RF455_SecondsPerDay',0xae8e90,8),('_RF455_MillisecondsPerSecond',0xaa9890,8),('_RF455_UInt32Bias',0xb369b0,4),('_RF455_DayRate',0xbf7348,4)]:
        if read_va(data,symbols[name],size)!=read_va(reference,ref_va,size):raise ValueError('Linked clock constant changed')
    needed={name for name,_,_ in FUNCTIONS} if args.lab else {'_RF455_GetDayFraction','_RF455_AdvanceDayClock'}
    functions=[]
    for (name,va,size),record in zip(FUNCTIONS,proof['binary_evidence'][0]['functions']):
        if name not in symbols:
            if name in needed:raise ValueError('Required clock function missing:'+name)
            continue
        expected=bytearray(read_va(reference,va,size))
        for reloc in record['relocations']:struct.pack_into('<I',expected,reloc['offset'],symbols[reloc['symbol']])
        actual=read_va(data,symbols[name],size)
        if actual!=expected:raise ValueError('Linked clock instructions differ:'+name)
        functions.append({'symbol':name,'va':hex(symbols[name]),'rva':hex(symbols[name]-0x400000),'reference_va':hex(va),'reference_rva':hex(va-0x400000),'size':size,'sha256':hashlib.sha256(actual).hexdigest(),'identity_except_verified_absolute_operands':True,'prefix_only':name=='_RF455_AdvanceDayClock'})
    # MSVC initializes a pointer to a dllimport function through .CRT$XCU:
    # mov eax,[GetTickCount IAT]; mov [ClockTickSource],eax; ret. Verify the
    # actual initializer and its registration, rather than expecting a nonzero
    # file-backed value in the pointer's zero-initialized storage.
    slot=symbols['__imp__GetTickCount@0'];provider=symbols['??__ERF455_ClockTickSource@@YAXXZ']
    initializer=symbols['?RF455_ClockTickSource$initializer$@@3P6AXXZA']
    expected=b'\xa1'+struct.pack('<I',slot)+b'\xa3'+struct.pack('<I',symbols['_RF455_ClockTickSource'])+b'\xc3'
    if read_va(data,provider,len(expected))!=expected:raise ValueError('Clock provider initializer changed')
    if read_va(data,initializer,4)!=struct.pack('<I',provider):raise ValueError('Clock .CRT$XCU registration changed')
    if pe(data)['image_base']!=0x400000:raise ValueError('Unexpected clock image base')
    header=struct.unpack_from('<I',data,0x3c)[0]
    import_rva,_=struct.unpack_from('<II',data,header+24+96+8);descriptor=0x400000+import_rva
    resolved=None
    while True:
        original,stamp,chain,module,first=struct.unpack('<IIIII',read_va(data,descriptor,20))
        if not (original or module or first):break
        for index in range(8192):
            name_at=struct.unpack('<I',read_va(data,0x400000+(original or first)+index*4,4))[0]
            if not name_at:break
            if 0x400000+first+index*4==slot and not name_at&0x80000000:
                name=read_va(data,0x400000+name_at+2,64).split(b'\0')[0]
                dll=read_va(data,0x400000+module,64).split(b'\0')[0]
                if name==b'GetTickCount':resolved=dll.decode('ascii')
        else:raise ValueError('Unterminated import thunks')
        descriptor+=20
    if resolved is None or resolved.lower()!='kernel32.dll':raise ValueError('Clock provider must resolve to KERNEL32.GetTickCount')
    path=WS/'inventory/client455-clock-link.json';all_results=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    all_results[mode]={'exe':(build/'Release/RF_Online.bin').relative_to(WS).as_posix(),'exe_sha256':hashlib.sha256(data).hexdigest(),'architecture':'x86','image_base':'0x400000','functions':functions,'default_provider':{'initializer_va':hex(provider),'initializer_rva':hex(provider-0x400000),'registration_va':hex(initializer),'module':resolved,'name':'GetTickCount'},'component_report_sha256':sha(WS/'inventory/client455-clock.json'),'source_sha256':proof['source_sha256'],'executed':False,'scope':'Selected linked routines; absent unused functions may be discarded by normal linker. Caller integration and full lighting remain separate.'}
    path.write_text(json.dumps(all_results,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:{mode} linked clock {len(functions)}routines/prefix;system GetTickCount provider and constants verified.')

if __name__=='__main__':main()
