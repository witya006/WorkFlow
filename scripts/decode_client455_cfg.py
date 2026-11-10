"""Decode every byte of IDA CFG regions with the installed MSVC disassembler.

Input binaries are read as data,never executed. An independent IDA instruction
count and complete CFG are required;compact batch previews are not evidence.
"""
import hashlib,json,re,subprocess,sys
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va

def main():
    path=(WS/sys.argv[1]).resolve();assert path.is_relative_to((WS/'artifacts').resolve())
    raw=json.loads(path.read_text());binary_path=WS/'work/client-reference/current/RF_Online.bin';binary=binary_path.read_bytes()
    pin=json.loads((WS/'config/client-target.json').read_text())['behavior_reference']['sha256']
    assert hashlib.sha256(binary).hexdigest()==pin and pe(binary)['architecture']=='x86'
    info=json.loads((WS/'inventory/msvc-verification.json').read_text());decoder=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    profiles={int(f['addr'],16):f for row in raw['profile']['result'] for f in row.get('data',[])}
    summaries=[];raw['asm']={}
    for row in raw['ranges']['result']:
        assert row['fn'] and not row['error'];start=int(row['fn']['addr'],16)
        cfg=next(c for c in raw['cfg']['result'] if int(c['addr'],16)==start)
        assert cfg['cursor']['done'] and cfg['count']==cfg['total_blocks']
        blocks=sorted((b for b in cfg['blocks'] if b['size']>0),key=lambda b:int(b['start'],16));regions=[]
        for block in blocks:
            a,b=int(block['start'],16),int(block['end'],16)
            assert b-a==block['size']
            if regions and regions[-1][1]==a:regions[-1][1]=b
            else:regions.append([a,b])
        lines=[];records=[]
        for index,(a,b) in enumerate(regions):
            run=subprocess.run([str(decoder),'/DISASM:BYTES',f'/RANGE:0x{a:x},0x{b:x}',str(binary_path)],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
            assert run.returncode==0
            decoded=path.parent/f'{start-0x400000:x}-{index}.txt';decoded.write_bytes(run.stdout)
            records.append(dict(file=decoded.relative_to(WS).as_posix(),sha256=hashlib.sha256(run.stdout).hexdigest()))
            region=[]
            for text in run.stdout.decode(errors='replace').splitlines():
                match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',text)
                if not match:
                    #dumpbin wraps long instruction bytes after six columns.
                    #These lines continue the preceding instruction,not a
                    #new instruction or a silently skipped gap.
                    continuation=re.fullmatch(r'\s+((?:[0-9A-F]{2}\s*)+)\s*',text)
                    if continuation and region:region[-1]['bytes']+=bytes.fromhex(continuation[1]).hex()
                    continue
                address=int(match[1],16)
                if not a<=address<b:continue
                code=bytes.fromhex(match[2]);assert code==read_va(binary,address,len(code))
                region.append(dict(addr=f'{address:x}',bytes=code.hex(),instruction=match[3]+(' '+match[4] if match[4] else '')))
            cursor=a
            for insn in region:
                assert int(insn['addr'],16)==cursor,(hex(start),hex(cursor),'undecoded region byte')
                code=bytes.fromhex(insn['bytes']);assert code==read_va(binary,cursor,len(code))
                cursor+=len(bytes.fromhex(insn['bytes']))
            assert cursor==b,(hex(start),hex(cursor),hex(b),'region not completely decoded')
            lines+=region
        starts={int(i['addr'],16) for i in lines}
        assert len(starts)==len(lines)==profiles[start]['instruction_count'],(hex(start),len(lines),profiles[start])
        assert all(int(b['start'],16) in starts for b in blocks)
        assert all(any(int(b['start'],16)<=a<int(b['end'],16) for b in blocks) for a in starts)
        pages=[]
        for offset in range(0,len(lines),100):
            portion=lines[offset:offset+100];end=offset+len(portion)
            pages.append(dict(addr=row['query'],asm=dict(start_ea=hex(start),name=row['fn']['name'],lines=portion),total_instructions=len(lines),instruction_count=len(portion),cursor=dict(done=True) if end==len(lines) else dict(next=end)))
        raw['asm'][row['query']]=pages
        summaries.append(dict(rva=hex(start-0x400000),instructions=len(lines),positive_cfg_blocks=len(blocks),decoded=records))
    raw['decoder']=dict(file=str(decoder),sha256=hashlib.sha256(decoder.read_bytes()).hexdigest(),input_sha256=pin,source='MSVC dumpbin over complete native IDA CFG regions;independent native IDA instruction counts',functions=summaries)
    path.write_text(json.dumps(raw,indent=2)+'\n')
    print(json.dumps(dict(functions=len(summaries),instructions=sum(f['instructions'] for f in summaries),positive_blocks=sum(f['positive_cfg_blocks'] for f in summaries),all_region_bytes_decoded=True,IDA_counts_match=True)))
if __name__=='__main__':main()
