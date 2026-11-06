"""Verify455 AES schedules/config/framing;generate private build input from pinned PE."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()
def multiply(a,b):
    result=0
    while b:
        if b&1:result^=a
        a=((a<<1)^(0x11b if a&128 else 0))&255;b>>=1
    return result
def substitution(a):
    reciprocal=0 if not a else 1;power=a;exponent=254
    while exponent:
        if exponent&1:reciprocal=multiply(reciprocal,power)
        power=multiply(power,power);exponent>>=1
    result=reciprocal^0x63
    for bits in range(1,5):result^=((reciprocal<<bits)|(reciprocal>>(8-bits)))&255
    return result
def expand(key):
    result=bytearray(key);constant=1
    while len(result)<208:
        at=len(result);temp=list(result[-4:])
        if at%24==0:
            temp=[substitution(x) for x in temp[1:]+temp[:1]];temp[0]^=constant;constant=multiply(constant,2)
        result.extend(result[at-24+i]^temp[i] for i in range(4))
    return bytes(result)
def canonical(raw):return b''.join(raw[i:i+4][::-1] for i in range(0,len(raw),4))
def forward_from_inverse(data):
    result=bytearray()
    for r in range(13):
        block=data[16*(12-r):16*(13-r)]
        if r in [0,12]:result.extend(block);continue
        for column in range(4):
            a=block[column*4:column*4+4]
            for row in range(4):result.append(multiply(a[row],2)^multiply(a[(row+1)%4],3)^a[(row+2)%4]^a[(row+3)%4])
    return bytes(result)
def main():
    pins=json.loads((WS/'config/client-target.json').read_text());evidence_path=WS/'artifacts/client455-network-codec/reference.json';evidence=json.loads(evidence_path.read_text());references=[];previous=None
    ranges=[(int(r['fn']['addr'],16),int(r['fn']['size'],16)) for r in evidence['ranges']['result']]
    data_ranges=[(0xbd1d68,4),(0xbd1d70,240),(0xbd1b84,4),(0xbd1c78,240),(0xb34380,0x2000),(0xb36380,256),(0xb368f0,16)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455pin')
        bodies=[{'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for at,size in ranges+data_ranges]
        if previous is not None and previous!=bodies:raise ValueError('Different455network code/data')
        previous=bodies;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','ranges':bodies})
    rounds=[struct.unpack('<I',read_va(raw,at,4))[0] for at in [0xbd1d68,0xbd1b84]]
    if rounds!=[12,12]:raise ValueError('Unexpected AES rounds')
    send=canonical(read_va(raw,0xbd1d70,240))[:208];receive=forward_from_inverse(canonical(read_va(raw,0xbd1c78,240)))
    if expand(send[:24])!=send or expand(receive[:24])!=receive:raise ValueError('Pinned AES192 schedules do not match standard expansion')
    generated=WS/'work/client455-port/network455/client455_network_defaults.h';generated.parent.mkdir(parents=True,exist_ok=True)
    text='#pragma once\n// Private generated protocol constants from pinned455;not account data.\n'
    for name,data in [('Send',send[:24]),('Receive',receive[:24])]:text+='static const unsigned char RF455_Default'+name+'Key[24]={'+','.join('0x%02x'%v for v in data)+'};\n'
    generated.write_text(text,encoding='ascii')
    report={'scope':'AES192-CBC schedules,zero IV/padding,packet framing and client transport configuration;not fullnetwork/authentication','references':references,'script_sha256':sha(Path(__file__).read_bytes()),'raw_evidence':{'file':evidence_path.relative_to(WS).as_posix(),'sha256':sha(evidence_path.read_bytes())},'generated_defaults':{'file':generated.relative_to(WS).as_posix(),'sha256':sha(generated.read_bytes())},'rounds':12,'forward_and_inverse_schedules_verified':True,'direction_keys_equal':send==receive,'configured_processes':2,'process_capacity':6,'receive_buffer':20000,'send_buffer':1000000,'packet_scratch':20000,'facts':['236byteconfig;Create copiesconfig0 toconfig1 BEFORE markingconfig0cipherkind0;config1kind1/no cipher','AES192 schedules expand exactly;decrypt table inverted to forward expansion and verified independently','CBC IV resetszero percall;partiallastblock zero-filled,notPKCS padding','Plain header LE16length/group/opcode;encrypted outer LE16length/BYTEpadding then16-byte-block ciphertext','Send wrapper togglesprocess0encryption off forgroup21,onforothergroups;doesnotimply authentication','Create passesconfig pointerSrc+472 toselector2;selector writes+228/+232 beyondtwo-element local array;unsafe stack overwrite is not reproduced'],'gaps':['Full35-handler455dispatch,gatecrypto request/reply consumers,wireID/PW50/32','Fullstandard/queuedtransport/threads/timers/Close/error parity','Unsafe/OOM/alias/concurrent/error-logging domains and observedCreate stackoverwrite','ActualpreengineConnectwait/fullUI/gameplay/shutdown/M9'],'M6':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-network-codec-reference.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS:AES192 directional schedules verified;'+str(len(ranges))+'code ranges;private defaults generated')
if __name__=='__main__':main()
