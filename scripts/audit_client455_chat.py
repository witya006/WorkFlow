"""Pin actual chat styles, country script paths and selected insertion contracts."""
import hashlib,json,shutil,struct
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS,pe

TABLES=[0xaf94ec,0xaf82b4,0xaf6c54,0xaf918c,0xaf70e4,0xaf76d4,0xaf73dc,0xaf79cc,0xaf7cc4,0xaf7fbc,0xaf88a4]


def literal(data,at):
    out=bytearray()
    while len(out)<512:
        byte=read_va(data,at+len(out),1)[0]
        if not byte:return bytes(out)
        out.append(byte)
    raise ValueError('Unterminated reference string')


def main():
    path=WS/'artifacts/client455-progress/chat109-reference.json';raw=json.loads(path.read_text());functions=[row['fn'] for row in raw['ranges']['result']]
    require(len(functions)==41 and len(raw['assembly'])==28 and sum(row['instruction_count'] for row in raw['assembly'])==2708 and all(row['cursor']['done'] for row in raw['assembly']) and all(row['cursor']['done'] for row in raw['getters']),'Complete selected coverage')
    lexer_path=WS/'artifacts/client455-progress/chat109-lexer-reference.json';lexer=json.loads(lexer_path.read_text());require(len(lexer['assembly'])==3 and sum(row['instruction_count'] for row in lexer['assembly'])==907 and all(row['cursor']['done'] for row in lexer['assembly']),'Complete byte lexer coverage');functions += [row['fn'] for row in lexer['ranges']['result']]
    pins=json.loads((WS/'config/client-target.json').read_text());refs=[];countries=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin';data=binary.read_bytes();require(sha(binary)==pins[key]['sha256'] and pe(data)['architecture']=='x86','Pinned input')
        ranges=[dict(rva=hex(int(fn['addr'],16)-0x400000),bytes=int(fn['size'],16),sha256=hashlib.sha256(read_va(data,int(fn['addr'],16),int(fn['size'],16))).hexdigest()) for fn in functions]
        more=[dict(rva=hex(at-0x400000),bytes=size,sha256=hashlib.sha256(read_va(data,at,size)).hexdigest()) for at,size in [(0xae6f40,1152),(0xae7400,1024),(0xaa8dd4,1)]]
        rows=[]
        for nation,table in enumerate(TABLES):
            path_method=struct.unpack('<I',read_va(data,table+364,4))[0];flag_method=struct.unpack('<I',read_va(data,table+240,4))[0];body=read_va(data,path_method,0x1b)
            prefix=bytes.fromhex('558bec83ec44535657894dfcb8');require(body.startswith(prefix),'Country getter opcode')
            at=struct.unpack_from('<I',body,len(prefix))[0];relative=literal(data,at).decode('ascii');flag=flag_method==0x82c9f0
            require(flag_method in [0x82c9f0,0x82ce90] and flag==(nation==2),'Country fallback19 flag')
            rows.append(dict(nation=nation,script=relative,script_literal_rva=hex(at-0x400000),getter_rva=hex(path_method-0x400000),fallback19_red=flag))
            for offset in [364,240]:more.append(dict(rva=hex(table+offset-0x400000),bytes=4,sha256=hashlib.sha256(read_va(data,table+offset,4)).hexdigest()))
            more.append(dict(rva=hex(at-0x400000),bytes=len(relative)+1,sha256=hashlib.sha256(read_va(data,at,len(relative)+1)).hexdigest()))
        refs.append(dict(sha256=sha(binary),architecture='x86',image_base='0x400000',ranges=ranges,data=more,countries=rows))
        if not countries:countries=rows
        require(rows==countries,'Country path equivalence')
    require(refs[0]['ranges']==refs[1]['ranges'] and refs[0]['data']==refs[1]['data'],'Selected byte equivalence')
    data=(WS/'work/client-reference/current/RF_Online.bin').read_bytes();labels=[read_va(data,0xae6f40+i*32,32).split(b'\0')[0].decode('ascii') for i in range(36)];keys=[read_va(data,0xae7400+i*256,256).split(b'\0')[0].decode('ascii') for i in range(4)]
    require(keys==['All','Party','Guild','System'] and len(set(labels))==36 and read_va(data,0xaa8dd4,1)==b'\0','Actual tag/key/empty literals')
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);inputs=[];missing=[];destroot=WS/'work/client455-reference-inputs/chat';destroot.mkdir(parents=True,exist_ok=True)
    for row in countries:
        original=client/row['script']
        if not original.is_file():missing.append(dict(nation=row['nation'],expected=row['script']));continue
        dest=destroot/f'nation{row["nation"]:02d}.txt';shutil.copyfile(original,dest);inputs.append(dict(nation=row['nation'],runtime_relative=row['script'],original=str(original),utf16_bom_without_decoding=dest.read_bytes()[:2] in [b'\xff\xfe',b'\xfe\xff'],**record(dest)))
    generated=WS/'work/client455-port/chat_reference_tables.h'
    generated.write_text('#pragma once\nstatic const char*const RF455_CHAT_TAGS[36]={'+','.join(json.dumps(s) for s in labels)+'};\nstatic const char*const RF455_CHAT_PATHS[11]={'+','.join(json.dumps(row['script']) for row in countries)+'};\nstatic const char*const RF455_CHAT_KEYS[4]={'+','.join(json.dumps(s) for s in keys)+'};\n',encoding='ascii')
    session=WS/'artifacts/client455-progress/chat109-session.json';state=json.loads(session.read_text());require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'Owned session cleanup')
    lexer_session=WS/'artifacts/client455-progress/chat109-lexer-session.json';state=json.loads(lexer_session.read_text());require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'Lexer session cleanup')
    report=dict(status='CONFIRMED_SELECTED',scope='Chat profile36/font16/prefix18,4pane/category14 insertion and target wrapping; full input/UI/dispatch remains open',script_sha256=sha(Path(__file__)),raw_evidence=record(path),lexer_evidence=record(lexer_path),session=record(session),lexer_session=record(lexer_session),references=refs,selected_functions=44,full_assembly_functions=31,instructions=3615,style_tags=labels,settings_keys=keys,countries=countries,inputs=inputs,missing_script_inputs=missing,generated=record(generated),
                facts=['Global font provider16 contains path,script parser andtwo36xFONT_INFO16 arrays; per-MainGame style manager owns36 prefix18 andcategory masks',
                       'Each script record is marker plus four signed colors clamped0..255 and string; both fonts get size12/style32/scale1; prefix usesWORD length/truncation15 andambient CRT _mbsnbcpy',
                       'Fallback13 writes header font twice and leaves body constructor defaults; fallback19 isred only in China,others useFFFFD0A0; fallback34 marker is empty',
                       'GameSetting ChatMode All/Party/Guild/System masks: when allzero reset All14 andotherpanes category5 plus forcedown category; DefModeOn newlyenabled bits forcepane0 on andwrites mergedmask',
                       'Insert uses36styles and14categories;style26 bypasses pane filters; firstheader removesleadingnewline only when board fragment count0,body usesadjustView1',
                       'Prefixmarker isseparate;body is sprintf("%s : %s",ID,text),prefix width reserves firstline;category8 disablesindent branch',
                       'Wrapping width is board0.width-2*marginX; targetindent count isalways0,even though it measures empty literal andcalls fillspaces. Preserve this quirk',
                       'Wrapping preserves explicitnewline/double-newline cases and uses actual text fit plus_mbsnbcat; terminal oversize glyph maydrop remainder rather thanhang'],
                gaps=['Full legacy network/chat caller/category migration,14filter controls/sideeffects/input/send/IME,exactstage singleton ordering and all chat UI remain open',
                      'Missing literal country script paths are actual input gaps;do not substitute similarly named files without evidence',
                      'Unsafe buffers/null/OOM/malformed script/sharedscratch/CRTstartup/privateABI/concurrency/lifecycle domains notfullyaccepted',
                      'C1A/CE7 common dispatch and live pending1 hover still unported; fullclient/M9 remains open'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    report['facts'].append('Byte lexer skips UTF16 BOM without decoding and ignores unfinished EOF token; actual Taiwan Csta isUTF16LE,so none of its style labels match and all36 fallback records areused')
    (WS/'inventory/client455-chat-reference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(functions=44,asm=3615,script_inputs=len(inputs),missing=missing,tags=36,full_chat=False)))


if __name__=='__main__':main()
