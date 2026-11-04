"""Pin actual client clock callers; console commands are not network messages."""
import hashlib,json,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));evidence=[];baseline=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        data=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes();digest=hashlib.sha256(data).hexdigest()
        if digest!=target[key]['sha256']:raise ValueError('Time caller reference changed')
        functions=[];bodies=[]
        for name,va,size in [('console_command',0x7e3b10,0x515),('client_map_load',0x7c8b60,0x368),('set_real_hms',0x8b14a0,0x93)]:
            body=read_va(data,va,size);bodies.append(body);functions.append({'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':hashlib.sha256(body).hexdigest()})
        if baseline is not None and baseline!=bodies:raise ValueError('Time caller bodies differ between pins')
        baseline=bodies;calls=[]
        for va,dest,meaning in [(0x7e3e55,0x8b12e0,'console %time hours,0,0'),(0x7e3f3a,0x8b14a0,'console %real_time hours,minutes,0'),(0x7c8de3,0x8b12d0,'client map load queries simulation rate'),(0x7c8e4d,0x8b1440,'client map load sets simulation fraction'),(0x7c8e87,0x8b15d0,'client map load sets real-time fraction')]:
            wanted=b'\xe8'+struct.pack('<i',dest-va-5)
            if read_va(data,va,5)!=wanted:raise ValueError('Time caller instruction changed')
            calls.append({'va':hex(va),'rva':hex(va-0x400000),'destination_va':hex(dest),'destination_rva':hex(dest-0x400000),'bytes':wanted.hex(),'meaning':meaning})
        for va,text in [(0xaeddf0,b'%time\0'),(0xaedde4,b'%real_time\0')]:
            if read_va(data,va,len(text))!=text:raise ValueError('Console clock command changed')
        evidence.append({'input':folder,'sha256':digest,'architecture':'x86','image_base':'0x400000','functions':functions,'calls':calls})
    report={'binary_evidence':evidence,'confirmed':['0x7E3E55 is the console %time command, not a network handler. Its only direct HMS setter xref was checked in IDA.',
        '0x7C8B60 loads client map and then initializes both clocks from cached fields, elapsed GetTickCount and the simulation rate.',
        'Map-load arithmetic adds elapsed_seconds%60 to seconds and (elapsed_seconds/60)%60 to minutes; no additional hour carry is present in that fragment.',
        'Console %real_time invokes a separate unaccelerated HMS setter; that setter/command is not yet source-integrated.'],
        'unknown':['Network origin/layout/update rules for the cached map time fields','Complete client CLand clock/caller restoration and date/weather fields','Full lighting/sky integration and both console command paths'],
        'raw_analysis':'artifacts/clock455-analysis; cached IDA database used. Input executables never executed.'}
    (WS/'inventory/client455-time-callers.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:3time caller functions/5call sites and2console strings match both pinned455PE.')

if __name__=='__main__':main()
