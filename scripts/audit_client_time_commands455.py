"""Pin text input, access gate and local clock-command contracts in both455PE."""
import hashlib,json,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));evidence=[];baseline=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest!=target[key]['sha256']:raise ValueError('Time command reference changed')
        bodies=[];functions=[]
        for name,va,size in [('input_send',0x433050,0x13c),('privileged_commands',0x4335a0,0x8b3),('local_parser',0x7e3b10,0x515),
                ('grade_getter',0x40a690,0x1c),('empty_input',0x432600,0x3b),('clear_prefix',0x432640,0x4e),('save_history',0x432690,0x1c1),
                ('atol_wrapper',0x874f6a,0x11),('strtol_wrapper',0x8754fe,0x29)]:
            body=read_va(data,va,size);bodies.append(body);functions.append({'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':hashlib.sha256(body).hexdigest()})
        if baseline is not None and bodies!=baseline:raise ValueError('Time command functions differ between pins')
        baseline=bodies;sites=[]
        for va,dest,meaning in [(0x433091,0x40a690,'query client grade'),(0x4330a2,0x4335a0,'call privileged text path'),(0x4330b5,0x432640,'clear consumed command prefix'),(0x4330ca,0x432690,'save original consumed command'),(0x4335bd,0x7e3b10,'try local parser before fallback'),(0x7e3e55,0x8b12e0,'set game HMS'),(0x7e3f3a,0x8b14a0,'set real HMS'),(0x874f72,0x8754fe,'atol uses strtol')]:
            wanted=b'\xe8'+struct.pack('<i',dest-va-5)
            if read_va(data,va,5)!=wanted:raise ValueError('Time command call changed:'+hex(va))
            sites.append({'va':hex(va),'rva':hex(va-0x400000),'destination_va':hex(dest),'bytes':wanted.hex(),'meaning':meaning})
        if read_va(data,0x433096,5)!=bytes.fromhex('83f8017c41'):raise ValueError('Grade>=1 gate changed')
        if read_va(data,0xaa8dd4,1)!=b'\0':raise ValueError('Consumed command prefix is not empty')
        if read_va(data,0x874f6a,4)!=bytes.fromhex('6a0a6a00'):raise ValueError('strtol radix/end-pointer changed')
        evidence.append({'input':folder,'sha256':digest,'architecture':'x86','image_base':'0x400000','functions':functions,'calls':sites,'grade_gate':{'va':'0x433096','rva':'0x33096','bytes':'83f8017c41','meaning':'signed grade>=1 before local command path'}})
    report={'binary_evidence':evidence,'confirmed':['Source is copied up to256bytes,byte256 terminated,then lowercased;input is not mutated','Cursor advances by token strlen without skipping leading whitespace;real minutes uses first argument strlen+1','Time uses hours,0,0;real_time hours,minutes,0;raw unsigned HMS wrapping follows signed32 strtol conversion','Other recognized directives/end terminate this local parser before later time tokens','The input grade>=1 gate precedes local parser;consumed command clears prefix and saves original text'],
            'unknown':['Complete other local directives and privileged/network fallback','Full modern/old CRT locale/non-ASCII and strtol/sscanf domain','Complete CHAT_INFO/chat histories/UI transport equivalence;selected time path only'],
            'raw_analysis':'artifacts/clock455-analysis/command-*.json;owned IDA1bf47ee9 closed/save;input EXEs never executed'}
    (WS/'inventory/client455-time-command-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:9input/command/CRT functions,8calls and grade>=1/prefix/decimal gates match both pinned455PE.')

if __name__=='__main__':main()
