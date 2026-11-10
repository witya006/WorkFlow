"""Locate pinned MSVC RTTI/vtables as data;not a behavior or port claim."""
import argparse,hashlib,json,re,struct
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--class-name',action='append');parser.add_argument('--output',default='inventory/client455-hud-discovery.json');args=parser.parse_args()
    names=args.class_name or ['CGP_MainGame','CGUIGaugeExpWindow','CGUIWindow','CEquipBoard']
    assert all(re.fullmatch('[A-Za-z_][A-Za-z_0-9]{0,95}',name) for name in names)
    output=(WS/args.output).resolve();assert output.is_relative_to((WS/'inventory').resolve()) and output.suffix=='.json'
    data=(WS/'work/client-reference/current/RF_Online.bin').read_bytes();image=pe(data)
    pin=json.loads((WS/'config/client-target.json').read_text())['behavior_reference']['sha256']
    assert hashlib.sha256(data).hexdigest()==pin
    text=next(s for s in image['sections'] if s['name']=='.text');rdata=next(s for s in image['sections'] if s['name']=='.rdata');base=image['image_base']
    raw=data[rdata['raw_offset']:rdata['raw_offset']+rdata['raw_size']]
    def address(offset):return base+rdata['rva']+offset
    def matches(value):
        start=0;wanted=struct.pack('<I',value)
        while True:
            at=raw.find(wanted,start)
            if at<0:return
            if at%4==0:yield at
            start=at+1
    def in_code(value):return base+text['rva']<=value<base+text['rva']+text['raw_size']
    classes=[]
    for name in names:
        name_offset=data.find(('.?AV'+name+'@@').encode()+b'\0');assert name_offset>=8,name
        section=next(s for s in image['sections'] if s['raw_offset']<=name_offset<s['raw_offset']+s['raw_size'])
        td=base+section['rva']+name_offset-section['raw_offset']-8;tables=[]
        for ref in matches(td):
            if ref<12:continue
            col=ref-12;signature,offset,ctor,_,hierarchy=struct.unpack_from('<5I',raw,col)
            if signature or ctor or offset>1000000:continue
            for table_ref in matches(address(col)):
                table=table_ref+4;functions=[]
                while table+4*len(functions)+4<=len(raw):
                    value=struct.unpack_from('<I',raw,table+4*len(functions))[0]
                    if not in_code(value):break
                    functions.append(hex(value))
                if len(functions)>=4:tables.append(dict(col_rva=hex(address(col)-base),object_offset=offset,vtable_rva=hex(address(table)-base),functions=functions))
        assert tables,name;classes.append(dict(name=name,type_descriptor_rva=hex(td-base),vtables=tables))
    report=dict(status='POINTER_DISCOVERY_NOT_BEHAVIOR',reference=dict(sha256=pin,architecture='x86',image_base=hex(base)),classes=classes,input_exe_executed=False,server_modified=False)
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],classes=[dict(name=row['name'],vtables=[t for t in row['vtables'] if not t['object_offset']]) for row in classes])))


if __name__=='__main__':main()
