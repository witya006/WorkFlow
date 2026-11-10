"""Pin condition calculations andgenerate small independent item-data oracles."""
import hashlib,json,math,struct
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_equipment import record,sha
from audit_client455_language import decode,encode_with_envelope
from audit_client455_item_payloads import item_tables
from build_client455_x87_math import read_va
from client455_reference_regions import verify_regions

def f32(value):return struct.unpack('<f',struct.pack('<f',value))[0]
def get(data,at,fmt='I'):return struct.unpack_from('<'+fmt,data,at)[0]
def put(data,at,value,fmt='I'):struct.pack_into('<'+fmt,data,at,value)
def word(value):return int(value)&0xffffffff if math.isfinite(value) and -2**63<=value<2**63 else 0
def signed(value):value&=0xffffffff;return value if value<2**31 else value-2**32

def modifier_oracle(row,actor=15):
    block=bytearray(200);mark=0;calls=[]
    for start in [60,88,116]:
        for i in range(7):put(block,start+4*i,1.0,'f')
    for at in [144,148,160]:put(block,at,1.0,'f')
    kind=row[88];accepted=1<=kind<=10 or kind in [27,46]
    if not accepted:return block,mark,calls,False
    effects=[(row[177+i],get(row,184+4*i,'f')) for i in range(4)] if kind==46 else [(row[185+i],get(row,192+4*i,'f')) for i in range(row[184])]
    scalar_float={2:160,7:144,12:152,15:72,21:144}
    scalar_int={20:20,25:56,26:12,33:48,34:28,35:40,36:44}
    vectors={3:[88+4*i for i in range(4,7)],4:[116+4*i for i in range(4,7)],6:[60+4*i for i in range(7)],24:[116+4*i for i in range(7)]}
    for code,value in effects:
        if value==0:continue
        if code in scalar_float:
            if code==12 and actor!=15:continue
            at=scalar_float[code];put(block,at,f32(get(block,at,'f')+value),'f')
        elif code in vectors:
            for at in vectors[code]:put(block,at,f32(get(block,at,'f')+value),'f')
        elif code in scalar_int:
            at=scalar_int[code];put(block,at,word(signed(get(block,at))+value))
        elif code==8:
            previous=block[164] if block[164]<128 else block[164]-256;block[164]=word(previous+value)&255;calls.append((previous&0xffffff00)|block[164])
        elif code==13:mark=(mark+1)&255
    return block,mark,calls,True

def totals_oracle(row,block,accepted):
    if not accepted:return [0]*6+[1.0,0]
    kind=row[88];attack=[0,0,0,0,0,0];hit=get(block,104,'f');weak=1
    if kind in [1,2,3,4,5,7,8]:
        factor=get(block,144,'f')
        if kind!=7:factor=f32(get(block,148,'f')-1.0+factor)
        weight={1:.23,2:.22,3:.18,4:.17,5:.20}.get(kind,1)
        defence=f32(get(row,216)*factor*f32(weight));attack[4]=word(f32(defence/2.0)) if defence>=0 else 0
        attack[5]=get(row,180)
        if kind<=5:weak=kind
    elif kind==6:
        category=get(row,216);mode=5 if category in [5,6,8,11] else 6 if category==7 else 4
        factor=max(0,get(block,60+4*mode,'f'));force=get(block,72,'f')
        attack[:2]=[word(get(row,at)*factor) for at in [232,236]]
        attack[2:4]=[word(get(row,at)*force) for at in [240,244]] if force>=0 else [0,0]
        hit=get(block,88+4*mode,'f')
    return attack+[hit,weak]

def fixture(template):
    tables=[[] for _ in range(47)]
    for kind in [0,1,2,3,4,5,6,7,8,9,10,27,46]:
        count=4 if kind==6 else 2 if kind in [1,9] else 1
        for index in range(count):
            row=bytearray(384);put(row,0,index);row[8:8+len(f'fixture{kind}_{index}')]=f'fixture{kind}_{index}'.encode();row[88]=kind;row[152]=1;row[160]=1;put(row,168,1000)
            if kind in [1,2,3,4,5,7,8]:
                rank=[1,2,3,4,5,7,8].index(kind)+1;put(row,216,rank*100);put(row,180,rank*10)
                if kind==1 and index==1:row[160]=0
            elif kind==6:
                put(row,216,[4,5,7,11][index])
                for at,value in zip([232,236,240,244],[100,201,50,81]):put(row,at,value)
                if index==0:row[184]=1;row[185]=6;put(row,192,.25,'f')
            elif kind==27:put(row,228,1.5,'f')
            elif kind==46:row[177]=7;put(row,184,.25,'f')
            elif kind==9 and index==1:row[184]=1;row[185]=8;put(row,192,0.0,'f')
            tables[kind].append(row)
    plain=b''.join(struct.pack('<II',len(rows),384)+b''.join(rows) for rows in tables)+bytes(376)
    n=get(template,29);envelope=template[:29]+struct.pack('<I',len(plain))+bytes(len(plain))+template[33+n:289+n]
    encoded=encode_with_envelope(envelope,plain);assert decode(encoded)==plain;return encoded

def main():
    raw=WS/'artifacts/client455-progress/equipment-conditions146-reference/session.json';proof=verify_regions(raw)
    prior_raw=WS/'artifacts/client455-progress/equipment-providers146-reference/session.json';prior=verify_regions(prior_raw)
    wanted={'0x411e0','0x412a0','0x41840','0x418d0','0x41970','0x41ac0','0x42460'}
    for reference in proof['references']:
        old=next(r for r in prior['references'] if r['sha256']==reference['sha256']);reused=[f for f in old['functions'] if f['rva'] in wanted];assert len(reused)==7
        reference['functions']+=reused
    proof['full_functions']+=7;proof['full_instructions']+=sum(f['instructions'] for f in reused);proof['positive_cfg_blocks']+=sum(f['positive_cfg_blocks'] for f in reused)
    assert proof['references'][0]['functions']==proof['references'][1]['functions']
    regions=[]
    for reference in proof['references']:
        binary=(WS/reference['file']).read_bytes();rows=[]
        for va,size in [(0x4417d0,76),(0x44181c,35),(0x442424,19),(0xaaa438,20),(0xaa92a8,4),(0xaa8ed8,4)]:
            data=read_va(binary,va,size);rows.append(dict(rva=hex(va-0x400000),bytes=size,sha256=hashlib.sha256(data).hexdigest(),data=data.hex()))
        assert get(read_va(binary,0xaa92a8,4),0)==0x404ea0 and get(read_va(binary,0xaa8ed8,4),0)==0x43e600
        assert struct.unpack('<5f',read_va(binary,0xaaa438,20))==tuple(f32(v) for v in [.23,.22,.18,.17,.20])
        regions.append(rows)
    assert regions[0]==regions[1]
    client=Path(json.loads((WS/'config/paths.json').read_text())['client_455']);input_file=client/'DataTable/Item.edf';original=input_file.read_bytes();tables,_,_=item_tables(decode(original))
    selected=[];encoded=b'EC46';cases=[]
    for kind in [0,1,2,3,4,5,6,7,8,9,10,27,46]:
        table=tables[kind];indices={0}
        for index in range(table['count']):
            row=table['data'][index*table['stride']:(index+1)*table['stride']]
            if len(row)<=200:continue
            if kind==46:nonzero=any(get(row,184+4*i,'f')!=0 for i in range(4))
            else:nonzero=0<row[184]<=6 and all(192+4*i+4<=len(row) for i in range(row[184])) and any(get(row,192+4*i,'f')!=0 for i in range(row[184]))
            if nonzero:indices.add(index);break
        for index in sorted(indices):
            row=table['data'][index*table['stride']:];block,mark,calls,accepted=modifier_oracle(row)
            totals=totals_oracle(row,block,accepted);cases.append(struct.pack('<III',kind,index,accepted)+block+bytes([mark])+struct.pack('<I',len(calls))+b''.join(struct.pack('<I',v) for v in calls)+struct.pack('<6IfB',*totals))
            selected.append(dict(type=kind,index=index,metadata_kind=row[88],accepted=accepted,mark=mark,skill_callbacks=calls,total=totals))
    root=WS/'artifacts/client455-equipment-conditions';root.mkdir(exist_ok=True);expected=root/'expected.bin';expected.write_bytes(encoded+struct.pack('<I',len(cases))+b''.join(cases));synthetic=root/'fixture.edf';synthetic.write_bytes(fixture(original))
    report=dict(status='PARTIAL_COMPONENT_STATIC',scope='Typed455equipment special/upgrade/combined stats/weak part source;ordinary actors/UI/network producers still open',**proof,
        raw=record(raw),reused_raw=record(prior_raw),reused_functions=7,data_regions=regions[0],script=record(Path(__file__)),decoder_script=record(WS/'scripts/decode_client455_cfg.py'),regions_script=record(WS/'scripts/client455_reference_regions.py'),
        sources=[record(WS/'scripts/native'/name) for name in ['client455_equipment_conditions.h','client455_equipment_conditions_probe.cpp','client455_normal_item_copy.h']],
        inputs=[dict(original=str(input_file),relative='DataTable/Item.edf',sha256=sha(input_file),bytes=len(original))],expected=record(expected),synthetic=record(synthetic),real_cases=selected,
        armour_set_predicate='CNormalItem virtual68 ->404EA0 reads record byte113,not metadata upgradable160',
        normal_item_source='44C670 embedded base player processor evenwhen current resource processor differs',
        current_runtime_unchanged=True,production_actor_connected=False,full_failure_fidelity=False,input_exe_executed=False,server_modified=False,M6='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-conditions-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(functions=proof['full_functions'],instructions=proof['full_instructions'],blocks=proof['positive_cfg_blocks'],real_cases=len(cases),fixture_bytes=synthetic.stat().st_size)))
if __name__=='__main__':main()
